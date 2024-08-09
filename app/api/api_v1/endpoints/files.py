from typing import List
import uuid
from fastapi import BackgroundTasks, APIRouter, Depends, HTTPException,Query,UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.core.config import settings
from app.api import deps
from app.db.models.files import File as FileModel
from app.db.models.users import User as UserModel
from app.schemas.files import File, FileUpdate
from app.helpers.supabase_bucket_insert import upload_file_to_supabase, delete_file_from_supabase
from app.helpers.qdrant_functions import delete_points_by_uuid

from app.background.unstructured_parse import process_pdf
router = APIRouter()

#################################################################################################
#   GET All Files with Pagination
#################################################################################################
@router.get("/", response_model=List[File])
async def get_all_files(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Maximum number of records to return")
):
    try:
        files = db.query(FileModel).offset(skip).limit(limit).all()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))

#################################################################################################
#   GET File BY ID
#################################################################################################
@router.get("/{file_id}", response_model=File)
async def get_file_by_id(file_id: uuid.UUID, db: Session = Depends(deps.get_db)):
    
    try:
        db_file = db.query(FileModel).filter(FileModel.file_id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        return db_file
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))


#################################################################################################
#   Upload a File
#################################################################################################
@router.post("/", response_model=File)
async def upload_file(
    *,
    db: Session = Depends(deps.get_db),
    uploader_id: uuid.UUID,
    filename: str,
    file: UploadFile = FastAPIFile(...),
    background_tasks: BackgroundTasks
):
    # Validate file extension
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    db_user = db.query(UserModel).filter(UserModel.id == uploader_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        file_bytes = await file.read()

        public_url = upload_file_to_supabase(file_bytes, filename, str(uploader_id))

        # Add to the database
        db_file = FileModel(
            uploader_id=uploader_id,
            file_name=filename,
            file_url=public_url,
            status="parsing..."
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        background_tasks.add_task(process_pdf, file_bytes, str(db_file.file_id), str(public_url))

        return db_file

    except ValidationError as e:
        raise HTTPException(status_code=422, detail="Invalid input: " + str(e))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    

#################################################################################################
#   Update Informations of a file
#################################################################################################
@router.put("/{file_id}", response_model=File)
async def update_file(
    *,
    db: Session = Depends(deps.get_db),
    file_id: uuid.UUID,
    file_in: FileUpdate
):
    try:
        db_file = db.query(FileModel).filter(FileModel.file_id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")

        update_data = file_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_file, key, value)

        db.commit()
        db.refresh(db_file)
        
        return db_file
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
    
#################################################################################################
#   DELETE a file and all its vector points
#################################################################################################
@router.delete("/{file_id}", response_model=dict)
async def delete_file_by_id(*, db: Session = Depends(deps.get_db), file_id: uuid.UUID):
    try:
        db_file = db.query(FileModel).filter(FileModel.file_id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = db_file.file_url.split("/")[-1]

        # Delete from Supabase
        supabase_delete_success = delete_file_from_supabase(file_path)
        if not supabase_delete_success:
            raise HTTPException(status_code=500, detail="Failed to delete file from Supabase")

        db.delete(db_file)
        db.commit()
        
        try:
            success = delete_points_by_uuid(str(settings.COLLECTION_NAME_RISK_MANAGEMENT), str(file_id))
            
            if success:
                return {"detail": f"File with ID {file_id} deleted from DB & vectorDB successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete File from vectorDB")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while deleting from vectorDB: {str(e)}")
        
    except HTTPException as http_exc:
        db.rollback()
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))