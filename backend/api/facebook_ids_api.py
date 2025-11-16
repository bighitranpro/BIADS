"""
Facebook IDs API
REST endpoints for managing Facebook ID/UID collection
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from core.database import get_db, FacebookID, Account
from services.activity_logger import ActivityLogger
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import re

router = APIRouter(prefix="/api/facebook-ids", tags=["Facebook IDs"])


# Pydantic Schemas
class FacebookIDCreate(BaseModel):
    """Schema để tạo Facebook ID mới"""
    uid: str = Field(..., min_length=1, max_length=50, description="Facebook UID")
    name: Optional[str] = Field(None, max_length=255, description="Tên hiển thị")
    username: Optional[str] = Field(None, max_length=255, description="Username")
    profile_url: Optional[str] = Field(None, max_length=500, description="Profile URL")
    status: str = Field("valid", description="Trạng thái: valid, invalid, used")
    is_friend: bool = Field(False, description="Đã kết bạn chưa")
    source: str = Field("manual", description="Nguồn: manual, import, scan_group, scan_post")
    source_id: Optional[str] = Field(None, description="ID nguồn (Group ID/Post ID)")
    collected_by_account_id: Optional[int] = Field(None, description="Tài khoản thu thập")
    notes: Optional[str] = Field(None, description="Ghi chú")


class FacebookIDUpdate(BaseModel):
    """Schema để update Facebook ID"""
    name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    profile_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    is_friend: Optional[bool] = None
    notes: Optional[str] = None


class FacebookIDResponse(BaseModel):
    """Schema response cho Facebook ID"""
    id: int
    uid: str
    name: Optional[str]
    username: Optional[str]
    profile_url: Optional[str]
    status: str
    is_friend: bool
    source: str
    source_id: Optional[str]
    collected_by_account_id: Optional[int]
    notes: Optional[str]
    created_at: str
    updated_at: str
    collected_by_info: Optional[Dict[str, Any]]


class FacebookIDStats(BaseModel):
    """Schema cho thống kê Facebook IDs"""
    total_count: int
    valid_count: int
    invalid_count: int
    used_count: int
    friend_count: int
    not_friend_count: int
    sources: Dict[str, int]


class FacebookIDScanGroup(BaseModel):
    """Schema cho scan group request"""
    account_id: int = Field(..., description="Tài khoản dùng để scan")
    group_url: str = Field(..., description="URL nhóm Facebook")
    max_ids: int = Field(100, ge=1, le=1000, description="Số lượng ID tối đa")
    scan_type: str = Field("members", description="Loại scan: members, posts, comments")


class FacebookIDValidate(BaseModel):
    """Schema cho validate request"""
    uids: List[str] = Field(..., description="Danh sách UID cần validate")
    account_id: Optional[int] = Field(None, description="Tài khoản dùng để validate")


# Helper Functions
def validate_facebook_uid(uid: str) -> bool:
    """Validate Facebook UID format"""
    # Facebook UID is typically 15 digits
    return bool(re.match(r'^\d{10,20}$', uid))


def extract_uid_from_url(url: str) -> Optional[str]:
    """Extract UID from Facebook URL"""
    # Pattern 1: facebook.com/profile.php?id=100012345678
    match = re.search(r'id=(\d+)', url)
    if match:
        return match.group(1)
    
    # Pattern 2: facebook.com/100012345678
    match = re.search(r'facebook\.com/(\d{10,20})', url)
    if match:
        return match.group(1)
    
    return None


# API Endpoints

@router.get("/", response_model=List[FacebookIDResponse])
async def get_facebook_ids(
    status: Optional[str] = Query(None, description="Filter by status"),
    is_friend: Optional[bool] = Query(None, description="Filter by friend status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    search: Optional[str] = Query(None, description="Search in UID, name, username"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách Facebook IDs với filters và search
    
    Query params:
    - status: Filter theo trạng thái (valid, invalid, used)
    - is_friend: Filter theo trạng thái bạn bè
    - source: Filter theo nguồn (manual, import, scan_group, scan_post)
    - search: Tìm kiếm trong UID, name, username
    - limit: Số lượng tối đa (default 100, max 1000)
    - offset: Bỏ qua bao nhiêu records (pagination)
    """
    try:
        # Build query với filters
        query = select(FacebookID)
        
        conditions = []
        if status:
            conditions.append(FacebookID.status == status)
        if is_friend is not None:
            conditions.append(FacebookID.is_friend == is_friend)
        if source:
            conditions.append(FacebookID.source == source)
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    FacebookID.uid.like(search_pattern),
                    FacebookID.name.like(search_pattern),
                    FacebookID.username.like(search_pattern)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(offset).limit(limit).order_by(FacebookID.created_at.desc())
        
        result = await db.execute(query)
        facebook_ids = result.scalars().all()
        
        # Format response với collected_by info
        response_data = []
        for fb_id in facebook_ids:
            # Get collected_by account info if exists
            collected_by_info = None
            if fb_id.collected_by_account_id:
                acc_query = select(Account).where(Account.id == fb_id.collected_by_account_id)
                acc_result = await db.execute(acc_query)
                acc = acc_result.scalar_one_or_none()
                
                if acc:
                    collected_by_info = {
                        "id": acc.id,
                        "uid": acc.uid,
                        "name": acc.name,
                        "username": acc.username
                    }
            
            response_data.append({
                "id": fb_id.id,
                "uid": fb_id.uid,
                "name": fb_id.name,
                "username": fb_id.username,
                "profile_url": fb_id.profile_url,
                "status": fb_id.status,
                "is_friend": fb_id.is_friend,
                "source": fb_id.source,
                "source_id": fb_id.source_id,
                "collected_by_account_id": fb_id.collected_by_account_id,
                "notes": fb_id.notes,
                "created_at": fb_id.created_at.isoformat(),
                "updated_at": fb_id.updated_at.isoformat(),
                "collected_by_info": collected_by_info
            })
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Facebook IDs: {str(e)}")


