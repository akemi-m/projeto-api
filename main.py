from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from datetime import datetime

app = FastAPI()

engine = create_engine('postgresql://postgres:root@localhost:900/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    
class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    birthday = Column(DateTime)
    salary = Column(Float(10, 2))
    department = Column(String(50))

    jobid = Column(Integer, ForeignKey('job.id', ondelete='SET NULL'))

    job = relationship('Job')

class JobHistory(Base):
    __tablename__ = 'jobhistory'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    salary = Column(Float(10, 2))
    job = Column(String(100))

    employeeid = Column(Integer, ForeignKey('employee.id', ondelete='CASCADE'))
    
    employee = relationship('Employee')

# migration
Base.metadata.create_all(bind=engine)

# 1. GET /api/Entidade1 : busca todos os registros
@app.get("/api/job")
def get_job():
    try:
        job_list = session.query(Job).all()
        if not job_list:
            return JSONResponse(content={'error': 'Job not found'}, status_code=404)

        job_list_response = []
        for job in job_list:
            employees = session.query(Employee).filter_by(jobid=job.id).all()

            employee_data = []
            for emp in employees:
                employee_data.append({
                    'id': emp.id,
                    'name': emp.name,
                    'birthday': str(emp.birthday),
                    'salary': emp.salary,
                    'department': emp.department
                })

            all_data = {
                'id': job.id,
                'name': job.name,
                'description': job.description,
                'employees': employee_data
            }

            job_list_response.append(all_data)

        return JSONResponse(content=job_list_response, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 2. Post /api/Entidade1 : cadastra um objeto
@app.post("/api/job")
def create_job(name: str, description: str):
    try:
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if not description:
            return JSONResponse(content={'error': 'Description is required'}, status_code=400)
    
        job = Job(name=name, description=description)
        session.add(job)
        session.commit()
        return JSONResponse(content={'id': job.id, 'description': job.description}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 3. GET /api/Entidade1/{Entidade1ID} :  busca um único objeto pelo ID e seus dependentes
@app.get("/api/job/{job_id}")
def get_all_by_job(job_id: int):
    try:
        job = session.query(Job).filter_by(id=job_id).first()
        if not job:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)

        employees = session.query(Employee).filter_by(jobid=job_id).all()
        if not employees:
            return JSONResponse(content={'error': 'No employee found'}, status_code=404)
    
        job_list = []
        for employee in employees:
            jobhistory = session.query(JobHistory).filter_by(employeeid=employee.id).first()

            jobhistory_data = None
            if jobhistory:
                jobhistory_data = {
                    'id': jobhistory.id,
                    'title': jobhistory.title,
                    'startdate': str(jobhistory.startdate),
                    'enddate': str(jobhistory.enddate),
                    'salary': str(jobhistory.salary),
                    'job': jobhistory.job
                }
        
            employee_data = None
            if employee:
                employee_data = {
                    'id': employee.id,
                    'name': employee.name,
                    'birthday': str(employee.birthday),
                    'salary': str(employee.salary),
                    'job': str(employee.job)
                }

            all_data = {
                'id': job.id,
                'name': job.name,
                'description': job.description,
                'employee': str(employee_data),
                'jobhistory': str(jobhistory_data),
            }

            job_list.append(all_data)

        return JSONResponse(content=job_list, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 4. PUT /api/Entidade1/{Entidade1ID} : atualiza um objeto
@app.put("/api/job/{job_id}")
def put_job(name: str, description: str, job_id: int):
    try:
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if not description:
            return JSONResponse(content={'error': 'Description is required'}, status_code=400)
        if not job_id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    
        job = session.query(Job).filter_by(id=job_id).first()
        if not job:
            return JSONResponse(content={'error': 'Job not found'}, status_code=404)
        
        job.name = name
        job.description = description
        session.commit()
        return JSONResponse(content={'id': job.id, 'name': job.name, 'description': job.description}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 5. DELETE /api/Entidade1/{Entidade1ID} : deleta um objeto
# OK
@app.delete("/jobs")
def delete_job(id: int):
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)

        job = session.query(Job).filter_by(id=id).first()
        if not job:
            return JSONResponse(content={'error': 'Job not found'}, status_code=404)
        
        session.delete(job)
        session.commit()
        return JSONResponse(content={'message': 'Job deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 6. GET /api/Entidade2 : busca todos os registros
@app.get("/api/employee")
def get_all_employees():
    try:
        employees = session.query(Employee).all()
        if not employees:
            return JSONResponse(content={'error': 'No employees found'}, status_code=404)

        employee_list = []
        for employee in employees:
            job = session.query(Job).filter_by(id=employee.jobid).first()

            job_data = None
            if job:
                job_data = {
                    'id': job.id,
                    'name': job.name,
                    'description': job.description
                }

            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'birthday': str(employee.birthday),
                'salary': str(employee.salary),
                'department': employee.department,
                'job': job_data
            }

            employee_list.append(employee_data)

        return JSONResponse(content=employee_list, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

    
# 7. Post /api/Entidade2 : cadastra um objeto
@app.post("/api/employees")
def create_employee(name: str, salary: float, department: str, jobid: int):
    try:
        if not jobid:
            return JSONResponse(content={'error': 'JobID is required'}, status_code=400)
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if salary is None:
            return JSONResponse(content={'error': 'Salary is required'}, status_code=400)
        
        find_job = session.query(Job).filter_by(id=jobid).first()
        if not find_job:
            return JSONResponse(content={'error': 'Job not found'}, status_code=404)
    
        employee = Employee(name=name, birthday=datetime.now(), salary=salary, department=department, jobid=jobid)
        session.add(employee)
        session.commit()
        return JSONResponse(content={'id': employee.id, 'birthday': str(employee.birthday), 'salary': str(employee.salary), 'department': employee.department, 'jobid': employee.jobid}, status_code=201)
    
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 8. GET /api/Entidade2/{Entidade2ID} :  busca um único objeto pelo ID e seus dependentes*
@app.get("/api/employee/{employee_id}")
def get_employees(employee_id: int):
    try:
        employee = session.query(Employee).filter_by(id=employee_id).first()
        if not employee:
            return JSONResponse(content={'error': 'Employee not found'}, status_code=404)

        jobhistories = session.query(JobHistory).filter_by(employeeid=employee_id).all()
        if not jobhistories:
            return JSONResponse(content={'error': 'No job history found'}, status_code=404)
    
        employee_list = []
        for jobhistory in jobhistories:

            jobhistory_data = None
            if jobhistory:
                jobhistory_data = {
                    'id': jobhistory.id,
                    'title': jobhistory.title,
                    'startdate': str(jobhistory.startdate),
                    'enddate': str(jobhistory.enddate),
                    'salary': str(jobhistory.salary),
                    'job': str(jobhistory.job)
                }

            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'birthday': str(employee.birthday),
                'salary': str(employee.salary),
                'department': employee.department,

                'job_history': jobhistory_data
            }

            employee_list.append(employee_data)

        return JSONResponse(content=employee_list, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 9. PUT /api/Entidade2/{Entidade2ID} : atualiza um objeto
@app.put("/employee/{employee_id}")
def put_post(name: str, salary: float, department: str, employee_id: int):
    try:
        if not name:
            return JSONResponse(content={'error': 'Name is required'}, status_code=400)
        if salary is None:
            return JSONResponse(content={'error': 'Salary is required'}, status_code=400)
        if not department:
            return JSONResponse(content={'error': 'Department is required'}, status_code=400)
        if not employee_id:
            return JSONResponse(content={'error': 'EmployeeID is required'}, status_code=400)

        employee = session.query(Employee).filter_by(id=employee_id).first()
        if not employee:
            return JSONResponse(content={'error': 'Employee not found'}, status_code=404)
        
        employee.name = name
        employee.salary = salary
        employee.department = department
        session.commit()
        return JSONResponse(content={'id': employee.id, 'name': employee.name, 'birthday': str(employee.birthday),'salary': str(employee.salary), 'department': employee.department}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 10. DELETE /api/Entidade2/{Entidade2ID} : deleta um objeto
@app.delete("/employee/{employee_id}")
def delete_employee(employee_id: int):
    try:
        if not employee_id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)

        employee = session.query(Employee).filter_by(id=employee_id).first()
        if not employee:
            return JSONResponse(content={'error': 'Employee not found'}, status_code=404)
        
        session.delete(employee)
        session.commit()
        return JSONResponse(content={'message': 'Employee deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 11. GET /api/Entidade3 : busca todos os registros
@app.get("/api/jobhistories")
def get_all_jobhistories():
    try:
        jobhistory_list = session.query(JobHistory).all()
        if not jobhistory_list:
            return JSONResponse(content={'error': 'No job history found'}, status_code=404)
        
        jobhistories = [{'id': j.id, 'title': j.title, 'startdate': str(j.startdate), 'enddate': str(j.enddate), 'salary': str(j.salary), 'job': j.job} for j in jobhistory_list]
        return JSONResponse(content=jobhistories, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 12. Post /api/Entidade3 : cadastra um objeto
@app.post("/api/jobhistories")
def create_jobhistory(title: str, salary: float, job: str, employeeid: int):
    try:
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if not salary:
            return JSONResponse(content={'error': 'Salary is required'}, status_code=400)
        if not job:
            return JSONResponse(content={'error': 'Job is required'}, status_code=400)
        if not employeeid:
            return JSONResponse(content={'error': 'EmployeeID is required'}, status_code=400)
        
        verify_employee = session.query(Employee).filter_by(id=employeeid).first()
        if not verify_employee:
            return JSONResponse(content={'error': 'Employee not found'}, status_code=404)

        jobhistory = JobHistory(title=title, startdate=datetime.now(), enddate=datetime.now(), salary=salary, job=job, employeeid=employeeid)
        session.add(jobhistory)
        session.commit()
        return JSONResponse(content={'id': jobhistory.id, 'title': jobhistory.title, 'startdate': str(jobhistory.startdate), 'enddate': str(jobhistory.enddate), 'salary': str(jobhistory.salary), 'job': jobhistory.job}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
# 13. GET /api/Entidade3/{Entidade3ID} : busca um único objeto pelo ID
@app.get("/api/JobHistory/{jobhistory_id}")
def get_jobhistory(jobhistory_id: int):
    try:
        jobhistory = session.query(JobHistory).filter_by(id=jobhistory_id).first()
        if not jobhistory:
            return JSONResponse(content={'error': 'Job history not found'}, status_code=404)

        data = {
            'id': jobhistory.id,
            'title': jobhistory.title,
            'startdate': str(jobhistory.startdate),
            'enddate': str(jobhistory.enddate),
            'salary': str(jobhistory.salary),
            'job': jobhistory.job,
            'employeeid': jobhistory.employeeid
        }

        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 14. PUT /api/Entidade3/{Entidade3ID} : atualiza um objeto
@app.put("/api/jobhistories/{jobhistory_id}")
def put_jobhistory(title: str, salary: float, job: str, jobhistory_id: int):
    try:
        if not jobhistory_id:
            return JSONResponse(content={'error': 'JobhistoryID is required'}, status_code=400)
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if salary is None:
            return JSONResponse(content={'error': 'Salary is required'}, status_code=400)
        if not job:
            return JSONResponse(content={'error': 'Job is required'}, status_code=400)
    
        jobhistory = session.query(JobHistory).filter_by(id=jobhistory_id).first()
        if not jobhistory:
            return JSONResponse(content={'error': 'Job History not found'}, status_code=404)
        
        jobhistory.title = title
        jobhistory.startdate = created=datetime.now(),
        jobhistory.enddate = created=datetime.now(),
        jobhistory.salary = salary,
        jobhistory.job = job
        session.commit()
        return JSONResponse(content={'id': jobhistory.id, 'title': jobhistory.title, 'startdate': str(jobhistory.startdate), 'enddate': str(jobhistory.enddate), 'salary': str(jobhistory.salary), 'job': jobhistory.job}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# 15. DELETE /api/Entidade3/{Entidade3ID} : deleta um objeto
@app.delete("/jobhistory/{jobhistory_id}")
def delete_jobhistory(jobhistory_id: int):
    try:
        if not jobhistory_id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)

        jobhistory = session.query(JobHistory).filter_by(id=jobhistory_id).first()
        if not jobhistory:
            return JSONResponse(content={'error': 'Job History not found'}, status_code=404)
        
        session.delete(jobhistory)
        session.commit()
        return JSONResponse(content={'message': 'Job History deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    