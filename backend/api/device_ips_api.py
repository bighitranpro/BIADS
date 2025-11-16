"""
Device IP Management API

Handles device IP tracking, management, and account-IP associations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from typing import List, Optional
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel, Field, validator

from core.database import get_db, Account, IPAddress as DeviceIP
from services.activity_logger import ActivityLogger

router = APIRouter(prefix="/api/device-ips", tags=["Device IPs"])

# Pydantic Models
class DeviceIPCreate(BaseModel):
    ip_address: str = Field(..., description="IP address")
    location: Optional[str] = Field(None, description="Location/Country")
    isp: Optional[str] = Field(None, description="Internet Service Provider")
    account_id: Optional[int] = Field(None, description="Associated account ID")
    is_trusted: bool = Field(True, description="Whether this IP is trusted")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator('ip_address')
    def validate_ip(cls, v):
        # Basic IP validation
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('Invalid IP address format')
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                raise ValueError('Invalid IP address format')
        return v

class DeviceIPUpdate(BaseModel):
    location: Optional[str] = None
    isp: Optional[str] = None
    account_id: Optional[int] = None
    is_trusted: Optional[bool] = None
    is_blocked: Optional[bool] = None
    notes: Optional[str] = None

class DeviceIPResponse(BaseModel):
    id: int
    ip_address: str
    location: Optional[str]
    isp: Optional[str]
    account_id: Optional[int]
    account_info: Optional[dict] = None
    is_trusted: bool
    is_blocked: bool
    last_used_at: Optional[datetime]
    access_count: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeviceIPStats(BaseModel):
    total_ips: int
    trusted_ips: int
    blocked_ips: int
    active_ips_24h: int
    total_accesses: int
    ips_by_location: dict

class DetectIPResponse(BaseModel):
    ip_address: str
    location: Optional[str]
    isp: Optional[str]
    already_exists: bool
    device_ip_id: Optional[int] = None

# Helper Functions
async def detect_current_ip() -> dict:
    """Detect current public IP and get location info"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Use ipapi.co for IP detection
            response = await client.get('https://ipapi.co/json/')
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip_address': data.get('ip'),
                    'location': f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}",
                    'isp': data.get('org', 'Unknown')
                }
    except Exception as e:
        print(f"Error detecting IP: {e}")
    
    # Fallback to simple IP detection
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get('https://api.ipify.org?format=json')
            if response.status_code == 200:
                return {
                    'ip_address': response.json().get('ip'),
                    'location': None,
                    'isp': None
                }
    except:
        pass
    
    return {'ip_address': None, 'location': None, 'isp': None}

# API Endpoints

