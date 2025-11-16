"""
Export API - Data Export Functionality
Provides endpoints for exporting data to CSV and JSON formats
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Literal
from datetime import datetime
import csv
import json
import io

from core.database import get_db, Account, Proxy, FacebookID, WhitelistAccount, Message, ActivityLog

router = APIRouter(prefix="/api/export", tags=["Export"])


def generate_csv(headers: List[str], rows: List[List[str]]) -> str:
    """Generate CSV string from headers and rows"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def generate_filename(entity: str, format: str) -> str:
    """Generate filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"bi_ads_{entity}_{timestamp}.{format}"


@router.get("/accounts")
async def export_accounts(
    format: Literal["csv", "json"] = "csv",
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export accounts to CSV or JSON
    
    Query Parameters:
    - format: Export format (csv or json)
    - status: Filter by status (optional)
    """
    try:
        # Build query
        query = select(Account)
        if status:
            query = query.where(Account.status == status)
        
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found to export")
        
        if format == "csv":
            # CSV format
            headers = [
                "ID", "Email", "Status", "Sub Account", "Proxy ID", 
                "Cookie Valid", "Last Active", "Created At"
            ]
            rows = []
            for acc in accounts:
                rows.append([
                    str(acc.id),
                    acc.email or "",
                    acc.status or "",
                    acc.sub_account or "",
                    str(acc.proxy_id) if acc.proxy_id else "",
                    "Yes" if acc.cookie_valid else "No",
                    acc.last_active.strftime("%Y-%m-%d %H:%M:%S") if acc.last_active else "",
                    acc.created_at.strftime("%Y-%m-%d %H:%M:%S") if acc.created_at else ""
                ])
            
            csv_content = generate_csv(headers, rows)
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('accounts', 'csv')}"
                }
            )
        
        else:  # JSON format
            data = []
            for acc in accounts:
                data.append({
                    "id": acc.id,
                    "email": acc.email,
                    "status": acc.status,
                    "sub_account": acc.sub_account,
                    "proxy_id": acc.proxy_id,
                    "cookie_valid": acc.cookie_valid,
                    "last_active": acc.last_active.isoformat() if acc.last_active else None,
                    "created_at": acc.created_at.isoformat() if acc.created_at else None
                })
            
            return Response(
                content=json.dumps(data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('accounts', 'json')}"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/proxies")
