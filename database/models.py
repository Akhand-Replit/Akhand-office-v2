from sqlalchemy import text

class EmployeeModel:
    """Employee data operations"""
    
    @staticmethod
    def get_all_employees(conn):
        """Get all employees from the database."""
        result = conn.execute(text('''
        SELECT id, username, full_name, profile_pic_url, is_active 
        FROM employees
        WHERE id != 1
        ORDER BY full_name
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_active_employees(conn):
        """Get all active employees."""
        result = conn.execute(text('''
        SELECT id, full_name FROM employees 
        WHERE is_active = TRUE AND id != 1
        ORDER BY full_name
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_employee_by_id(conn, employee_id):
        """Get employee data by ID."""
        result = conn.execute(text('''
        SELECT username, full_name, profile_pic_url
        FROM employees
        WHERE id = :employee_id
        '''), {'employee_id': employee_id})
        return result.fetchone()
    
    @staticmethod
    def add_employee(conn, username, password, full_name, profile_pic_url):
        """Add a new employee to the database."""
        default_pic = "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        
        conn.execute(text('''
        INSERT INTO employees (username, password, full_name, profile_pic_url, is_active)
        VALUES (:username, :password, :full_name, :profile_pic_url, TRUE)
        '''), {
            'username': username,
            'password': password,
            'full_name': full_name,
            'profile_pic_url': profile_pic_url if profile_pic_url else default_pic
        })
        conn.commit()
    
    @staticmethod
    def update_employee_status(conn, employee_id, is_active):
        """Activate or deactivate an employee."""
        conn.execute(text('UPDATE employees SET is_active = :is_active WHERE id = :id'), 
                    {'id': employee_id, 'is_active': is_active})
        conn.commit()
    
    @staticmethod
    def reset_password(conn, employee_id, new_password):
        """Reset an employee's password."""
        conn.execute(text('UPDATE employees SET password = :password WHERE id = :id'), 
                    {'id': employee_id, 'password': new_password})
        conn.commit()
    
    @staticmethod
    def update_profile(conn, employee_id, full_name, profile_pic_url):
        """Update employee profile information."""
        conn.execute(text('''
        UPDATE employees
        SET full_name = :full_name, profile_pic_url = :profile_pic_url
        WHERE id = :employee_id
        '''), {
            'full_name': full_name,
            'profile_pic_url': profile_pic_url,
            'employee_id': employee_id
        })
        conn.commit()
    
    @staticmethod
    def update_password(conn, employee_id, new_password):
        """Update employee password."""
        conn.execute(text('''
        UPDATE employees
        SET password = :new_password
        WHERE id = :employee_id
        '''), {'new_password': new_password, 'employee_id': employee_id})
        conn.commit()
    
    @staticmethod
    def verify_password(conn, employee_id, current_password):
        """Verify employee's current password."""
        result = conn.execute(text('''
        SELECT COUNT(*)
        FROM employees
        WHERE id = :employee_id AND password = :current_password
        '''), {'employee_id': employee_id, 'current_password': current_password})
        return result.fetchone()[0] > 0


class ReportModel:
    """Daily report data operations"""
    
    @staticmethod
    def get_employee_reports(conn, employee_id, start_date, end_date):
        """Get reports for a specific employee within a date range."""
        result = conn.execute(text('''
        SELECT id, report_date, report_text
        FROM daily_reports
        WHERE employee_id = :employee_id
        AND report_date BETWEEN :start_date AND :end_date
        ORDER BY report_date DESC
        '''), {'employee_id': employee_id, 'start_date': start_date, 'end_date': end_date})
        return result.fetchall()
    
    @staticmethod
    def get_all_reports(conn, start_date, end_date, employee_name=None):
        """Get all reports with optional employee filter."""
        query = '''
        SELECT e.full_name, dr.report_date, dr.report_text, dr.id, e.id as employee_id
        FROM daily_reports dr
        JOIN employees e ON dr.employee_id = e.id
        WHERE dr.report_date BETWEEN :start_date AND :end_date
        '''
        
        params = {'start_date': start_date, 'end_date': end_date}
        
        if employee_name and employee_name != "All Employees":
            query += ' AND e.full_name = :employee_name'
            params['employee_name'] = employee_name
        
        query += ' ORDER BY dr.report_date DESC, e.full_name'
        
        result = conn.execute(text(query), params)
        return result.fetchall()
    
    @staticmethod
    def add_report(conn, employee_id, report_date, report_text):
        """Add a new report."""
        conn.execute(text('''
        INSERT INTO daily_reports (employee_id, report_date, report_text)
        VALUES (:employee_id, :report_date, :report_text)
        '''), {
            'employee_id': employee_id,
            'report_date': report_date,
            'report_text': report_text
        })
        conn.commit()
    
    @staticmethod
    def update_report(conn, report_id, report_date, report_text):
        """Update an existing report."""
        conn.execute(text('''
        UPDATE daily_reports 
        SET report_text = :report_text, report_date = :report_date, created_at = CURRENT_TIMESTAMP
        WHERE id = :id
        '''), {
            'report_text': report_text,
            'report_date': report_date,
            'id': report_id
        })
        conn.commit()
    
    @staticmethod
    def check_report_exists(conn, employee_id, report_date):
        """Check if a report already exists for the given date."""
        result = conn.execute(text('''
        SELECT id FROM daily_reports 
        WHERE employee_id = :employee_id AND report_date = :report_date
        '''), {'employee_id': employee_id, 'report_date': report_date})
        return result.fetchone()


class TaskModel:
    """Task data operations"""
    
    @staticmethod
    def get_all_tasks(conn, employee_name=None, status_filter=None):
        """Get all tasks with optional employee and status filters."""
        query = '''
        SELECT t.id, e.full_name, t.task_description, t.due_date, t.is_completed, t.created_at, e.id as employee_id
        FROM tasks t
        JOIN employees e ON t.employee_id = e.id
        WHERE 1=1
        '''
        
        params = {}
        
        if employee_name and employee_name != "All Employees":
            query += ' AND e.full_name = :employee_name'
            params['employee_name'] = employee_name
        
        if status_filter == "Pending":
            query += ' AND t.is_completed = FALSE'
        elif status_filter == "Completed":
            query += ' AND t.is_completed = TRUE'
        
        query += ' ORDER BY t.due_date ASC NULLS LAST, t.created_at DESC'
        
        result = conn.execute(text(query), params)
        return result.fetchall()
    
    @staticmethod
    def get_employee_tasks(conn, employee_id, completed=None):
        """Get tasks for a specific employee."""
        query = '''
        SELECT id, task_description, due_date, is_completed, created_at
        FROM tasks
        WHERE employee_id = :employee_id
        '''
        
        params = {'employee_id': employee_id}
        
        if completed is not None:
            query += ' AND is_completed = :completed'
            params['completed'] = completed
        
        query += ' ORDER BY due_date ASC NULLS LAST, created_at DESC'
        
        result = conn.execute(text(query), params)
        return result.fetchall()
    
    @staticmethod
    def add_task(conn, employee_id, task_description, due_date):
        """Add a new task."""
        conn.execute(text('''
        INSERT INTO tasks (employee_id, task_description, due_date, is_completed)
        VALUES (:employee_id, :task_description, :due_date, FALSE)
        '''), {
            'employee_id': employee_id,
            'task_description': task_description,
            'due_date': due_date
        })
        conn.commit()
    
    @staticmethod
    def update_task_status(conn, task_id, is_completed):
        """Update task completion status."""
        conn.execute(text('UPDATE tasks SET is_completed = :is_completed WHERE id = :id'), 
                    {'id': task_id, 'is_completed': is_completed})
        conn.commit()
    
    @staticmethod
    def delete_task(conn, task_id):
        """Delete a task."""
        conn.execute(text('DELETE FROM tasks WHERE id = :id'), {'id': task_id})
        conn.commit()
