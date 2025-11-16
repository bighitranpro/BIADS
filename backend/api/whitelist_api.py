"""
Whitelist Account Management API

Manages whitelist accounts that are protected from certain automated actions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import io

from core.database import get_db, WhitelistAccount, Account
from services.activity_logger import ActivityLogger
from services.file_parser import parse_uid_list

router = APIRouter(prefix="/api/whitelist", tags=["Whitelist"])

# Pydantic Models
class WhitelistCreate(BaseModel):
    uid: str = Field(..., description="Facebook UID")
    name: Optional[str] = Field(None, description="Name")
    username: Optional[str] = Field(None, description="Username")
    reason: Optional[str] = Field(None, description="Reason for whitelisting")
    
    @validator('uid')
    def validate_uid(cls, v):
        if not v or not v.strip():
            raise ValueError('UID cannot be empty')
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Invalid Facebook UID format')
        return v.strip()

class WhitelistUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    reason: Optional[str] = None
    is_active: Optional[bool] = None

class WhitelistResponse(BaseModel):
    id: int
    uid: str
    name: Optional[str]
    username: Optional[str]
    reason: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WhitelistStats(BaseModel):
    total_whitelisted: int
    active_count: int
    inactive_count: int
    recent_additions: int

# API Endpoints

@router.get("/", response_model=List[WhitelistResponse])
async def get_whitelist(
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get whitelist accounts"""
    try:
        query = select(WhitelistAccount)
        
        filters = []
        if is_active is not None:
            filters.append(WhitelistAccount.is_active == is_active)
        if search:
            filters.append(
                or_(
                    WhitelistAccount.uid.ilike(f'%{search}%'),
                    WhitelistAccount.name.ilike(f'%{search}%'),
                    WhitelistAccount.username.ilike(f'%{search}%')
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(WhitelistAccount.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=WhitelistStats)
async def get_whitelist_stats(db: AsyncSession = Depends(get_db)):
    """Get whitelist statistics"""
    try:
        total_result = await db.execute(select(func.count(WhitelistAccount.id)))
        total = total_result.scalar() or 0
        
        active_result = await db.execute(
            select(func.count(WhitelistAccount.id)).where(WhitelistAccount.is_active == True)
        )
        active = active_result.scalar() or 0
        
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_result = await db.execute(
            select(func.count(WhitelistAccount.id)).where(WhitelistAccount.created_at >= week_ago)
        )
        recent = recent_result.scalar() or 0
        
        return WhitelistStats(
            total_whitelisted=total,
            active_count=active,
            inactive_count=total - active,
            recent_additions=recent
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
async def add_to_whitelist(
    data: WhitelistCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add account to whitelist"""
    try:
        # Check if already exists
        result = await db.execute(
            select(WhitelistAccount).where(WhitelistAccount.uid == data.uid)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            if existing.is_active:
                raise HTTPException(status_code=400, detail="UID already in whitelist")
            else:
                # Reactivate
                existing.is_active = True
                existing.updated_at = datetime.utcnow()
                await db.commit()
                return {'success': True, 'message': 'Whitelist entry reactivated'}
        
        # Create new
        whitelist = WhitelistAccount(
            uid=data.uid,
            name=data.name,
            username=data.username,
            reason=data.reason,
            is_active=True
        )
        
        db.add(whitelist)
        await db.commit()
        await db.refresh(whitelist)
        
        await ActivityLogger.log(
            db=db,
            activity_type='whitelist_added',
            description=f'Added {data.uid} to whitelist',
            metadata={'uid': data.uid, 'reason': data.reason}
        )
        
        return {
            'success': True,
            'message': 'Added to whitelist successfully',
            'data': {'id': whitelist.id, 'uid': whitelist.uid}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import", response_model=dict)
async def import_whitelist(
    file: UploadFile = File(...),
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Import whitelist from file"""
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        
        uids = parse_uid_list(text_content)
        
        if not uids:
            raise HTTPException(status_code=400, detail="No valid UIDs found in file")
        
        added_count = 0
        skipped_count = 0
        
        for uid in uids:
            # Check if exists
            result = await db.execute(
                select(WhitelistAccount).where(WhitelistAccount.uid == uid)
            )
            existing = result.scalar_one_or_none()
            
            if existing and existing.is_active:
                skipped_count += 1
                continue
            
            if existing:
                existing.is_active = True
                existing.updated_at = datetime.utcnow()
            else:
                whitelist = WhitelistAccount(
                    uid=uid,
                    reason=reason,
                    is_active=True
                )
                db.add(whitelist)
            
            added_count += 1
        
        await db.commit()
        
        await ActivityLogger.log(
            db=db,
            activity_type='whitelist_imported',
            description=f'Imported {added_count} accounts to whitelist',
            metadata={'added': added_count, 'skipped': skipped_count}
        )
        
        return {
            'success': True,
            'message': f'Import completed: {added_count} added, {skipped_count} skipped',
            'data': {'added': added_count, 'skipped': skipped_count}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{whitelist_id}", response_model=dict)
async def update_whitelist(
    whitelist_id: int,
    data: WhitelistUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update whitelist entry"""
    try:
        result = await db.execute(
            select(WhitelistAccount).where(WhitelistAccount.id == whitelist_id)
        )
        whitelist = result.scalar_one_or_none()
        
        if not whitelist:
            raise HTTPException(status_code=404, detail="Whitelist entry not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(whitelist, field, value)
        
        whitelist.updated_at = datetime.utcnow()
        await db.commit()
        
        return {'success': True, 'message': 'Whitelist updated successfully'}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{whitelist_id}", response_model=dict)
async def remove_from_whitelist(
    whitelist_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove account from whitelist"""
    try:
        result = await db.execute(
            select(WhitelistAccount).where(WhitelistAccount.id == whitelist_id)
        )
        whitelist = result.scalar_one_or_none()
        
        if not whitelist:
            raise HTTPException(status_code=404, detail="Whitelist entry not found")
        
        uid = whitelist.uid
        await db.delete(whitelist)
        await db.commit()
        
        await ActivityLogger.log(
            db=db,
            activity_type='whitelist_removed',
            description=f'Removed {uid} from whitelist',
            metadata={'uid': uid}
        )
        
        return {'success': True, 'message': 'Removed from whitelist successfully'}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/{uid}", response_model=dict)
async def check_whitelist(
    uid: str,
    db: AsyncSession = Depends(get_db)
):
    """Check if UID is whitelisted"""
    try:
        result = await db.execute(
            select(WhitelistAccount).where(
                and_(
                    WhitelistAccount.uid == uid,
                    WhitelistAccount.is_active == True
                )
            )
        )
        whitelist = result.scalar_one_or_none()
        
        return {
            'whitelisted': whitelist is not None,
            'uid': uid,
            'reason': whitelist.reason if whitelist else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