async def export_proxies(
    format: Literal["csv", "json"] = "csv",
    type: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export proxies to CSV or JSON
    
    Query Parameters:
    - format: Export format (csv or json)
    - type: Filter by type (optional)
    - status: Filter by status (optional)
    """
    try:
        # Build query
        query = select(Proxy)
        if type:
            query = query.where(Proxy.type == type)
        if status:
            query = query.where(Proxy.status == status)
        
        result = await db.execute(query)
        proxies = result.scalars().all()
        
        if not proxies:
            raise HTTPException(status_code=404, detail="No proxies found to export")
        
        if format == "csv":
            # CSV format
            headers = [
                "ID", "IP", "Port", "Username", "Password", "Type", 
                "Status", "Location", "Last Checked", "Created At"
            ]
            rows = []
            for proxy in proxies:
                rows.append([
                    str(proxy.id),
                    proxy.ip or "",
                    str(proxy.port) if proxy.port else "",
                    proxy.username or "",
                    proxy.password or "",
                    proxy.type or "",
                    proxy.status or "",
                    proxy.location or "",
                    proxy.last_checked.strftime("%Y-%m-%d %H:%M:%S") if proxy.last_checked else "",
                    proxy.created_at.strftime("%Y-%m-%d %H:%M:%S") if proxy.created_at else ""
                ])
            
            csv_content = generate_csv(headers, rows)
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('proxies', 'csv')}"
                }
            )
        
        else:  # JSON format
            data = []
            for proxy in proxies:
                data.append({
                    "id": proxy.id,
                    "ip": proxy.ip,
                    "port": proxy.port,
                    "username": proxy.username,
                    "password": proxy.password,
                    "type": proxy.type,
                    "status": proxy.status,
                    "location": proxy.location,
                    "last_checked": proxy.last_checked.isoformat() if proxy.last_checked else None,
                    "created_at": proxy.created_at.isoformat() if proxy.created_at else None
                })
            
            return Response(
                content=json.dumps(data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('proxies', 'json')}"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/facebook-ids")
async def export_facebook_ids(
    format: Literal["csv", "json"] = "csv",
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export Facebook IDs to CSV or JSON
    
    Query Parameters:
    - format: Export format (csv or json)
    - status: Filter by status (optional)
    """
    try:
        # Build query
        query = select(FacebookID)
        if status:
            query = query.where(FacebookID.status == status)
        
        result = await db.execute(query)
        facebook_ids = result.scalars().all()
        
        if not facebook_ids:
            raise HTTPException(status_code=404, detail="No Facebook IDs found to export")
        
        if format == "csv":
            # CSV format
            headers = [
                "ID", "UID", "Name", "Profile URL", "Status", 
                "Gender", "Friends Count", "Created At"
            ]
            rows = []
            for fb in facebook_ids:
                rows.append([
                    str(fb.id),
                    fb.uid or "",
                    fb.name or "",
                    fb.profile_url or "",
                    fb.status or "",
                    fb.gender or "",
                    str(fb.friends_count) if fb.friends_count else "0",
                    fb.created_at.strftime("%Y-%m-%d %H:%M:%S") if fb.created_at else ""
                ])
            
            csv_content = generate_csv(headers, rows)
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('facebook_ids', 'csv')}"
                }
            )
        
        else:  # JSON format
            data = []
            for fb in facebook_ids:
                data.append({
                    "id": fb.id,
                    "uid": fb.uid,
                    "name": fb.name,
                    "profile_url": fb.profile_url,
                    "status": fb.status,
                    "gender": fb.gender,
                    "friends_count": fb.friends_count,
                    "created_at": fb.created_at.isoformat() if fb.created_at else None
                })
            
            return Response(
                content=json.dumps(data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('facebook_ids', 'json')}"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/whitelist")
async def export_whitelist(
    format: Literal["csv", "json"] = "csv",
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export whitelist to CSV or JSON
    
    Query Parameters:
    - format: Export format (csv or json)
    - status: Filter by status (optional)
    """
    try:
        # Build query
        query = select(WhitelistAccount)
        if status:
            query = query.where(WhitelistAccount.status == status)
        
        result = await db.execute(query)
        whitelist = result.scalars().all()
        
        if not whitelist:
            raise HTTPException(status_code=404, detail="No whitelist entries found to export")
        
        if format == "csv":
            # CSV format
            headers = [
                "ID", "UID", "Name", "Status", "Relationship", 
                "Note", "Added At", "Last Updated"
            ]
            rows = []
            for wl in whitelist:
                rows.append([
                    str(wl.id),
                    wl.uid or "",
                    wl.name or "",
                    wl.status or "",
                    wl.relationship or "",
                    wl.note or "",
                    wl.added_at.strftime("%Y-%m-%d %H:%M:%S") if wl.added_at else "",
                    wl.updated_at.strftime("%Y-%m-%d %H:%M:%S") if wl.updated_at else ""
                ])
            
            csv_content = generate_csv(headers, rows)
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('whitelist', 'csv')}"
                }
            )
        
        else:  # JSON format
            data = []
            for wl in whitelist:
                data.append({
                    "id": wl.id,
                    "uid": wl.uid,
                    "name": wl.name,
                    "status": wl.status,
                    "relationship": wl.relationship,
                    "note": wl.note,
                    "added_at": wl.added_at.isoformat() if wl.added_at else None,
                    "updated_at": wl.updated_at.isoformat() if wl.updated_at else None
                })
            
            return Response(
                content=json.dumps(data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('whitelist', 'json')}"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/messages")
async def export_messages(
    format: Literal["csv", "json"] = "csv",
    conversation_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export messages to CSV or JSON
    
    Query Parameters:
    - format: Export format (csv or json)
    - conversation_id: Filter by conversation (optional)
    """
    try:
        # Build query
        query = select(Message)
        if conversation_id:
            query = query.where(Message.conversation_id == conversation_id)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            raise HTTPException(status_code=404, detail="No messages found to export")
        
        if format == "csv":
            # CSV format
            headers = [
                "ID", "Conversation ID", "Account ID", "Sender UID", 
                "Receiver UID", "Content", "Direction", "Timestamp"
            ]
            rows = []
            for msg in messages:
                rows.append([
                    str(msg.id),
                    str(msg.conversation_id) if msg.conversation_id else "",
                    str(msg.account_id) if msg.account_id else "",
                    msg.sender_uid or "",
                    msg.receiver_uid or "",
                    msg.content or "",
                    msg.direction or "",
                    msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if msg.timestamp else ""
                ])
            
            csv_content = generate_csv(headers, rows)
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('messages', 'csv')}"
                }
            )
        
        else:  # JSON format
            data = []
            for msg in messages:
                data.append({
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "account_id": msg.account_id,
                    "sender_uid": msg.sender_uid,
                    "receiver_uid": msg.receiver_uid,
                    "content": msg.content,
                    "direction": msg.direction,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                })
            
            return Response(
                content=json.dumps(data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('messages', 'json')}"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/activity-log")
