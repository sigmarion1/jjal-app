from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from database import Base


class Image(Base):
    __tablename__ = "image"

    name = Column(String, primary_key=True, index=True)
    url = Column(String)
    thumbnail_url = Column(String)
