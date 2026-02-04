from sqlalchemy import (
    Column,
    Integer,
    String,
    Index,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_serializer import SerializerMixin


class Base(DeclarativeBase, SerializerMixin):
    pass


class IntraServiceUser(Base):
    __tablename__ = "user_intraservice"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    companyid = Column(Integer, ForeignKey("company_intraservice.id"), nullable=False)
    email = Column(String(250))
    login = Column(String(100))
    mobilephone = Column(String(100))
    phone = Column(String(100))
    position = Column(String(100))
    isarchive = Column(Boolean)

    __table_args__ = (Index("user_name_index", "name"),)

    def __repr__(self):
        return f"({self.id}) {self.name}"

    def dump_to_json(self):
        item = {}
        for column in self.__table__.columns:
            item[column.name] = str(getattr(self, column.name))
        return item


class IntraServiceCompany(Base):
    __tablename__ = "company_intraservice"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    fullname = Column(String(1250), nullable=False)
    isarchive = Column(Boolean)
    is_active = Column(Boolean)
    typeid = Column(Integer)

    __table_args__ = (Index("company_name_index", "name"),)

    def __repr__(self):
        return f"({self.id}) {self.name}"

    def dump_to_json(self):
        item = {}
        for column in self.__table__.columns:
            item[column.name] = str(getattr(self, column.name))
        return item
