"""
Messages Management API

Handles messaging, conversations, auto-reply configurations, and message statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import json

from core.database import get_db, Account, Message, AutoReplyTemplate
from services.activity_logger import ActivityLogger

router = APIRouter(prefix="/api/messages", tags=["Messages"])

# Pydantic Models
class MessageCreate(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    account_id: int = Field(..., description="Account sending the message")
    receiver_uid: str = Field(..., description="Receiver UID")
    receiver_name: Optional[str] = Field(None, description="Receiver name")
    message_text: str = Field(..., description="Message content")
    message_type: str = Field("text", description="Message type: text, image, sticker, link")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule message for later")
    
    @validator('receiver_uid')
    def validate_uid(cls, v):
        if not v or len(v) < 10 or len(v) > 20:
            raise ValueError('Invalid UID format')
        if not v.isdigit():
            raise ValueError('UID must contain only digits')
        return v

class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None
    message_text: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    account_id: int
    sender_uid: str
    sender_name: Optional[str]
    receiver_uid: str
    receiver_name: Optional[str]
    message_text: Optional[str]
    message_type: str
    is_read: bool
    is_sent_by_me: bool
    auto_reply_enabled: bool
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    conversation_id: str
    account_id: int
    account_info: Optional[dict]
    other_participant_uid: str
    other_participant_name: Optional[str]
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int
    total_messages: int
    is_auto_reply_enabled: bool

class AutoReplyTemplateCreate(BaseModel):
    account_id: int = Field(..., description="Account ID")
    name: str = Field(..., description="Template name")
    trigger_keywords: List[str] = Field(..., description="Keywords that trigger this reply")
    reply_message: str = Field(..., description="Auto-reply message content")
    is_active: bool = Field(True, description="Whether template is active")
    priority: int = Field(0, description="Priority (higher = checked first)")

class AutoReplyTemplateUpdate(BaseModel):
    name: Optional[str] = None
    trigger_keywords: Optional[List[str]] = None
    reply_message: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

class AutoReplyTemplateResponse(BaseModel):
    id: int
    account_id: int
    name: str
    trigger_keywords: List[str]
    reply_message: str
    is_active: bool
    priority: int
    use_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageStats(BaseModel):
    total_conversations: int
    total_messages: int
    unread_messages: int
    sent_messages: int
    received_messages: int
    auto_replies_sent: int
    active_auto_reply_templates: int
    messages_today: int
    messages_this_week: int
    top_contacts: List[dict]

# API Endpoints

@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    unread_only: bool = Query(False, description="Show only unread conversations"),
    search: Optional[str] = Query(None, description="Search by participant name or message"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of conversations with filters
    """
    try:
        # Build query to get distinct conversations
        query = select(Message.conversation_id, Message.account_id).distinct()
        
        if account_id:
            query = query.where(Message.account_id == account_id)
        
        if search:
            query = query.where(
                or_(
                    Message.sender_name.ilike(f"%{search}%"),
                    Message.receiver_name.ilike(f"%{search}%"),
                    Message.message_text.ilike(f"%{search}%")
                )
            )
        
        result = await db.execute(query.limit(limit).offset(offset))
        conversations = result.fetchall()
        
        # Build conversation responses
        conversation_responses = []
        for conv_id, acc_id in conversations:
            # Get conversation details
            conv_query = select(Message).where(
                and_(
                    Message.conversation_id == conv_id,
                    Message.account_id == acc_id
                )
            ).order_by(desc(Message.created_at))
            
            conv_result = await db.execute(conv_query)
            messages = conv_result.scalars().all()
            
            if not messages:
                continue
            
            # Get unread count
            unread_query = select(func.count(Message.id)).where(
                and_(
                    Message.conversation_id == conv_id,
                    Message.account_id == acc_id,
                    Message.is_read == False,
                    Message.is_sent_by_me == False
                )
            )
            unread_result = await db.execute(unread_query)
            unread_count = unread_result.scalar() or 0
            
            # Skip if unread_only filter is active and no unread messages
            if unread_only and unread_count == 0:
                continue
            
            # Get account info
            account_query = select(Account).where(Account.id == acc_id)
            account_result = await db.execute(account_query)
            account = account_result.scalar_one_or_none()
            
            # Determine other participant
            last_message = messages[0]
            other_uid = last_message.receiver_uid if last_message.is_sent_by_me else last_message.sender_uid
            other_name = last_message.receiver_name if last_message.is_sent_by_me else last_message.sender_name
            
            conversation_responses.append(ConversationResponse(
                conversation_id=conv_id,
                account_id=acc_id,
                account_info={
                    "id": account.id,
                    "uid": account.uid,
                    "name": account.name
                } if account else None,
                other_participant_uid=other_uid,
                other_participant_name=other_name,
                last_message=last_message.message_text,
                last_message_at=last_message.created_at,
                unread_count=unread_count,
                total_messages=len(messages),
                is_auto_reply_enabled=last_message.auto_reply_enabled
            ))
        
        return conversation_responses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")


