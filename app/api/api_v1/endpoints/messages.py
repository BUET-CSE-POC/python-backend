from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.api import deps
from app.schemas.messages import Message, MessageCreate, MessageUpdate
from app.db.models.messages import Message as MessageModel

router = APIRouter()

#################################################################################################
#   CREATE MESSAGE
#################################################################################################
@router.post("/", response_model=Message)
async def create_message(*, db: Session = Depends(deps.get_db), message_in: MessageCreate):
    
    try:
        db_message = MessageModel(
            chat_id = message_in.chat_id,
            sender = message_in.sender,
            content = message_in.content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
#################################################################################################
#   UPDATE MESSAGE
#################################################################################################
@router.put("/{message_id}", response_model=Message)
async def update_message(*, db: Session = Depends(deps.get_db),message_id: uuid.UUID, message_in: MessageUpdate):
    
    try:
        db_message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        if not db_message:
            raise HTTPException(status_code=404, detail="Message not found")

        update_data = message_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_message, key, value)

        db.commit()
        db.refresh(db_message)
        return db_message
    except HTTPException as http_exc:
        raise http_exc
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
    