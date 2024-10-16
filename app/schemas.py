from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class StudentBase(BaseModel):
    name: str
    hsc_batch: str
    kb_batch: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class PaymentHistoryBase(BaseModel):
    date: date
    payment: float
    paid: float
    total_subjects: int

class PaymentHistoryCreate(PaymentHistoryBase):
    student_id: str

class PaymentHistory(PaymentHistoryBase):
    id: int
    student_id: str
    due: float

    class Config:
        from_attributes = True  # This replaces orm_mode = True

class ExamHistoryBase(BaseModel):
    date: date
    subject_name: str
    total_marks: float
    obtained_marks: float

class ExamHistoryCreate(ExamHistoryBase):
    student_id: str

class ExamHistory(ExamHistoryBase):
    id: int
    student_id: str

    class Config:
        from_attributes = True

class Student(StudentBase):
    id: str
    payment_history: List[PaymentHistory] = []
    exam_history: List[ExamHistory] = []

    class Config:
        from_attributes = True  # This replaces orm_mode = True

class AttendanceCreate(BaseModel):
    student_id: str
    date: date
    present: bool

class Attendance(AttendanceCreate):
    id: int

    class Config:
        from_attributes = True  # This replaces orm_mode = True

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
    total_payment: float
    total_paid: float
    total_due: float

class StudentPaymentHistory(BaseModel):
    student_id: str
    payments: List[PaymentHistory]

class MonthlyPaymentSummary(BaseModel):
    year: int
    month: int
    payments: List[PaymentHistory]

class DuePaymentSummary(BaseModel):
    payments: List[PaymentHistory]

class StudentExamHistory(BaseModel):
    student_id: str
    exams: List[ExamHistory]

class MonthlyExamSummary(BaseModel):
    year: int
    month: int
    exams: List[ExamHistory]

class YearlyExamSummary(BaseModel):
    year: int
    exams: List[ExamHistory]

class MonthlyExamPercentage(BaseModel):
    student_id: str
    year: int
    month: int
    percentage: float