@router.get("/{conversation_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get messages in a specific conversation
    """
    try:
        query = select(Message).where(Message.conversation_id == conversation_id)
        
        if account_id:
            query = query.where(Message.account_id == account_id)
        
        query = query.order_by(desc(Message.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        # Mark messages as read
        if messages:
            for message in messages:
                if not message.is_read and not message.is_sent_by_me:
                    message.is_read = True
            await db.commit()
        
        return messages
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.post("/send", response_model=dict)
async def send_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a new message
    """
    try:
        # Get account info
        account_query = select(Account).where(Account.id == message_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create message
        new_message = Message(
            conversation_id=message_data.conversation_id,
            account_id=message_data.account_id,
            sender_uid=account.uid,
            sender_name=account.name,
            receiver_uid=message_data.receiver_uid,
            receiver_name=message_data.receiver_name,
            message_text=message_data.message_text,
            message_type=message_data.message_type,
            is_sent_by_me=True,
            scheduled_at=message_data.scheduled_at,
            sent_at=datetime.now() if not message_data.scheduled_at else None
        )
        
        db.add(new_message)
        await db.commit()
        await db.refresh(new_message)
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=message_data.account_id,
            action="send_message",
            message=f"Sent message to {message_data.receiver_uid}",
            level="info",
            extra_data={"conversation_id": message_data.conversation_id}
        )
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "message_id": new_message.id,
            "scheduled": message_data.scheduled_at is not None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/stats/dashboard", response_model=MessageStats)
async def get_message_stats(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get message statistics dashboard
    """
    try:
        base_query = select(Message)
        if account_id:
            base_query = base_query.where(Message.account_id == account_id)
        
        # Total conversations
        conv_query = select(func.count(func.distinct(Message.conversation_id)))
        if account_id:
            conv_query = conv_query.where(Message.account_id == account_id)
        conv_result = await db.execute(conv_query)
        total_conversations = conv_result.scalar() or 0
        
        # Total messages
        total_query = select(func.count(Message.id))
        if account_id:
            total_query = total_query.where(Message.account_id == account_id)
        total_result = await db.execute(total_query)
        total_messages = total_result.scalar() or 0
        
        # Unread messages
        unread_query = select(func.count(Message.id)).where(
            and_(
                Message.is_read == False,
                Message.is_sent_by_me == False
            )
        )
        if account_id:
            unread_query = unread_query.where(Message.account_id == account_id)
        unread_result = await db.execute(unread_query)
        unread_messages = unread_result.scalar() or 0
        
        # Sent messages
        sent_query = select(func.count(Message.id)).where(Message.is_sent_by_me == True)
        if account_id:
            sent_query = sent_query.where(Message.account_id == account_id)
        sent_result = await db.execute(sent_query)
        sent_messages = sent_result.scalar() or 0
        
        # Received messages
        received_messages = total_messages - sent_messages
        
        # Auto-replies sent
        auto_reply_query = select(func.count(Message.id)).where(
            and_(
                Message.auto_reply_enabled == True,
                Message.is_sent_by_me == True
            )
        )
        if account_id:
            auto_reply_query = auto_reply_query.where(Message.account_id == account_id)
        auto_reply_result = await db.execute(auto_reply_query)
        auto_replies_sent = auto_reply_result.scalar() or 0
        
        # Active auto-reply templates
        template_query = select(func.count(AutoReplyTemplate.id)).where(
            AutoReplyTemplate.is_active == True
        )
        if account_id:
            template_query = template_query.where(AutoReplyTemplate.account_id == account_id)
        template_result = await db.execute(template_query)
        active_templates = template_result.scalar() or 0
        
        # Messages today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_query = select(func.count(Message.id)).where(
            Message.created_at >= today_start
        )
        if account_id:
            today_query = today_query.where(Message.account_id == account_id)
        today_result = await db.execute(today_query)
        messages_today = today_result.scalar() or 0
        
        # Messages this week
        week_start = datetime.now() - timedelta(days=7)
        week_query = select(func.count(Message.id)).where(
            Message.created_at >= week_start
        )
        if account_id:
            week_query = week_query.where(Message.account_id == account_id)
        week_result = await db.execute(week_query)
        messages_this_week = week_result.scalar() or 0
        
        # Top contacts (most messaged)
        top_contacts_query = select(
            Message.receiver_uid,
            Message.receiver_name,
            func.count(Message.id).label('message_count')
        ).where(
            Message.is_sent_by_me == True
        ).group_by(
            Message.receiver_uid,
            Message.receiver_name
        ).order_by(
            desc('message_count')
        ).limit(10)
        
        if account_id:
            top_contacts_query = top_contacts_query.where(Message.account_id == account_id)
        
        top_contacts_result = await db.execute(top_contacts_query)
        top_contacts_raw = top_contacts_result.fetchall()
        
        top_contacts = [
            {
                "uid": uid,
                "name": name or "Unknown",
                "message_count": count
            }
            for uid, name, count in top_contacts_raw
        ]
        
        return MessageStats(
            total_conversations=total_conversations,
            total_messages=total_messages,
            unread_messages=unread_messages,
            sent_messages=sent_messages,
            received_messages=received_messages,
            auto_replies_sent=auto_replies_sent,
            active_auto_reply_templates=active_templates,
            messages_today=messages_today,
            messages_this_week=messages_this_week,
            top_contacts=top_contacts
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/auto-reply/templates", response_model=List[AutoReplyTemplateResponse])
async def get_auto_reply_templates(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get auto-reply templates
    """
    try:
        query = select(AutoReplyTemplate)
        
        conditions = []
        if account_id:
            conditions.append(AutoReplyTemplate.account_id == account_id)
        if is_active is not None:
            conditions.append(AutoReplyTemplate.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AutoReplyTemplate.priority))
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        # Parse trigger_keywords from JSON
        response_templates = []
        for template in templates:
            keywords = json.loads(template.trigger_keywords) if template.trigger_keywords else []
            response_templates.append(AutoReplyTemplateResponse(
                id=template.id,
                account_id=template.account_id,
                name=template.name,
                trigger_keywords=keywords,
                reply_message=template.reply_message,
                is_active=template.is_active,
                priority=template.priority,
                use_count=template.use_count,
                created_at=template.created_at,
                updated_at=template.updated_at
            ))
        
        return response_templates
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.post("/auto-reply/templates", response_model=dict)
async def create_auto_reply_template(
    template_data: AutoReplyTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new auto-reply template
    """
    try:
        # Verify account exists
        account_query = select(Account).where(Account.id == template_data.account_id)
        account_result = await db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Create template
        new_template = AutoReplyTemplate(
            account_id=template_data.account_id,
            name=template_data.name,
            trigger_keywords=json.dumps(template_data.trigger_keywords),
            reply_message=template_data.reply_message,
            is_active=template_data.is_active,
            priority=template_data.priority
        )
        
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=template_data.account_id,
            action="create_auto_reply_template",
            message=f"Created auto-reply template: {template_data.name}",
            level="info"
        )
        
        return {
            "success": True,
            "message": "Auto-reply template created successfully",
            "template_id": new_template.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/auto-reply/templates/{template_id}", response_model=dict)
async def update_auto_reply_template(
    template_id: int,
    template_data: AutoReplyTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update auto-reply template
    """
    try:
        query = select(AutoReplyTemplate).where(AutoReplyTemplate.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update fields
        if template_data.name is not None:
            template.name = template_data.name
        if template_data.trigger_keywords is not None:
            template.trigger_keywords = json.dumps(template_data.trigger_keywords)
        if template_data.reply_message is not None:
            template.reply_message = template_data.reply_message
        if template_data.is_active is not None:
            template.is_active = template_data.is_active
        if template_data.priority is not None:
            template.priority = template_data.priority
        
        template.updated_at = datetime.now()
        
        await db.commit()
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=template.account_id,
            action="update_auto_reply_template",
            message=f"Updated auto-reply template: {template.name}",
            level="info"
        )
        
        return {
            "success": True,
            "message": "Auto-reply template updated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/auto-reply/templates/{template_id}", response_model=dict)
async def delete_auto_reply_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete auto-reply template
    """
    try:
        query = select(AutoReplyTemplate).where(AutoReplyTemplate.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template_name = template.name
        account_id = template.account_id
        
        await db.delete(template)
        await db.commit()
        
        # Log activity
        await ActivityLogger.log_activity(
            db=db,
            account_id=account_id,
            action="delete_auto_reply_template",
            message=f"Deleted auto-reply template: {template_name}",
            level="warning"
        )
        
        return {
            "success": True,
            "message": "Auto-reply template deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


@router.post("/{message_id}/mark-read", response_model=dict)
async def mark_message_read(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a message as read
    """
    try:
        query = select(Message).where(Message.id == message_id)
        result = await db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message.is_read = True
        await db.commit()
        
        return {
            "success": True,
            "message": "Message marked as read"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark message as read: {str(e)}")


@router.post("/conversations/{conversation_id}/mark-all-read", response_model=dict)
async def mark_conversation_read(
    conversation_id: str,
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark all messages in a conversation as read
    """
    try:
        query = select(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.is_read == False,
                Message.is_sent_by_me == False
            )
        )
        
        if account_id:
            query = query.where(Message.account_id == account_id)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        count = 0
        for message in messages:
            message.is_read = True
            count += 1
        
        await db.commit()
        
        return {
            "success": True,
            "message": f"Marked {count} messages as read"
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark conversation as read: {str(e)}")
