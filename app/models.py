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
    total_subjects = Column(Integer)
    required_payment = Column(Float)

    attendances = relationship("Attendance", back_populates="student")
    payments = relationship("Payment", back_populates="student")
    exam_results = relationship("ExamResult", back_populates="student")

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    present = Column(Boolean, nullable=False)

    student = relationship("Student", back_populates="attendances")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)

    student = relationship("Student", back_populates="payments")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    total_marks = Column(Integer, nullable=False)

    results = relationship("ExamResult", back_populates="exam")

class ExamResult(Base):
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    obtained_marks = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="exam_results")
    exam = relationship("Exam", back_populates="results")
