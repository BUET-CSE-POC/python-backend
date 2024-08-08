import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class File(Base):
    __tablename__ = 'fileinfo'

    file_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_url = Column(String, nullable=False)
    status = Column(String, nullable=True, default='parsing...')
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    uploader = relationship('User', back_populates='files')
