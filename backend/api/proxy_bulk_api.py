"""
Proxy Bulk Operations API
Bulk assign, check, delete proxies
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db, Proxy, Account
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import httpx
from datetime import datetime

router = APIRouter(prefix="/api/proxies/bulk", tags=["Proxy Bulk Operations"])


class BulkAssignRequest(BaseModel):
    """Request để gán proxy hàng loạt"""
    account_ids: List[int]
    proxy_ids: List[int]
    strategy: str = "round_robin"  # round_robin, random, one_to_one


class BulkCheckRequest(BaseModel):
    """Request để check proxy hàng loạt"""
    proxy_ids: Optional[List[int]] = None  # None = check all


class BulkDeleteRequest(BaseModel):
    """Request để xóa proxy hàng loạt"""
    proxy_ids: List[int]


@router.post("/assign")
async def bulk_assign_proxies(
    request: BulkAssignRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Gán proxy hàng loạt cho nhiều accounts
    
    Strategies:
    - round_robin: Chia đều proxies cho accounts (default)
    - random: Gán random proxy cho mỗi account
    - one_to_one: Gán 1-1 (số accounts = số proxies)
    """
    try:
        from services.activity_logger import log_proxy_assign
        
        # Get accounts
        accounts_result = await db.execute(
            select(Account).where(Account.id.in_(request.account_ids))
        )
        accounts = accounts_result.scalars().all()
        
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")
        
        # Get proxies
        proxies_result = await db.execute(
            select(Proxy).where(Proxy.id.in_(request.proxy_ids))
        )
        proxies = proxies_result.scalars().all()
        
        if not proxies:
            raise HTTPException(status_code=404, detail="No proxies found")
        
        # Assign based on strategy
        assigned_count = 0
        
        if request.strategy == "round_robin":
            for i, account in enumerate(accounts):
                proxy = proxies[i % len(proxies)]
                account.proxy_id = proxy.id
                await log_proxy_assign(db, account.id, proxy.id)
                assigned_count += 1
        
        elif request.strategy == "random":
            import random
            for account in accounts:
                proxy = random.choice(proxies)
                account.proxy_id = proxy.id
                await log_proxy_assign(db, account.id, proxy.id)
                assigned_count += 1
        
        elif request.strategy == "one_to_one":
            if len(accounts) != len(proxies):
                raise HTTPException(
                    status_code=400, 
                    detail=f"one_to_one requires equal accounts and proxies. Got {len(accounts)} accounts and {len(proxies)} proxies"
                )
            
            for account, proxy in zip(accounts, proxies):
                account.proxy_id = proxy.id
                await log_proxy_assign(db, account.id, proxy.id)
                assigned_count += 1
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Assigned proxies to {assigned_count} accounts",
            "assigned_count": assigned_count,
            "strategy": request.strategy,
            "accounts_count": len(accounts),
            "proxies_count": len(proxies)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unassign")
async def bulk_unassign_proxies(
    account_ids: List[int],
    db: AsyncSession = Depends(get_db)
):
    """
    Gỡ proxy hàng loạt khỏi nhiều accounts
    """
    try:
        from services.activity_logger import log_proxy_remove
        
        # Get accounts
        accounts_result = await db.execute(
            select(Account).where(Account.id.in_(account_ids))
        )
        accounts = accounts_result.scalars().all()
        
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")
        
        # Unassign proxies
        unassigned_count = 0
        for account in accounts:
            if account.proxy_id:
                account.proxy_id = None
                await log_proxy_remove(db, account.id)
                unassigned_count += 1
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Unassigned proxies from {unassigned_count} accounts",
            "unassigned_count": unassigned_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def check_single_proxy(proxy: Proxy, db: AsyncSession) -> Dict:
    """Check single proxy liveness"""
    try:
        proxy_url = f"{proxy.protocol}://"
        if proxy.username and proxy.password:
            proxy_url += f"{proxy.username}:{proxy.password}@"
        proxy_url += f"{proxy.ip}:{proxy.port}"
        
        async with httpx.AsyncClient(proxies={"all://": proxy_url}, timeout=10.0) as client:
            start_time = datetime.now()
            response = await client.get("https://www.google.com", follow_redirects=True)
            end_time = datetime.now()
            
            latency = int((end_time - start_time).total_seconds() * 1000)  # ms
            
            if response.status_code == 200:
                proxy.status = 'active'
                proxy.speed = latency
                proxy.last_checked = datetime.now()
                await db.commit()
                
                return {
                    "proxy_id": proxy.id,
                    "ip": proxy.ip,
                    "port": proxy.port,
                    "status": "active",
                    "latency_ms": latency,
                    "success": True
                }
            else:
                proxy.status = 'error'
                proxy.last_checked = datetime.now()
                await db.commit()
                
                return {
                    "proxy_id": proxy.id,
                    "ip": proxy.ip,
                    "port": proxy.port,
                    "status": "error",
                    "error": f"Status code: {response.status_code}",
                    "success": False
                }
    
    except Exception as e:
        proxy.status = 'error'
        proxy.last_checked = datetime.now()
        await db.commit()
        
        return {
            "proxy_id": proxy.id,
            "ip": proxy.ip,
            "port": proxy.port,
            "status": "error",
            "error": str(e),
            "success": False
        }


