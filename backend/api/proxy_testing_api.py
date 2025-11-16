"""
Proxy Testing API - Proxy Health Check and Testing
Provides endpoints for testing proxy connectivity, speed, and rotation
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import httpx
import time

from core.database import get_db, Proxy
from services.activity_logger import ActivityLogger

router = APIRouter(prefix="/api/proxy-testing", tags=["Proxy Testing"])

# ============================================
# PYDANTIC MODELS
# ============================================

class ProxyTestRequest(BaseModel):
    """Request model for testing a single proxy"""
    proxy_id: int = Field(..., description="Proxy ID to test")
    test_url: str = Field(default="https://www.google.com", description="URL to test against")
    timeout: int = Field(default=10, description="Timeout in seconds")

class BulkProxyTestRequest(BaseModel):
    """Request model for bulk proxy testing"""
    proxy_ids: Optional[List[int]] = Field(None, description="List of proxy IDs (None = test all)")
    test_url: str = Field(default="https://www.google.com", description="URL to test against")
    timeout: int = Field(default=10, description="Timeout per proxy")
    max_concurrent: int = Field(default=5, description="Max concurrent tests")

class ProxyTestResult(BaseModel):
    """Result model for proxy test"""
    proxy_id: int
    ip: str
    port: int
    status: str  # "success", "failed", "timeout"
    response_time: Optional[float] = None  # in milliseconds
    error_message: Optional[str] = None
    tested_at: datetime

class ProxyRotationConfig(BaseModel):
    """Configuration for proxy rotation"""
    strategy: str = Field("round-robin", description="Rotation strategy: round-robin, random, least-used")
    enabled: bool = Field(True, description="Enable proxy rotation")
    rotate_on_error: bool = Field(True, description="Rotate proxy when error occurs")
    max_uses_per_proxy: int = Field(100, description="Max uses before rotation")

class ProxyRotationStatus(BaseModel):
    """Status of proxy rotation system"""
    current_proxy_id: Optional[int]
    total_proxies: int
    active_proxies: int
    rotation_strategy: str
    total_rotations: int
    last_rotation: Optional[datetime]

# ============================================
# HELPER FUNCTIONS
# ============================================

def build_proxy_url(proxy: Proxy) -> str:
    """Build proxy URL from proxy object"""
    if proxy.username and proxy.password:
        return f"{proxy.type}://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}"
    else:
        return f"{proxy.type}://{proxy.ip}:{proxy.port}"

async def test_proxy_connectivity(
    proxy: Proxy,
    test_url: str = "https://www.google.com",
    timeout: int = 10
) -> ProxyTestResult:
    """
    Test a single proxy's connectivity and measure response time
    
    Args:
        proxy: Proxy object to test
        test_url: URL to test against
        timeout: Timeout in seconds
    
    Returns:
        ProxyTestResult with test results
    """
    start_time = time.time()
    
    try:
        proxy_url = build_proxy_url(proxy)
        
        async with httpx.AsyncClient(
            proxies={
                "http://": proxy_url,
                "https://": proxy_url
            },
            timeout=timeout,
            follow_redirects=True
        ) as client:
            response = await client.get(test_url)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                return ProxyTestResult(
                    proxy_id=proxy.id,
                    ip=proxy.ip,
                    port=proxy.port,
                    status="success",
                    response_time=round(response_time, 2),
                    error_message=None,
                    tested_at=datetime.now()
                )
            else:
                return ProxyTestResult(
                    proxy_id=proxy.id,
                    ip=proxy.ip,
                    port=proxy.port,
                    status="failed",
                    response_time=None,
                    error_message=f"HTTP {response.status_code}",
                    tested_at=datetime.now()
                )
    
    except asyncio.TimeoutError:
        return ProxyTestResult(
            proxy_id=proxy.id,
            ip=proxy.ip,
            port=proxy.port,
            status="timeout",
            response_time=None,
            error_message="Connection timeout",
            tested_at=datetime.now()
        )
    
    except Exception as e:
        return ProxyTestResult(
            proxy_id=proxy.id,
            ip=proxy.ip,
            port=proxy.port,
            status="failed",
            response_time=None,
            error_message=str(e)[:200],  # Limit error message length
            tested_at=datetime.now()
        )

async def update_proxy_status(
    db: AsyncSession,
    proxy_id: int,
    test_result: ProxyTestResult
):
    """Update proxy status in database based on test result"""
    new_status = "active" if test_result.status == "success" else "inactive"
    
    # Convert response_time to integer for speed field (already in ms)
    speed_value = int(test_result.response_time) if test_result.response_time else None
    
    stmt = update(Proxy).where(Proxy.id == proxy_id).values(
        status=new_status,
        last_checked=test_result.tested_at,
        speed=speed_value
    )
    
    await db.execute(stmt)
    await db.commit()

# ============================================
# API ENDPOINTS
# ============================================

@router.post("/test-single", response_model=ProxyTestResult)
async def test_single_proxy(
    request: ProxyTestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Test a single proxy connectivity and speed
    
    - Tests proxy connection to specified URL
    - Measures response time
    - Updates proxy status in database
    - Logs test results
    """
    try:
        # Get proxy from database
        result = await db.execute(select(Proxy).where(Proxy.id == request.proxy_id))
        proxy = result.scalar_one_or_none()
        
        if not proxy:
            raise HTTPException(status_code=404, detail=f"Proxy ID {request.proxy_id} not found")
        
        # Test proxy
        test_result = await test_proxy_connectivity(proxy, request.test_url, request.timeout)
        
        # Update database
        await update_proxy_status(db, proxy.id, test_result)
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            action_type="proxy_test",
            action="test_single_proxy",
            target=f"proxy_{proxy.id}",
            status=test_result.status,
            details=f"Proxy {proxy.ip}:{proxy.port} test: {test_result.status}",
            metadata={
                "proxy_id": proxy.id,
                "response_time": test_result.response_time,
                "error": test_result.error_message
            }
        )
        
        return test_result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy test failed: {str(e)}")


