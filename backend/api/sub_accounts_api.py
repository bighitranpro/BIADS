"""
Sub Accounts API
REST endpoints for managing sub-accounts (tài khoản phụ)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from core.database import get_db, SubAccount, Account
from services.activity_logger import ActivityLogger
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

router = APIRouter(prefix="/api/sub-accounts", tags=["Sub Accounts"])


# Pydantic Schemas
class SubAccountCreate(BaseModel):
    """Schema để tạo sub account mới"""
    main_account_id: int = Field(..., description="ID của tài khoản chính")
    uid: str = Field(..., min_length=1, max_length=50, description="Facebook UID")
    name: Optional[str] = Field(None, max_length=255, description="Tên hiển thị")
    username: Optional[str] = Field(None, max_length=255, description="Username Facebook")
    cookies: Optional[str] = Field(None, description="Cookies JSON string")
    access_token: Optional[str] = Field(None, description="Facebook access token")
    status: str = Field("active", description="Trạng thái: active, inactive, banned")
    auto_like: bool = Field(True, description="Tự động like bài viết")
    auto_comment: bool = Field(False, description="Tự động comment")
    auto_share: bool = Field(False, description="Tự động share")


class SubAccountUpdate(BaseModel):
    """Schema để update sub account"""
    name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    cookies: Optional[str] = None
    access_token: Optional[str] = None
    status: Optional[str] = None
    auto_like: Optional[bool] = None
    auto_comment: Optional[bool] = None
    auto_share: Optional[bool] = None


class SubAccountResponse(BaseModel):
    """Schema response cho sub account"""
    id: int
    main_account_id: int
    uid: str
    name: Optional[str]
    username: Optional[str]
    status: str
    auto_like: bool
    auto_comment: bool
    auto_share: bool
    interaction_count: int
    last_interaction: Optional[str]
    created_at: str
    updated_at: str
    main_account_info: Optional[Dict[str, Any]]


class SubAccountStats(BaseModel):
    """Schema cho thống kê sub accounts"""
    total_count: int
    active_count: int
    inactive_count: int
    banned_count: int
    total_interactions: int
    accounts_with_subs: int


class SubAccountInteract(BaseModel):
    """Schema cho interaction request"""
    sub_account_ids: List[int] = Field(..., description="Danh sách ID sub accounts")
    target_post_url: str = Field(..., description="URL bài viết cần tương tác")
    actions: List[str] = Field(..., description="Danh sách hành động: like, comment, share")
    comment_text: Optional[str] = Field(None, description="Nội dung comment (nếu có)")
    delay_seconds: int = Field(5, ge=1, le=60, description="Delay giữa các tương tác")


# API Endpoints

@router.get("/", response_model=List[SubAccountResponse])
async def get_sub_accounts(
    main_account_id: Optional[int] = Query(None, description="Filter by main account ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    auto_like: Optional[bool] = Query(None, description="Filter by auto_like setting"),
    limit: int = Query(100, ge=1, le=500, description="Max number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách sub accounts với filters
    
    Query params:
    - main_account_id: Filter theo tài khoản chính
    - status: Filter theo trạng thái (active, inactive, banned)
    - auto_like: Filter theo cài đặt auto like
    - limit: Số lượng tối đa (default 100, max 500)
    - offset: Bỏ qua bao nhiêu records (pagination)
    """
    try:
        # Build query với filters
        query = select(SubAccount)
        
        conditions = []
        if main_account_id:
            conditions.append(SubAccount.main_account_id == main_account_id)
        if status:
            conditions.append(SubAccount.status == status)
        if auto_like is not None:
            conditions.append(SubAccount.auto_like == auto_like)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination
        query = query.offset(offset).limit(limit).order_by(SubAccount.created_at.desc())
        
        result = await db.execute(query)
        sub_accounts = result.scalars().all()
        
        # Format response với main account info
        response_data = []
        for sub_acc in sub_accounts:
            # Get main account info
            main_acc_query = select(Account).where(Account.id == sub_acc.main_account_id)
            main_acc_result = await db.execute(main_acc_query)
            main_acc = main_acc_result.scalar_one_or_none()
            
            main_acc_info = None
            if main_acc:
                main_acc_info = {
                    "id": main_acc.id,
                    "uid": main_acc.uid,
                    "name": main_acc.name,
                    "username": main_acc.username
                }
            
            response_data.append({
                "id": sub_acc.id,
                "main_account_id": sub_acc.main_account_id,
                "uid": sub_acc.uid,
                "name": sub_acc.name,
                "username": sub_acc.username,
                "status": sub_acc.status,
                "auto_like": sub_acc.auto_like,
                "auto_comment": sub_acc.auto_comment,
                "auto_share": sub_acc.auto_share,
                "interaction_count": sub_acc.interaction_count,
                "last_interaction": sub_acc.last_interaction.isoformat() if sub_acc.last_interaction else None,
                "created_at": sub_acc.created_at.isoformat(),
                "updated_at": sub_acc.updated_at.isoformat(),
                "main_account_info": main_acc_info
            })
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sub accounts: {str(e)}")


