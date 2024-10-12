from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from . import models, schemas, database
from typing import List
from datetime import date, timedelta
import random
import string
from fastapi.encoders import jsonable_encoder
import logging
from collections import defaultdict

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    student = db.query(models.Student).filter(models.Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == attendance.student_id,
        models.Attendance.date == attendance.date
    ).first()
    
    if existing_attendance:
        existing_attendance.present = attendance.present
        db.commit()
        db.refresh(existing_attendance)
        return existing_attendance
    else:
        db_attendance = models.Attendance(**attendance.dict())
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        return db_attendance

@app.post("/payments/", response_model=schemas.PaymentHistory)
def create_payment(payment: schemas.PaymentHistoryCreate, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(models.Student.id == payment.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    due = payment.payment - payment.paid
    db_payment = models.PaymentHistory(**payment.dict(), due=due)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.get("/payments/student/{student_id}", response_model=schemas.StudentPaymentHistory)
def get_student_payment_history(student_id: str, db: Session = Depends(database.get_db)):
    try:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        payments = db.query(models.PaymentHistory).filter(models.PaymentHistory.student_id == student_id).all()
        pydantic_payments = [schemas.PaymentHistory.from_orm(payment) for payment in payments]
        return schemas.StudentPaymentHistory(student_id=student_id, payments=pydantic_payments)
    except Exception as e:
        logger.error(f"Error in get_student_payment_history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/payments/year/{year}", response_model=List[schemas.PaymentHistory])
def get_yearly_payments(year: int, db: Session = Depends(database.get_db)):
    try:
        payments = db.query(models.PaymentHistory).filter(extract('year', models.PaymentHistory.date) == year).all()
        if not payments:
            raise HTTPException(status_code=404, detail="No payments found for this year")
        return [schemas.PaymentHistory.from_orm(payment) for payment in payments]
    except Exception as e:
        logger.error(f"Error in get_yearly_payments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/payments/month/{year}/{month}", response_model=schemas.MonthlyPaymentSummary)
def get_monthly_payments(year: int, month: int, db: Session = Depends(database.get_db)):
    try:
        payments = db.query(models.PaymentHistory).filter(
            extract('year', models.PaymentHistory.date) == year,
            extract('month', models.PaymentHistory.date) == month
        ).all()
        if not payments:
            raise HTTPException(status_code=404, detail="No payments found for this month")
        pydantic_payments = [schemas.PaymentHistory.from_orm(payment) for payment in payments]
        return schemas.MonthlyPaymentSummary(year=year, month=month, payments=pydantic_payments)
    except Exception as e:
        logger.error(f"Error in get_monthly_payments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/payments/due", response_model=schemas.DuePaymentSummary)
def get_due_payments(db: Session = Depends(database.get_db)):
    try:
        payments = db.query(models.PaymentHistory).filter(models.PaymentHistory.due > 0).all()
        if not payments:
            raise HTTPException(status_code=404, detail="No due payments found")
        
        pydantic_payments = [schemas.PaymentHistory.from_orm(payment) for payment in payments]
        return schemas.DuePaymentSummary(payments=pydantic_payments)
    except Exception as e:
        logger.error(f"Error in get_due_payments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/monthly_attendance/{student_id}/{year}/{month}", response_model=schemas.MonthlyAttendance)
def get_monthly_attendance(student_id: str, year: int, month: int, db: Session = Depends(database.get_db)):
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

    payments = db.query(models.PaymentHistory).filter(
        models.PaymentHistory.student_id == student_id,
        extract('year', models.PaymentHistory.date) == year,
        extract('month', models.PaymentHistory.date) == month
    ).all()

    total_payment = sum(payment.payment for payment in payments)
    total_paid = sum(payment.paid for payment in payments)
    total_due = sum(payment.due for payment in payments)

    return schemas.MonthlyPayment(
        student_id=student_id,
        month=month,
        year=year,
        total_payment=total_payment,
        total_paid=total_paid,
        total_due=total_due
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

@app.delete("/payments/{student_id}/{date}")
def delete_payment(student_id: str, date: date, db: Session = Depends(database.get_db)):
    payment = db.query(models.PaymentHistory).filter(
        models.PaymentHistory.student_id == student_id,
        models.PaymentHistory.date == date
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    db.delete(payment)
    db.commit()
    return {"message": "Payment record deleted successfully"}

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

@app.get("/students/{student_id}/yearly_dues", response_model=dict[int, float])
def get_student_yearly_dues(student_id: str, db: Session = Depends(database.get_db)):
    try:
        student = db.query(models.Student).filter(models.Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        yearly_dues = db.query(
            extract('year', models.PaymentHistory.date).label('year'),
            func.sum(models.PaymentHistory.due).label('total_due')
        ).filter(
            models.PaymentHistory.student_id == student_id
        ).group_by(
            extract('year', models.PaymentHistory.date)
        ).all()
        
        dues_dict = {year: float(total_due) for year, total_due in yearly_dues}
        return dues_dict
    except Exception as e:
        logger.error(f"Error in get_student_yearly_dues: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
