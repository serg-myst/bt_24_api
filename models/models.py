from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, UniqueConstraint, Index, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_serializer import SerializerMixin


# Base = declarative_base()

class Base(DeclarativeBase, SerializerMixin):
    pass


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    second_name = Column(String(100))
    work_position = Column(String(500))
    birthday = Column(DateTime(timezone=False), nullable=True)
    date_register = Column(DateTime(timezone=True))
    phone = Column(String(50))
    email = Column(String(50))
    photo = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    department_id = Column(Integer, ForeignKey('department.id'))
    user_department = relationship('Department', backref='user', uselist=True)

    __table_args__ = (
        Index('user_name_index', 'name'),
    )

    def __repr__(self):
        return f'({self.id}) {self.name} {self.last_name}'

    def dump_to_json(self):
        item = {}
        for column in self.__table__.columns:
            item[column.name] = str(getattr(self, column.name))
        return item


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    parent = Column(Integer, ForeignKey('department.id'), nullable=True)
    sort = Column(Integer)
    is_active = Column(Boolean)
    dep_head = relationship('DepartmentHead', backref='head', uselist=False)

    __table_args__ = (
        UniqueConstraint('name'),
        Index('department_name_index', 'name'),
    )

    def __repr__(self):
        return f'({self.id}) {self.name}'


class DepartmentHead(Base):
    __tablename__ = 'department_head'
    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey('department.id'), unique=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    # department = relationship("Department", uselist=False)
    user = relationship("User", uselist=False, backref='users')

    __table_args__ = (
        Index('department_id_index', 'department_id'),
    )

    def __repr__(self):
        return f'({self.department_id}) {self.user_id}'