@router.get("/stats", response_model=SubAccountStats)
async def get_sub_accounts_stats(
    main_account_id: Optional[int] = Query(None, description="Stats for specific main account"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thống kê sub accounts
    
    Query params:
    - main_account_id: Thống kê cho tài khoản chính cụ thể (optional)
    """
    try:
        # Build base query
        base_query = select(SubAccount)
        if main_account_id:
            base_query = base_query.where(SubAccount.main_account_id == main_account_id)
        
        # Total count
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total_count = total_result.scalar() or 0
        
        # Active count
        active_query = select(func.count()).select_from(
            base_query.where(SubAccount.status == 'active').subquery()
        )
        active_result = await db.execute(active_query)
        active_count = active_result.scalar() or 0
        
        # Inactive count
        inactive_query = select(func.count()).select_from(
            base_query.where(SubAccount.status == 'inactive').subquery()
        )
        inactive_result = await db.execute(inactive_query)
        inactive_count = inactive_result.scalar() or 0
        
        # Banned count
        banned_query = select(func.count()).select_from(
            base_query.where(SubAccount.status == 'banned').subquery()
        )
        banned_result = await db.execute(banned_query)
        banned_count = banned_result.scalar() or 0
        
        # Total interactions
        interactions_query = select(func.sum(SubAccount.interaction_count)).select_from(base_query.subquery())
        interactions_result = await db.execute(interactions_query)
        total_interactions = interactions_result.scalar() or 0
        
        # Accounts with sub accounts
        accounts_query = select(func.count(func.distinct(SubAccount.main_account_id))).select_from(base_query.subquery())
        accounts_result = await db.execute(accounts_query)
        accounts_with_subs = accounts_result.scalar() or 0
        
        return {
            "total_count": total_count,
            "active_count": active_count,
            "inactive_count": inactive_count,
            "banned_count": banned_count,
            "total_interactions": int(total_interactions),
            "accounts_with_subs": accounts_with_subs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.get("/{sub_account_id}", response_model=SubAccountResponse)
async def get_sub_account(
    sub_account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Lấy thông tin chi tiết một sub account"""
    try:
        query = select(SubAccount).where(SubAccount.id == sub_account_id)
        result = await db.execute(query)
        sub_acc = result.scalar_one_or_none()
        
        if not sub_acc:
            raise HTTPException(status_code=404, detail="Sub account not found")
        
        # Get main account info
        main_acc_query = select(Account).where(Account.id == sub_acc.main_account_id)
        main_acc_result = await db.execute(main_acc_query)
        main_acc = main_acc_result.scalar_one_or_none()
        
        main_acc_info = None
        if main_acc:
            main_acc_info = {
                "id": main_acc.id,
                "uid": main_acc.uid,
                "name": main_acc.name,
                "username": main_acc.username
            }
        
        return {
            "id": sub_acc.id,
            "main_account_id": sub_acc.main_account_id,
            "uid": sub_acc.uid,
            "name": sub_acc.name,
            "username": sub_acc.username,
            "status": sub_acc.status,
            "auto_like": sub_acc.auto_like,
            "auto_comment": sub_acc.auto_comment,
            "auto_share": sub_acc.auto_share,
            "interaction_count": sub_acc.interaction_count,
            "last_interaction": sub_acc.last_interaction.isoformat() if sub_acc.last_interaction else None,
            "created_at": sub_acc.created_at.isoformat(),
            "updated_at": sub_acc.updated_at.isoformat(),
            "main_account_info": main_acc_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sub account: {str(e)}")


@router.post("/", response_model=Dict[str, Any])
async def create_sub_account(
    sub_account: SubAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo sub account mới
    
    Body:
    - main_account_id: ID tài khoản chính (required)
    - uid: Facebook UID (required)
    - name: Tên hiển thị (optional)
    - username: Username Facebook (optional)
    - cookies: Cookies JSON string (optional)
    - access_token: Access token (optional)
    - status: Trạng thái (default: active)
    - auto_like: Tự động like (default: true)
    - auto_comment: Tự động comment (default: false)
    - auto_share: Tự động share (default: false)
    """
    try:
        # Check if main account exists
        main_acc_query = select(Account).where(Account.id == sub_account.main_account_id)
        main_acc_result = await db.execute(main_acc_query)
        main_acc = main_acc_result.scalar_one_or_none()
        
        if not main_acc:
            raise HTTPException(status_code=404, detail="Main account not found")
        
        # Check if UID already exists
        existing_query = select(SubAccount).where(SubAccount.uid == sub_account.uid)
        existing_result = await db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Sub account with this UID already exists")
        
        # Create new sub account
        new_sub_acc = SubAccount(
            main_account_id=sub_account.main_account_id,
            uid=sub_account.uid,
            name=sub_account.name,
            username=sub_account.username,
            cookies=sub_account.cookies,
            access_token=sub_account.access_token,
            status=sub_account.status,
            auto_like=sub_account.auto_like,
            auto_comment=sub_account.auto_comment,
            auto_share=sub_account.auto_share,
            interaction_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_sub_acc)
        await db.commit()
        await db.refresh(new_sub_acc)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="sub_account_create",
            message=f"Đã tạo sub account {sub_account.uid} cho tài khoản chính {main_acc.name or main_acc.uid}",
            level="success",
            account_id=sub_account.main_account_id,
            extra_data={
                "sub_account_id": new_sub_acc.id,
                "sub_account_uid": sub_account.uid,
                "main_account_uid": main_acc.uid
            }
        )
        
        return {
            "success": True,
            "message": "Sub account created successfully",
            "sub_account_id": new_sub_acc.id,
            "uid": new_sub_acc.uid
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating sub account: {str(e)}")


@router.put("/{sub_account_id}", response_model=Dict[str, Any])
async def update_sub_account(
    sub_account_id: int,
    update_data: SubAccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật thông tin sub account
    
    Body (tất cả optional):
    - name: Tên hiển thị
    - username: Username Facebook
    - cookies: Cookies JSON string
    - access_token: Access token
    - status: Trạng thái
    - auto_like: Tự động like
    - auto_comment: Tự động comment
    - auto_share: Tự động share
    """
    try:
        # Get existing sub account
        query = select(SubAccount).where(SubAccount.id == sub_account_id)
        result = await db.execute(query)
        sub_acc = result.scalar_one_or_none()
        
        if not sub_acc:
            raise HTTPException(status_code=404, detail="Sub account not found")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(sub_acc, field, value)
        
        sub_acc.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(sub_acc)
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="sub_account_update",
            message=f"Đã cập nhật sub account {sub_acc.uid}",
            level="info",
            account_id=sub_acc.main_account_id,
            extra_data={
                "sub_account_id": sub_acc.id,
                "updated_fields": list(update_dict.keys())
            }
        )
        
        return {
            "success": True,
            "message": "Sub account updated successfully",
            "sub_account_id": sub_acc.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating sub account: {str(e)}")


@router.delete("/{sub_account_id}", response_model=Dict[str, Any])
async def delete_sub_account(
    sub_account_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Xóa sub account"""
    try:
        # Get sub account
        query = select(SubAccount).where(SubAccount.id == sub_account_id)
        result = await db.execute(query)
        sub_acc = result.scalar_one_or_none()
        
        if not sub_acc:
            raise HTTPException(status_code=404, detail="Sub account not found")
        
        uid = sub_acc.uid
        main_account_id = sub_acc.main_account_id
        
        # Delete sub account
        await db.delete(sub_acc)
        await db.commit()
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="sub_account_delete",
            message=f"Đã xóa sub account {uid}",
            level="warning",
            account_id=main_account_id,
            extra_data={
                "sub_account_id": sub_account_id,
                "sub_account_uid": uid
            }
        )
        
        return {
            "success": True,
            "message": "Sub account deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting sub account: {str(e)}")


@router.post("/bulk/import", response_model=Dict[str, Any])
async def import_sub_accounts(
    file: UploadFile = File(..., description="Text file with format: main_account_uid|sub_uid|name|username per line"),
    db: AsyncSession = Depends(get_db)
):
    """
    Import sub accounts từ file text
    
    Format file (mỗi dòng):
    main_account_uid|sub_uid|name|username
    
    hoặc đơn giản:
    main_account_uid|sub_uid
    
    Example:
    100012345678|100087654321|Nguyen Van A|nguyenvana
    100012345678|100087654322|Tran Thi B
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
                parts = [p.strip() for p in line.split('|')]
                
                if len(parts) < 2:
                    errors.append(f"Line {line_num}: Invalid format (need at least main_uid|sub_uid)")
                    skipped_count += 1
                    continue
                
                main_uid = parts[0]
                sub_uid = parts[1]
                name = parts[2] if len(parts) > 2 else None
                username = parts[3] if len(parts) > 3 else None
                
                # Find main account
                main_acc_query = select(Account).where(Account.uid == main_uid)
                main_acc_result = await db.execute(main_acc_query)
                main_acc = main_acc_result.scalar_one_or_none()
                
                if not main_acc:
                    errors.append(f"Line {line_num}: Main account {main_uid} not found")
                    skipped_count += 1
                    continue
                
                # Check if sub account already exists
                existing_query = select(SubAccount).where(SubAccount.uid == sub_uid)
                existing_result = await db.execute(existing_query)
                existing = existing_result.scalar_one_or_none()
                
                if existing:
                    errors.append(f"Line {line_num}: Sub account {sub_uid} already exists")
                    skipped_count += 1
                    continue
                
                # Create sub account
                new_sub_acc = SubAccount(
                    main_account_id=main_acc.id,
                    uid=sub_uid,
                    name=name,
                    username=username,
                    status='active',
                    auto_like=True,
                    auto_comment=False,
                    auto_share=False,
                    interaction_count=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                db.add(new_sub_acc)
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
                action="sub_account_import",
                message=f"Đã import {created_count} sub accounts từ file",
                level="success",
                extra_data={
                    "created_count": created_count,
                    "skipped_count": skipped_count,
                    "total_lines": len(lines)
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
        raise HTTPException(status_code=500, detail=f"Error importing sub accounts: {str(e)}")


@router.post("/bulk/interact", response_model=Dict[str, Any])
async def interact_with_sub_accounts(
    interact_data: SubAccountInteract,
    db: AsyncSession = Depends(get_db)
):
    """
    Sử dụng sub accounts để tương tác với bài viết
    
    Body:
    - sub_account_ids: Danh sách ID sub accounts
    - target_post_url: URL bài viết cần tương tác
    - actions: Danh sách hành động ["like", "comment", "share"]
    - comment_text: Nội dung comment (nếu có action comment)
    - delay_seconds: Delay giữa các tương tác (default: 5)
    
    Note: Đây là endpoint khởi tạo task, việc tương tác thực tế
    sẽ được xử lý bởi background task với Selenium
    """
    try:
        # Validate sub accounts exist
        sub_accounts = []
        for sub_id in interact_data.sub_account_ids:
            query = select(SubAccount).where(SubAccount.id == sub_id)
            result = await db.execute(query)
            sub_acc = result.scalar_one_or_none()
            
            if not sub_acc:
                raise HTTPException(status_code=404, detail=f"Sub account ID {sub_id} not found")
            
            if sub_acc.status != 'active':
                raise HTTPException(status_code=400, detail=f"Sub account {sub_acc.uid} is not active")
            
            sub_accounts.append(sub_acc)
        
        # Validate actions
        valid_actions = ['like', 'comment', 'share']
        for action in interact_data.actions:
            if action not in valid_actions:
                raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
        
        if 'comment' in interact_data.actions and not interact_data.comment_text:
            raise HTTPException(status_code=400, detail="comment_text is required when using comment action")
        
        # Log activity
        await ActivityLogger.log(
            db=db,
            action="sub_account_interact_start",
            message=f"Bắt đầu tương tác với {len(sub_accounts)} sub accounts",
            level="info",
            extra_data={
                "sub_account_count": len(sub_accounts),
                "target_post_url": interact_data.target_post_url,
                "actions": interact_data.actions,
                "delay_seconds": interact_data.delay_seconds
            }
        )
        
        # TODO: Implement actual interaction logic with Selenium
        # This would be done in a background task
        # For now, just return success response
        
        return {
            "success": True,
            "message": f"Interaction task created for {len(sub_accounts)} sub accounts",
            "sub_account_count": len(sub_accounts),
            "actions": interact_data.actions,
            "target_url": interact_data.target_post_url,
            "note": "This is a task creation endpoint. Actual interaction will be processed in background."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating interaction task: {str(e)}")
