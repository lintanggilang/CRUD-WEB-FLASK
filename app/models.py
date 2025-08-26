from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # 'admin' or 'user'
    
    permissions = relationship("Permission", back_populates="user")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city = Column(String)
    
    user = relationship("User", back_populates="permissions")

class DataTable(Base):
    __tablename__ = "data_table"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    data_field1 = Column(String)
    data_field2 = Column(String)