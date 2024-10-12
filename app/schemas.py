from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class StudentBase(BaseModel):
    name: str
    hsc_batch: str
    kb_batch: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    total_subjects: Optional[int] = None
    required_payment: Optional[float] = None

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: str

    class Config:
        orm_mode = True

class AttendanceCreate(BaseModel):
    student_id: str
    date: date
    present: bool

class Attendance(AttendanceCreate):
    id: int

    class Config:
        orm_mode = True

class PaymentCreate(BaseModel):
    student_id: str
    date: date
    amount: float

class Payment(PaymentCreate):
    id: int

    class Config:
        orm_mode = True

class ExamCreate(BaseModel):
    date: date
    total_marks: int

class Exam(ExamCreate):
    id: int

    class Config:
        orm_mode = True

class ExamResultCreate(BaseModel):
    student_id: str
    exam_id: int
    obtained_marks: int

class ExamResult(ExamResultCreate):
    id: int

    class Config:
        orm_mode = True

class MonthlyAttendance(BaseModel):
    student_id: str
    month: int
    year: int
    total_days: int
    present_days: int

class MonthlyPayment(BaseModel):
    student_id: str
    month: int
    year: int
    required_payment: float
    paid_amount: float
    due_amount: float

class MonthlyExamResult(BaseModel):
    student_id: str
    month: int
    year: int
    exams: List[Exam]
    results: List[ExamResult]