@router.post("/check")
async def bulk_check_proxies(
    request: BulkCheckRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Kiểm tra proxy hàng loạt (live/die)
    Chạy background để không block
    """
    try:
        # Get proxies to check
        if request.proxy_ids:
            proxies_result = await db.execute(
                select(Proxy).where(Proxy.id.in_(request.proxy_ids))
            )
        else:
            # Check all proxies
            proxies_result = await db.execute(select(Proxy))
        
        proxies = proxies_result.scalars().all()
        
        if not proxies:
            raise HTTPException(status_code=404, detail="No proxies found")
        
        # Add to background tasks
        async def check_all_proxies():
            results = []
            for proxy in proxies:
                result = await check_single_proxy(proxy, db)
                results.append(result)
            
            # Log results
            from services.activity_logger import ActivityLogger
            live_count = sum(1 for r in results if r['success'])
            dead_count = len(results) - live_count
            
            await ActivityLogger.log(
                db,
                action="bulk_check_proxies",
                message=f"Checked {len(results)} proxies: {live_count} live, {dead_count} dead",
                level="info",
                extra_data={
                    "total": len(results),
                    "live": live_count,
                    "dead": dead_count
                }
            )
        
        background_tasks.add_task(check_all_proxies)
        
        return {
            "success": True,
            "message": f"Started checking {len(proxies)} proxies in background",
            "proxy_count": len(proxies)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-sync")
async def bulk_check_proxies_sync(
    request: BulkCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Kiểm tra proxy hàng loạt (synchronous - chờ kết quả)
    """
    try:
        # Get proxies to check
        if request.proxy_ids:
            proxies_result = await db.execute(
                select(Proxy).where(Proxy.id.in_(request.proxy_ids))
            )
        else:
            proxies_result = await db.execute(select(Proxy))
        
        proxies = proxies_result.scalars().all()
        
        if not proxies:
            raise HTTPException(status_code=404, detail="No proxies found")
        
        # Check all proxies
        results = []
        for proxy in proxies:
            result = await check_single_proxy(proxy, db)
            results.append(result)
        
        live_count = sum(1 for r in results if r['success'])
        dead_count = len(results) - live_count
        
        return {
            "success": True,
            "message": f"Checked {len(results)} proxies: {live_count} live, {dead_count} dead",
            "results": results,
            "summary": {
                "total": len(results),
                "live": live_count,
                "dead": dead_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def bulk_delete_proxies(
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa proxy hàng loạt
    """
    try:
        from services.activity_logger import ActivityLogger
        
        # Get proxies to delete
        proxies_result = await db.execute(
            select(Proxy).where(Proxy.id.in_(request.proxy_ids))
        )
        proxies = proxies_result.scalars().all()
        
        if not proxies:
            raise HTTPException(status_code=404, detail="No proxies found")
        
        # Unassign from accounts first
        accounts_result = await db.execute(
            select(Account).where(Account.proxy_id.in_(request.proxy_ids))
        )
        accounts_with_proxy = accounts_result.scalars().all()
        
        for account in accounts_with_proxy:
            account.proxy_id = None
        
        # Delete proxies
        deleted_count = 0
        for proxy in proxies:
            await db.delete(proxy)
            deleted_count += 1
        
        await db.commit()
        
        # Log
        await ActivityLogger.log(
            db,
            action="bulk_delete_proxies",
            message=f"Deleted {deleted_count} proxies",
            level="warning",
            extra_data={
                "deleted_count": deleted_count,
                "unassigned_accounts": len(accounts_with_proxy)
            }
        )
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} proxies and unassigned from {len(accounts_with_proxy)} accounts",
            "deleted_count": deleted_count,
            "unassigned_accounts": len(accounts_with_proxy)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def bulk_import_proxies(
    proxies_text: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Import proxy hàng loạt từ text
    Format: ip:port:username:password hoặc ip:port
    Mỗi proxy 1 dòng
    """
    try:
        lines = proxies_text.strip().split('\n')
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split(':')
                
                if len(parts) < 2:
                    errors.append(f"Invalid format: {line}")
                    skipped_count += 1
                    continue
                
                ip = parts[0]
                port = int(parts[1])
                username = parts[2] if len(parts) > 2 else None
                password = parts[3] if len(parts) > 3 else None
                
                # Check if proxy already exists
                existing = await db.execute(
                    select(Proxy).where(Proxy.ip == ip, Proxy.port == port)
                )
                if existing.scalar_one_or_none():
                    skipped_count += 1
                    continue
                
                # Create new proxy
                proxy = Proxy(
                    ip=ip,
                    port=port,
                    username=username,
                    password=password,
                    protocol='http',
                    status='active'
                )
                db.add(proxy)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error parsing {line}: {str(e)}")
                skipped_count += 1
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Imported {imported_count} proxies, skipped {skipped_count}",
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors[:10]  # Return first 10 errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def bulk_export_proxies(
    db: AsyncSession = Depends(get_db)
):
    """
    Export tất cả proxies ra text
    Format: ip:port:username:password
    """
    try:
        proxies_result = await db.execute(select(Proxy))
        proxies = proxies_result.scalars().all()
        
        lines = []
        for proxy in proxies:
            if proxy.username and proxy.password:
                line = f"{proxy.ip}:{proxy.port}:{proxy.username}:{proxy.password}"
            else:
                line = f"{proxy.ip}:{proxy.port}"
            lines.append(line)
        
        return {
            "success": True,
            "proxies_text": '\n'.join(lines),
            "count": len(lines)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
