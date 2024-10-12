## Setup and Running

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Students
- `POST /students/`: Create a new student
- `GET /students/`: Get all students
- `GET /students/{student_id}`: Get details of a specific student
- `GET /students/batch/{kb_batch}`: Get list of students by KB batch
- `PUT /students/{student_id}`: Update student information
- `DELETE /students/{student_id}`: Delete a student
- `GET /students/{student_id}/yearly_dues`: Get yearly dues for a student

### Attendance
- `POST /attendance/`: Create or update attendance record
- `GET /monthly_attendance/{student_id}/{year}/{month}`: Get monthly attendance for a student
- `DELETE /attendance/{student_id}/{date}`: Delete an attendance record

### Payments
- `POST /payments/`: Create a payment record
- `GET /payments/student/{student_id}`: Get payment history for a student
- `GET /payments/year/{year}`: Get all payments for a specific year
- `GET /payments/month/{year}/{month}`: Get all payments for a specific month
- `GET /payments/due`: Get all due payments
- `GET /monthly_payment/{student_id}/{year}/{month}`: Get monthly payment status for a student
- `DELETE /payments/{student_id}/{date}`: Delete a payment record

### Exams
- `POST /exams/`: Create an exam record
- `GET /exams/student/{student_id}`: Get exam history for a student
- `GET /exams/year/{year}`: Get all exams for a specific year
- `GET /exams/month/{year}/{month}`: Get all exams for a specific month
- `GET /exams/percentage/{student_id}/{year}/{month}`: Get monthly exam percentage for a student

### Database Management
- `POST /reset-database`: Reset the entire database (use with caution)

## Features

- Custom unique ID generation for students
- Attendance tracking with duplicate prevention
- Payment management with due calculation
- Exam record management and performance tracking
- Monthly reports for attendance, payments, and exams
- Student management by KB batch
- Yearly dues summary for students

## Testing

Use the provided `http-requests.http` file with REST Client in Visual Studio Code or similar tools to test the API endpoints.

## Note

This is a backend system. For production use, consider implementing authentication, authorization, and connecting to a more robust database system.