async def export_activity_log(
    format: Literal["csv", "json"] = "csv",
    action_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export activity log to CSV or JSON
    
    Query Parameters:
    - format: Export format (csv or json)
    - action_type: Filter by action type (optional)
    """
    try:
        # Build query
        query = select(ActivityLog)
        if action_type:
            query = query.where(ActivityLog.action_type == action_type)
        
        result = await db.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="No activity logs found to export")
        
        if format == "csv":
            # CSV format
            headers = [
                "ID", "Account ID", "Action Type", "Action", 
                "Target", "Status", "Details", "Timestamp"
            ]
            rows = []
            for log in logs:
                rows.append([
                    str(log.id),
                    str(log.account_id) if log.account_id else "",
                    log.action_type or "",
                    log.action or "",
                    log.target or "",
                    log.status or "",
                    log.details or "",
                    log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else ""
                ])
            
            csv_content = generate_csv(headers, rows)
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('activity_log', 'csv')}"
                }
            )
        
        else:  # JSON format
            data = []
            for log in logs:
                data.append({
                    "id": log.id,
                    "account_id": log.account_id,
                    "action_type": log.action_type,
                    "action": log.action,
                    "target": log.target,
                    "status": log.status,
                    "details": log.details,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                })
            
            return Response(
                content=json.dumps(data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={generate_filename('activity_log', 'json')}"
                }
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/stats")
async def get_export_stats(db: AsyncSession = Depends(get_db)):
    """Get statistics about exportable data"""
    try:
        # Count records in each table
        accounts_count = (await db.execute(select(Account))).scalars().all()
        proxies_count = (await db.execute(select(Proxy))).scalars().all()
        facebook_ids_count = (await db.execute(select(FacebookID))).scalars().all()
        whitelist_count = (await db.execute(select(WhitelistAccount))).scalars().all()
        messages_count = (await db.execute(select(Message))).scalars().all()
        activity_log_count = (await db.execute(select(ActivityLog))).scalars().all()
        
        return {
            "success": True,
            "stats": {
                "accounts": len(accounts_count),
                "proxies": len(proxies_count),
                "facebook_ids": len(facebook_ids_count),
                "whitelist": len(whitelist_count),
                "messages": len(messages_count),
                "activity_log": len(activity_log_count)
            },
            "total_exportable_records": (
                len(accounts_count) + 
                len(proxies_count) + 
                len(facebook_ids_count) + 
                len(whitelist_count) + 
                len(messages_count) + 
                len(activity_log_count)
            ),
            "supported_formats": ["csv", "json"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export stats: {str(e)}")
