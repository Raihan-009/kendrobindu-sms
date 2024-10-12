from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    hsc_batch = Column(String, nullable=False)
    kb_batch = Column(String)
    phone = Column(String)
    address = Column(String)

    attendances = relationship("Attendance", back_populates="student")
    payment_history = relationship("PaymentHistory", back_populates="student")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    present = Column(Boolean, nullable=False)

    student = relationship("Student", back_populates="attendances")

class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    payment = Column(Float, nullable=False)
    paid = Column(Float, nullable=False)
    due = Column(Float, nullable=False)
    total_subjects = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="payment_history")