@router.post("/test-bulk", response_model=Dict[str, Any])
async def test_bulk_proxies(
    request: BulkProxyTestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Test multiple proxies concurrently
    
    - Tests all specified proxies (or all if none specified)
    - Runs tests concurrently with max_concurrent limit
    - Updates proxy statuses in database
    - Returns summary statistics
    """
    try:
        # Get proxies to test
        if request.proxy_ids:
            stmt = select(Proxy).where(Proxy.id.in_(request.proxy_ids))
        else:
            stmt = select(Proxy)
        
        result = await db.execute(stmt)
        proxies = result.scalars().all()
        
        if not proxies:
            raise HTTPException(status_code=404, detail="No proxies found to test")
        
        # Test proxies with concurrency limit
        semaphore = asyncio.Semaphore(request.max_concurrent)
        
        async def test_with_semaphore(proxy):
            async with semaphore:
                return await test_proxy_connectivity(proxy, request.test_url, request.timeout)
        
        # Run tests concurrently
        test_results = await asyncio.gather(
            *[test_with_semaphore(proxy) for proxy in proxies],
            return_exceptions=True
        )
        
        # Process results
        valid_results = []
        for result in test_results:
            if isinstance(result, ProxyTestResult):
                valid_results.append(result)
                # Update database
                await update_proxy_status(db, result.proxy_id, result)
        
        # Calculate statistics
        total_tested = len(valid_results)
        successful = sum(1 for r in valid_results if r.status == "success")
        failed = sum(1 for r in valid_results if r.status == "failed")
        timeout = sum(1 for r in valid_results if r.status == "timeout")
        
        avg_response_time = None
        if successful > 0:
            response_times = [r.response_time for r in valid_results if r.response_time]
            if response_times:
                avg_response_time = round(sum(response_times) / len(response_times), 2)
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            action_type="proxy_test",
            action="test_bulk_proxies",
            target="multiple_proxies",
            status="completed",
            details=f"Tested {total_tested} proxies: {successful} success, {failed} failed, {timeout} timeout",
            metadata={
                "total_tested": total_tested,
                "successful": successful,
                "failed": failed,
                "timeout": timeout,
                "avg_response_time": avg_response_time
            }
        )
        
        return {
            "success": True,
            "message": f"Tested {total_tested} proxies",
            "statistics": {
                "total_tested": total_tested,
                "successful": successful,
                "failed": failed,
                "timeout": timeout,
                "success_rate": round((successful / total_tested * 100), 2) if total_tested > 0 else 0,
                "avg_response_time_ms": avg_response_time
            },
            "results": [r.dict() for r in valid_results]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk proxy test failed: {str(e)}")


@router.get("/rotation/status", response_model=ProxyRotationStatus)
async def get_rotation_status(db: AsyncSession = Depends(get_db)):
    """
    Get current proxy rotation status
    
    - Shows current proxy in rotation
    - Total and active proxy counts
    - Rotation statistics
    """
    try:
        # Get all proxies
        result = await db.execute(select(Proxy))
        all_proxies = result.scalars().all()
        
        # Get active proxies
        active_proxies = [p for p in all_proxies if p.status == "active"]
        
        # Get rotation config (would typically be stored in settings)
        # For now, return default values
        return ProxyRotationStatus(
            current_proxy_id=active_proxies[0].id if active_proxies else None,
            total_proxies=len(all_proxies),
            active_proxies=len(active_proxies),
            rotation_strategy="round-robin",
            total_rotations=0,  # Would track this in production
            last_rotation=None   # Would track this in production
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rotation status: {str(e)}")


@router.post("/rotation/configure")
async def configure_proxy_rotation(
    config: ProxyRotationConfig,
    db: AsyncSession = Depends(get_db)
):
    """
    Configure proxy rotation settings
    
    - Set rotation strategy (round-robin, random, least-used)
    - Enable/disable rotation
    - Configure rotation behavior
    """
    try:
        # In production, this would save to settings table
        # For now, just validate and return success
        
        valid_strategies = ["round-robin", "random", "least-used"]
        if config.strategy not in valid_strategies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy. Must be one of: {', '.join(valid_strategies)}"
            )
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            action_type="proxy_config",
            action="configure_rotation",
            target="proxy_rotation",
            status="success",
            details=f"Proxy rotation configured: {config.strategy}",
            metadata=config.dict()
        )
        
        return {
            "success": True,
            "message": "Proxy rotation configured successfully",
            "config": config.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure rotation: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_proxy_testing_stats(db: AsyncSession = Depends(get_db)):
    """
    Get proxy testing statistics
    
    - Total proxies and status breakdown
    - Average response times
    - Last test times
    """
    try:
        # Get all proxies
        result = await db.execute(select(Proxy))
        proxies = result.scalars().all()
        
        if not proxies:
            return {
                "success": True,
                "statistics": {
                    "total_proxies": 0,
                    "active": 0,
                    "inactive": 0,
                    "never_tested": 0,
                    "avg_response_time_ms": None,
                    "fastest_proxy": None,
                    "slowest_proxy": None
                }
            }
        
        # Calculate statistics
        total_proxies = len(proxies)
        active = sum(1 for p in proxies if p.status == "active")
        inactive = sum(1 for p in proxies if p.status == "inactive")
        never_tested = sum(1 for p in proxies if not p.last_checked)
        
        # Response time statistics (using speed field)
        response_times = [p.speed for p in proxies if p.speed]
        avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else None
        
        fastest_proxy = None
        slowest_proxy = None
        if response_times:
            fastest = min(proxies, key=lambda p: p.speed if p.speed else float('inf'))
            slowest = max(proxies, key=lambda p: p.speed if p.speed else 0)
            
            if fastest.speed:
                fastest_proxy = {
                    "id": fastest.id,
                    "ip": fastest.ip,
                    "port": fastest.port,
                    "response_time": fastest.speed
                }
            
            if slowest.speed:
                slowest_proxy = {
                    "id": slowest.id,
                    "ip": slowest.ip,
                    "port": slowest.port,
                    "response_time": slowest.speed
                }
        
        return {
            "success": True,
            "statistics": {
                "total_proxies": total_proxies,
                "active": active,
                "inactive": inactive,
                "never_tested": never_tested,
                "health_rate": round((active / total_proxies * 100), 2) if total_proxies > 0 else 0,
                "avg_response_time_ms": avg_response_time,
                "fastest_proxy": fastest_proxy,
                "slowest_proxy": slowest_proxy
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get proxy stats: {str(e)}")