@router.get("/", response_model=List[DeviceIPResponse])
async def get_device_ips(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    is_trusted: Optional[bool] = Query(None, description="Filter by trusted status"),
    is_blocked: Optional[bool] = Query(None, description="Filter by blocked status"),
    search: Optional[str] = Query(None, description="Search in IP or location"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get list of device IPs with filters"""
    try:
        query = select(DeviceIP)
        
        # Apply filters
        filters = []
        if account_id is not None:
            filters.append(DeviceIP.account_id == account_id)
        if is_trusted is not None:
            filters.append(DeviceIP.is_trusted == is_trusted)
        if is_blocked is not None:
            filters.append(DeviceIP.is_blocked == is_blocked)
        if search:
            filters.append(
                or_(
                    DeviceIP.ip_address.ilike(f'%{search}%'),
                    DeviceIP.location.ilike(f'%{search}%'),
                    DeviceIP.isp.ilike(f'%{search}%')
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Order by last used
        query = query.order_by(DeviceIP.last_used_at.desc().nullslast())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        ips = result.scalars().all()
        
        # Enrich with account info
        response_data = []
        for ip in ips:
            ip_dict = {
                'id': ip.id,
                'ip_address': ip.ip_address,
                'location': ip.location,
                'isp': ip.isp,
                'account_id': ip.account_id,
                'account_info': None,
                'is_trusted': ip.is_trusted,
                'is_blocked': ip.is_blocked,
                'last_used_at': ip.last_used_at,
                'access_count': ip.access_count,
                'notes': ip.notes,
                'created_at': ip.created_at,
                'updated_at': ip.updated_at
            }
            
            # Get account info if associated
            if ip.account_id:
                acc_result = await db.execute(
                    select(Account).where(Account.id == ip.account_id)
                )
                account = acc_result.scalar_one_or_none()
                if account:
                    ip_dict['account_info'] = {
                        'id': account.id,
                        'uid': account.uid,
                        'name': account.name
                    }
            
            response_data.append(DeviceIPResponse(**ip_dict))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=DeviceIPStats)
async def get_device_ip_stats(db: AsyncSession = Depends(get_db)):
    """Get device IP statistics"""
    try:
        # Total IPs
        total_result = await db.execute(select(func.count(DeviceIP.id)))
        total_ips = total_result.scalar() or 0
        
        # Trusted IPs
        trusted_result = await db.execute(
            select(func.count(DeviceIP.id)).where(DeviceIP.is_trusted == True)
        )
        trusted_ips = trusted_result.scalar() or 0
        
        # Blocked IPs
        blocked_result = await db.execute(
            select(func.count(DeviceIP.id)).where(DeviceIP.is_blocked == True)
        )
        blocked_ips = blocked_result.scalar() or 0
        
        # Active in last 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        active_result = await db.execute(
            select(func.count(DeviceIP.id)).where(DeviceIP.last_used_at >= yesterday)
        )
        active_ips_24h = active_result.scalar() or 0
        
        # Total accesses
        accesses_result = await db.execute(
            select(func.sum(DeviceIP.access_count))
        )
        total_accesses = accesses_result.scalar() or 0
        
        # IPs by location
        location_result = await db.execute(
            select(DeviceIP.location, func.count(DeviceIP.id))
            .where(DeviceIP.location.isnot(None))
            .group_by(DeviceIP.location)
        )
        ips_by_location = {loc: count for loc, count in location_result.all()}
        
        return DeviceIPStats(
            total_ips=total_ips,
            trusted_ips=trusted_ips,
            blocked_ips=blocked_ips,
            active_ips_24h=active_ips_24h,
            total_accesses=int(total_accesses),
            ips_by_location=ips_by_location
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detect", response_model=DetectIPResponse)
async def detect_ip(db: AsyncSession = Depends(get_db)):
    """Detect current public IP address"""
    try:
        ip_info = await detect_current_ip()
        
        if not ip_info['ip_address']:
            raise HTTPException(status_code=500, detail="Could not detect IP address")
        
        # Check if IP already exists
        result = await db.execute(
            select(DeviceIP).where(DeviceIP.ip_address == ip_info['ip_address'])
        )
        existing_ip = result.scalar_one_or_none()
        
        return DetectIPResponse(
            ip_address=ip_info['ip_address'],
            location=ip_info['location'],
            isp=ip_info['isp'],
            already_exists=existing_ip is not None,
            device_ip_id=existing_ip.id if existing_ip else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
async def create_device_ip(
    ip_data: DeviceIPCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a new device IP"""
    try:
        # Check if IP already exists
        result = await db.execute(
            select(DeviceIP).where(DeviceIP.ip_address == ip_data.ip_address)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="IP address already exists")
        
        # Validate account if provided
        if ip_data.account_id:
            acc_result = await db.execute(
                select(Account).where(Account.id == ip_data.account_id)
            )
            if not acc_result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Account not found")
        
        # Create new IP
        new_ip = DeviceIP(
            ip_address=ip_data.ip_address,
            location=ip_data.location,
            isp=ip_data.isp,
            account_id=ip_data.account_id,
            is_trusted=ip_data.is_trusted,
            notes=ip_data.notes,
            access_count=0
        )
        
        db.add(new_ip)
        await db.commit()
        await db.refresh(new_ip)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            activity_type='device_ip_added',
            description=f'Added device IP: {ip_data.ip_address}',
            account_id=ip_data.account_id,
            metadata={'ip_id': new_ip.id, 'ip_address': ip_data.ip_address}
        )
        
        return {
            'success': True,
            'message': 'Device IP added successfully',
            'data': {'id': new_ip.id, 'ip_address': new_ip.ip_address}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{ip_id}", response_model=dict)
async def update_device_ip(
    ip_id: int,
    ip_data: DeviceIPUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update device IP information"""
    try:
        result = await db.execute(select(DeviceIP).where(DeviceIP.id == ip_id))
        device_ip = result.scalar_one_or_none()
        
        if not device_ip:
            raise HTTPException(status_code=404, detail="Device IP not found")
        
        # Validate account if provided
        if ip_data.account_id is not None:
            acc_result = await db.execute(
                select(Account).where(Account.id == ip_data.account_id)
            )
            if not acc_result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Account not found")
        
        # Update fields
        update_data = ip_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device_ip, field, value)
        
        device_ip.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            activity_type='device_ip_updated',
            description=f'Updated device IP: {device_ip.ip_address}',
            account_id=device_ip.account_id,
            metadata={'ip_id': ip_id}
        )
        
        return {
            'success': True,
            'message': 'Device IP updated successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{ip_id}", response_model=dict)
async def delete_device_ip(
    ip_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a device IP"""
    try:
        result = await db.execute(select(DeviceIP).where(DeviceIP.id == ip_id))
        device_ip = result.scalar_one_or_none()
        
        if not device_ip:
            raise HTTPException(status_code=404, detail="Device IP not found")
        
        ip_address = device_ip.ip_address
        account_id = device_ip.account_id
        
        await db.delete(device_ip)
        await db.commit()
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            activity_type='device_ip_deleted',
            description=f'Deleted device IP: {ip_address}',
            account_id=account_id,
            metadata={'ip_address': ip_address}
        )
        
        return {
            'success': True,
            'message': 'Device IP deleted successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
