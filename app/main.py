from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from typing import List
from datetime import date, timedelta
import random
import string

app = FastAPI()

# Create tables
database.create_tables()

def generate_unique_id(hsc_batch):
    letters = string.ascii_uppercase + string.digits
    unique_part = ''.join(random.choice(letters) for _ in range(6))
    return f"{unique_part}-{hsc_batch}"

@app.post("/reset-database")
def reset_database():
    database.reset_database()
    return {"message": "Database reset successfully"}

@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    unique_id = generate_unique_id(student.hsc_batch)
    db_student = models.Student(id=unique_id, **student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/", response_model=List[schemas.Student])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students

@app.get("/students/{student_id}", response_model=schemas.Student)
def get_student(student_id: str, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/students/batch/{kb_batch}", response_model=List[schemas.Student])
def get_students_by_batch(kb_batch: str, db: Session = Depends(database.get_db)):
    students = db.query(models.Student).filter(models.Student.kb_batch == kb_batch).all()
    if not students:
        raise HTTPException(status_code=404, detail="No students found for this batch")
    return students

@app.post("/attendance/", response_model=schemas.Attendance)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(database.get_db)):
    # Check if the student exists
    student = db.query(models.Student).filter(models.Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if an attendance record already exists for this student and date
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == attendance.student_id,
        models.Attendance.date == attendance.date
    ).first()
    
    if existing_attendance:
        # Update the existing attendance record
        existing_attendance.present = attendance.present
        db.commit()
        db.refresh(existing_attendance)
        return existing_attendance
    else:
        # Create a new attendance record
        db_attendance = models.Attendance(**attendance.dict())
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        return db_attendance

@app.post("/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(database.get_db)):
    # Check if the student exists
    student = db.query(models.Student).filter(models.Student.id == payment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.post("/exams/", response_model=schemas.Exam)
def create_exam(exam: schemas.ExamCreate, db: Session = Depends(database.get_db)):
    db_exam = models.Exam(**exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@app.post("/exam_results/", response_model=schemas.ExamResult)
def create_exam_result(exam_result: schemas.ExamResultCreate, db: Session = Depends(database.get_db)):
    # Check if the student exists
    student = db.query(models.Student).filter(models.Student.id == exam_result.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if the exam exists
    exam = db.query(models.Exam).filter(models.Exam.id == exam_result.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    db_exam_result = models.ExamResult(**exam_result.dict())
    db.add(db_exam_result)
    db.commit()
    db.refresh(db_exam_result)
    return db_exam_result

@app.get("/monthly_attendance/{student_id}/{year}/{month}", response_model=schemas.MonthlyAttendance)
def get_monthly_attendance(student_id: str, year: int, month: int, db: Session = Depends(database.get_db)):
    # Check if the student exists
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    attendances = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id,
        models.Attendance.date.between(date(year, month, 1), date(year, month + 1, 1) - timedelta(days=1))
    ).all()

    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.present)

    return schemas.MonthlyAttendance(
        student_id=student_id,
        month=month,
        year=year,
        total_days=total_days,
        present_days=present_days
    )

@app.get("/monthly_payment/{student_id}/{year}/{month}", response_model=schemas.MonthlyPayment)
def get_monthly_payment(student_id: str, year: int, month: int, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    payments = db.query(models.Payment).filter(
        models.Payment.student_id == student_id,
        models.Payment.date.between(date(year, month, 1), date(year, month + 1, 1) - timedelta(days=1))
    ).all()

    paid_amount = sum(payment.amount for payment in payments)
    due_amount = student.required_payment - paid_amount

    return schemas.MonthlyPayment(
        student_id=student_id,
        month=month,
        year=year,
        required_payment=student.required_payment,
        paid_amount=paid_amount,
        due_amount=due_amount
    )

@app.get("/monthly_exam_results/{student_id}/{year}/{month}", response_model=schemas.MonthlyExamResult)
def get_monthly_exam_results(student_id: str, year: int, month: int, db: Session = Depends(database.get_db)):
    exams = db.query(models.Exam).filter(
        models.Exam.date.between(date(year, month, 1), date(year, month + 1, 1) - timedelta(days=1))
    ).all()

    exam_results = db.query(models.ExamResult).filter(
        models.ExamResult.student_id == student_id,
        models.ExamResult.exam_id.in_([exam.id for exam in exams])
    ).all()

    return schemas.MonthlyExamResult(
        student_id=student_id,
        month=month,
        year=year,
        exams=exams,
        results=exam_results
    )

@app.delete("/students/{student_id}")
def delete_student(student_id: str, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@app.delete("/attendance/{student_id}/{date}")
def delete_attendance(student_id: str, date: date, db: Session = Depends(database.get_db)):
    attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id,
        models.Attendance.date == date
    ).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    db.delete(attendance)
    db.commit()
    return {"message": "Attendance record deleted successfully"}

@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(database.get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    db.delete(payment)
    db.commit()
    return {"message": "Payment record deleted successfully"}

@app.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(database.get_db)):
    exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    db.delete(exam)
    db.commit()
    return {"message": "Exam deleted successfully"}

@app.delete("/exam_results/{result_id}")
def delete_exam_result(result_id: int, db: Session = Depends(database.get_db)):
    result = db.query(models.ExamResult).filter(models.ExamResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Exam result not found")
    db.delete(result)
    db.commit()
    return {"message": "Exam result deleted successfully"}

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: str, student: schemas.StudentCreate, db: Session = Depends(database.get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student
