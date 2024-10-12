
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

### Attendance
- `POST /attendance/`: Create or update attendance record
- `GET /monthly_attendance/{student_id}/{year}/{month}`: Get monthly attendance for a student
- `DELETE /attendance/{student_id}/{date}`: Delete an attendance record

### Payments
- `POST /payments/`: Create a payment record
- `GET /monthly_payment/{student_id}/{year}/{month}`: Get monthly payment status for a student
- `DELETE /payments/{payment_id}`: Delete a payment record

### Exams
- `POST /exams/`: Create a new exam
- `DELETE /exams/{exam_id}`: Delete an exam

### Exam Results
- `POST /exam_results/`: Create an exam result
- `GET /monthly_exam_results/{student_id}/{year}/{month}`: Get monthly exam results for a student
- `DELETE /exam_results/{result_id}`: Delete an exam result

### Database Management
- `POST /reset-database`: Reset the entire database (use with caution)

## Features

- Custom unique ID generation for students
- Attendance tracking with duplicate prevention
- Payment management
- Exam creation and result recording
- Monthly reports for attendance, payments, and exam results
- Student management by KB batch

## Testing

Use the provided `http-requests.http` file with REST Client in Visual Studio Code or similar tools to test the API endpoints.

## Note

This is a backend system. For production use, consider implementing authentication, authorization, and connecting to a more robust database system.