@router.get("/stats", response_model=FacebookIDStats)
async def get_facebook_ids_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thống kê Facebook IDs
    """
    try:
        # Total count
        total_query = select(func.count()).select_from(FacebookID)
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        # Valid count
        valid_query = select(func.count()).select_from(FacebookID).where(FacebookID.status == 'valid')
        valid_result = await db.execute(valid_query)
        valid_count = valid_result.scalar() or 0
        
        # Invalid count
        invalid_query = select(func.count()).select_from(FacebookID).where(FacebookID.status == 'invalid')
        invalid_result = await db.execute(invalid_query)
        invalid_count = invalid_result.scalar() or 0
        
        # Used count
        used_query = select(func.count()).select_from(FacebookID).where(FacebookID.status == 'used')
        used_result = await db.execute(used_query)
        used_count = used_result.scalar() or 0
        
        # Friend count
        friend_query = select(func.count()).select_from(FacebookID).where(FacebookID.is_friend == True)
        friend_result = await db.execute(friend_query)
        friend_count = friend_result.scalar() or 0
        
        # Not friend count
        not_friend_query = select(func.count()).select_from(FacebookID).where(FacebookID.is_friend == False)
        not_friend_result = await db.execute(not_friend_query)
        not_friend_count = not_friend_result.scalar() or 0
        
        # Sources breakdown
        sources_query = select(FacebookID.source, func.count()).group_by(FacebookID.source)
        sources_result = await db.execute(sources_query)
        sources = dict(sources_result.all())
        
        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "used_count": used_count,
            "friend_count": friend_count,
            "not_friend_count": not_friend_count,
            "sources": sources
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/{facebook_id}", response_model=FacebookIDResponse)
async def get_facebook_id(
    facebook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Lấy thông tin chi tiết một Facebook ID"""
    try:
        query = select(FacebookID).where(FacebookID.id == facebook_id)
        result = await db.execute(query)
        fb_id = result.scalar_one_or_none()
        
        if not fb_id:
            raise HTTPException(status_code=404, detail="Facebook ID not found")
        
        # Get collected_by info
        collected_by_info = None
        if fb_id.collected_by_account_id:
            acc_query = select(Account).where(Account.id == fb_id.collected_by_account_id)
            acc_result = await db.execute(acc_query)
            acc = acc_result.scalar_one_or_none()
            
            if acc:
                collected_by_info = {
                    "id": acc.id,
                    "uid": acc.uid,
                    "name": acc.name,
                    "username": acc.username
                }
        
        return {
            "id": fb_id.id,
            "uid": fb_id.uid,
            "name": fb_id.name,
            "username": fb_id.username,
            "profile_url": fb_id.profile_url,
            "status": fb_id.status,
            "is_friend": fb_id.is_friend,
            "source": fb_id.source,
            "source_id": fb_id.source_id,
            "collected_by_account_id": fb_id.collected_by_account_id,
            "notes": fb_id.notes,
            "created_at": fb_id.created_at.isoformat(),
            "updated_at": fb_id.updated_at.isoformat(),
            "collected_by_info": collected_by_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Facebook ID: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_facebook_id(
    facebook_id: FacebookIDCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo Facebook ID mới
    
    Body:
    - uid: Facebook UID (required)
    - name: Tên hiển thị (optional)
    - username: Username (optional)
    - profile_url: Profile URL (optional)
    - status: Trạng thái (default: valid)
    - is_friend: Đã kết bạn (default: false)
    - source: Nguồn (default: manual)
    - source_id: ID nguồn (optional)
    - collected_by_account_id: Tài khoản thu thập (optional)
    - notes: Ghi chú (optional)
    """
    try:
        # Validate UID format
        if not validate_facebook_uid(facebook_id.uid):
            raise HTTPException(status_code=400, detail="Invalid Facebook UID format")
        
        # Check if UID already exists
        existing_query = select(FacebookID).where(FacebookID.uid == facebook_id.uid)
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Facebook ID already exists")
        
        # Validate collected_by_account_id if provided
        if facebook_id.collected_by_account_id:
            acc_query = select(Account).where(Account.id == facebook_id.collected_by_account_id)
            acc_result = await db.execute(acc_query)
            acc = acc_result.scalar_one_or_none()
            
            if not acc:
                raise HTTPException(status_code=404, detail="Collected by account not found")
        
        # Create new Facebook ID
        new_fb_id = FacebookID(
            uid=facebook_id.uid,
            name=facebook_id.name,
            username=facebook_id.username,
            profile_url=facebook_id.profile_url,
            status=facebook_id.status,
            is_friend=facebook_id.is_friend,
            source=facebook_id.source,
            source_id=facebook_id.source_id,
            collected_by_account_id=facebook_id.collected_by_account_id,
            notes=facebook_id.notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_fb_id)
        await db.commit()
        await db.refresh(new_fb_id)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="facebook_id_create",
            message=f"Đã thêm Facebook ID {facebook_id.uid}",
            level="success",
            account_id=facebook_id.collected_by_account_id,
            extra_data={
                "facebook_id": new_fb_id.id,
                "uid": facebook_id.uid,
                "source": facebook_id.source
            }
        )
        
        return {
            "success": True,
            "message": "Facebook ID created successfully",
            "facebook_id": new_fb_id.id,
            "uid": new_fb_id.uid
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating Facebook ID: {str(e)}")


@router.put("/{facebook_id}", response_model=Dict[str, Any])
async def update_facebook_id(
    facebook_id: int,
    update_data: FacebookIDUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật thông tin Facebook ID
    
    Body (tất cả optional):
    - name: Tên hiển thị
    - username: Username
    - profile_url: Profile URL
    - status: Trạng thái
    - is_friend: Đã kết bạn
    - notes: Ghi chú
    """
    try:
        # Get existing Facebook ID
        query = select(FacebookID).where(FacebookID.id == facebook_id)
        result = await db.execute(query)
        fb_id = result.scalar_one_or_none()
        
        if not fb_id:
            raise HTTPException(status_code=404, detail="Facebook ID not found")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(fb_id, field, value)
        
        fb_id.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(fb_id)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="facebook_id_update",
            message=f"Đã cập nhật Facebook ID {fb_id.uid}",
            level="info",
            extra_data={
                "facebook_id": fb_id.id,
                "updated_fields": list(update_dict.keys())
            }
        )
        
        return {
            "success": True,
            "message": "Facebook ID updated successfully",
            "facebook_id": fb_id.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating Facebook ID: {str(e)}")


@router.delete("/{facebook_id}", response_model=Dict[str, Any])
async def delete_facebook_id(
    facebook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Xóa Facebook ID"""
    try:
        # Get Facebook ID
        query = select(FacebookID).where(FacebookID.id == facebook_id)
        result = await db.execute(query)
        fb_id = result.scalar_one_or_none()
        
        if not fb_id:
            raise HTTPException(status_code=404, detail="Facebook ID not found")
        
        uid = fb_id.uid
        
        # Delete Facebook ID
        await db.delete(fb_id)
        await db.commit()
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="facebook_id_delete",
            message=f"Đã xóa Facebook ID {uid}",
            level="warning",
            extra_data={
                "facebook_id": facebook_id,
                "uid": uid
            }
        )
        
        return {
            "success": True,
            "message": "Facebook ID deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting Facebook ID: {str(e)}")


@router.post("/bulk/import", response_model=Dict[str, Any])
async def import_facebook_ids(
    file: UploadFile = File(..., description="Text file with UIDs or URLs, one per line"),
    source: str = Query("import", description="Source tag for imported IDs"),
    collected_by_account_id: Optional[int] = Query(None, description="Collecting account ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Import Facebook IDs từ file text
    
    Format file (mỗi dòng một trong các dạng):
    - UID: 100012345678
    - URL: https://facebook.com/profile.php?id=100012345678
    - URL: https://facebook.com/100012345678
    - UID|name|username: 100012345678|Nguyen Van A|nguyenvana
    """
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            raise HTTPException(status_code=400, detail="File is empty")
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            try:
                # Check if line has pipe separator
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    uid = parts[0]
                    name = parts[1] if len(parts) > 1 else None
                    username = parts[2] if len(parts) > 2 else None
                else:
                    # Try to extract UID from URL or use as is
                    uid = extract_uid_from_url(line) or line
                    name = None
                    username = None
                
                # Validate UID
                if not validate_facebook_uid(uid):
                    errors.append(f"Line {line_num}: Invalid UID format '{uid}'")
                    skipped_count += 1
                    continue
                
                # Check if already exists
                existing_query = select(FacebookID).where(FacebookID.uid == uid)
                existing_result = await db.execute(existing_query)
                existing = existing_result.scalar_one_or_none()
                
                if existing:
                    errors.append(f"Line {line_num}: UID {uid} already exists")
                    skipped_count += 1
                    continue
                
                # Create Facebook ID
                new_fb_id = FacebookID(
                    uid=uid,
                    name=name,
                    username=username,
                    status='valid',
                    is_friend=False,
                    source=source,
                    collected_by_account_id=collected_by_account_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                db.add(new_fb_id)
                created_count += 1
                
            except Exception as e:
                errors.append(f"Line {line_num}: {str(e)}")
                skipped_count += 1
        
        # Commit all changes
        if created_count > 0:
            await db.commit()
            
            # Log activity
            await ActivityLogger.log(
                db=db,
                action="facebook_id_import",
                message=f"Đã import {created_count} Facebook IDs từ file",
                level="success",
                account_id=collected_by_account_id,
                extra_data={
                    "created_count": created_count,
                    "skipped_count": skipped_count,
                    "total_lines": len(lines),
                    "source": source
                }
            )
        
        return {
            "success": True,
            "message": f"Import completed: {created_count} created, {skipped_count} skipped",
            "created_count": created_count,
            "skipped_count": skipped_count,
            "total_lines": len(lines),
            "errors": errors[:10]  # Return max 10 errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error importing Facebook IDs: {str(e)}")


@router.post("/bulk/delete", response_model=Dict[str, Any])
async def bulk_delete_facebook_ids(
    ids: List[int] = Query(..., description="List of Facebook ID IDs to delete"),
    db: AsyncSession = Depends(get_db)
):
    """Xóa nhiều Facebook IDs"""
    try:
        deleted_count = 0
        
        for fb_id in ids:
            query = select(FacebookID).where(FacebookID.id == fb_id)
            result = await db.execute(query)
            fb = result.scalar_one_or_none()
            
            if fb:
                await db.delete(fb)
                deleted_count += 1
        
        await db.commit()
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="facebook_id_bulk_delete",
            message=f"Đã xóa {deleted_count} Facebook IDs",
            level="warning",
            extra_data={
                "deleted_count": deleted_count,
                "total_requested": len(ids)
            }
        )
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} Facebook IDs",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting Facebook IDs: {str(e)}")


@router.post("/validate", response_model=Dict[str, Any])
async def validate_facebook_ids(
    validate_data: FacebookIDValidate,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate Facebook IDs (check if they're valid/active)
    
    Note: Đây là endpoint khởi tạo validation task.
    Việc validate thực tế sẽ được xử lý bởi background task với Selenium.
    """
    try:
        # Validate UIDs format
        invalid_uids = []
        for uid in validate_data.uids:
            if not validate_facebook_uid(uid):
                invalid_uids.append(uid)
        
        if invalid_uids:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid UID format: {', '.join(invalid_uids[:5])}"
            )
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="facebook_id_validate_start",
            message=f"Bắt đầu validate {len(validate_data.uids)} Facebook IDs",
            level="info",
            account_id=validate_data.account_id,
            extra_data={
                "uid_count": len(validate_data.uids),
                "account_id": validate_data.account_id
            }
        )
        
        # TODO: Implement actual validation logic with Selenium
        # This would be done in a background task
        
        return {
            "success": True,
            "message": f"Validation task created for {len(validate_data.uids)} Facebook IDs",
            "uid_count": len(validate_data.uids),
            "note": "This is a task creation endpoint. Actual validation will be processed in background."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating validation task: {str(e)}")


@router.post("/scan-group", response_model=Dict[str, Any])
async def scan_group_for_ids(
    scan_data: FacebookIDScanGroup,
    db: AsyncSession = Depends(get_db)
):
    """
    Scan Facebook group để thu thập IDs
    
    Body:
    - account_id: Tài khoản dùng để scan
    - group_url: URL nhóm Facebook
    - max_ids: Số lượng ID tối đa cần thu thập (default: 100, max: 1000)
    - scan_type: Loại scan - members (thành viên), posts (người đăng), comments (người comment)
    
    Note: Đây là endpoint khởi tạo scan task.
    Việc scan thực tế sẽ được xử lý bởi background task với Selenium.
    """
    try:
        # Validate account exists
        acc_query = select(Account).where(Account.id == scan_data.account_id)
        acc_result = await db.execute(acc_query)
        acc = acc_result.scalar_one_or_none()
        
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Extract group ID from URL
        group_id = None
        if 'groups/' in scan_data.group_url:
            match = re.search(r'groups/([^/\?]+)', scan_data.group_url)
            if match:
                group_id = match.group(1)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="facebook_id_scan_group_start",
            message=f"Bắt đầu scan group để thu thập tối đa {scan_data.max_ids} IDs",
            level="info",
            account_id=scan_data.account_id,
            extra_data={
                "group_url": scan_data.group_url,
                "group_id": group_id,
                "max_ids": scan_data.max_ids,
                "scan_type": scan_data.scan_type
            }
        )
        
        # TODO: Implement actual scanning logic with Selenium
        # This would be done in a background task
        
        return {
            "success": True,
            "message": f"Group scan task created (max {scan_data.max_ids} IDs)",
            "account_id": scan_data.account_id,
            "group_url": scan_data.group_url,
            "scan_type": scan_data.scan_type,
            "note": "This is a task creation endpoint. Actual scanning will be processed in background."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating scan task: {str(e)}")
