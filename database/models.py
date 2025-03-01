from sqlalchemy import text

class CompanyModel:
    """Company data operations"""
    
    @staticmethod
    def get_all_companies(conn):
        """Get all companies from the database."""
        result = conn.execute(text('''
        SELECT id, company_name, username, profile_pic_url, is_active, created_at 
        FROM companies
        ORDER BY company_name
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_active_companies(conn):
        """Get all active companies."""
        result = conn.execute(text('''
        SELECT id, company_name FROM companies 
        WHERE is_active = TRUE
        ORDER BY company_name
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_company_by_id(conn, company_id):
        """Get company data by ID."""
        result = conn.execute(text('''
        SELECT company_name, username, profile_pic_url, is_active
        FROM companies
        WHERE id = :company_id
        '''), {'company_id': company_id})
        return result.fetchone()
    
    @staticmethod
    def add_company(conn, company_name, username, password, profile_pic_url):
        """Add a new company to the database."""
        default_pic = "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        
        conn.execute(text('''
        INSERT INTO companies (company_name, username, password, profile_pic_url, is_active)
        VALUES (:company_name, :username, :password, :profile_pic_url, TRUE)
        '''), {
            'company_name': company_name,
            'username': username,
            'password': password,
            'profile_pic_url': profile_pic_url if profile_pic_url else default_pic
        })
        conn.commit()
    
    @staticmethod
    def update_company_status(conn, company_id, is_active):
        """Activate or deactivate a company and all its branches and employees."""
        # Update company status
        conn.execute(text('UPDATE companies SET is_active = :is_active WHERE id = :id'), 
                    {'id': company_id, 'is_active': is_active})
        
        # Update all branches for this company
        conn.execute(text('''
        UPDATE branches 
        SET is_active = :is_active 
        WHERE company_id = :company_id
        '''), {'company_id': company_id, 'is_active': is_active})
        
        # Update all employees in all branches of this company
        conn.execute(text('''
        UPDATE employees 
        SET is_active = :is_active 
        WHERE branch_id IN (SELECT id FROM branches WHERE company_id = :company_id)
        '''), {'company_id': company_id, 'is_active': is_active})
        
        conn.commit()
    
    @staticmethod
    def reset_password(conn, company_id, new_password):
        """Reset a company's password."""
        conn.execute(text('UPDATE companies SET password = :password WHERE id = :id'), 
                    {'id': company_id, 'password': new_password})
        conn.commit()
    
    @staticmethod
    def update_profile(conn, company_id, company_name, profile_pic_url):
        """Update company profile information."""
        conn.execute(text('''
        UPDATE companies
        SET company_name = :company_name, profile_pic_url = :profile_pic_url
        WHERE id = :company_id
        '''), {
            'company_name': company_name,
            'profile_pic_url': profile_pic_url,
            'company_id': company_id
        })
        conn.commit()
    
    @staticmethod
    def verify_password(conn, company_id, current_password):
        """Verify company's current password."""
        result = conn.execute(text('''
        SELECT COUNT(*)
        FROM companies
        WHERE id = :company_id AND password = :current_password
        '''), {'company_id': company_id, 'current_password': current_password})
        return result.fetchone()[0] > 0


class BranchModel:
    """Branch data operations"""
    
    @staticmethod
    def get_all_branches(conn):
        """Get all branches with company information."""
        result = conn.execute(text('''
        SELECT b.id, b.branch_name, b.location, b.branch_head, b.is_active, 
               c.company_name, c.id as company_id
        FROM branches b
        JOIN companies c ON b.company_id = c.id
        ORDER BY c.company_name, b.branch_name
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_company_branches(conn, company_id):
        """Get all branches for a specific company."""
        result = conn.execute(text('''
        SELECT id, branch_name, location, branch_head, is_active
        FROM branches
        WHERE company_id = :company_id
        ORDER BY branch_name
        '''), {'company_id': company_id})
        return result.fetchall()
    
    @staticmethod
    def get_active_branches(conn, company_id=None):
        """Get all active branches, optionally filtered by company."""
        query = '''
        SELECT b.id, b.branch_name, c.company_name
        FROM branches b
        JOIN companies c ON b.company_id = c.id
        WHERE b.is_active = TRUE AND c.is_active = TRUE
        '''
        
        params = {}
        if company_id:
            query += ' AND b.company_id = :company_id'
            params = {'company_id': company_id}
        
        query += ' ORDER BY c.company_name, b.branch_name'
        
        result = conn.execute(text(query), params)
        return result.fetchall()


class MessageModel:
    """Message data operations"""
    
    @staticmethod
    def send_message(conn, sender_type, sender_id, receiver_type, receiver_id, message_text):
        """Send a new message."""
        conn.execute(text('''
        INSERT INTO messages 
        (sender_type, sender_id, receiver_type, receiver_id, message_text, is_read)
        VALUES (:sender_type, :sender_id, :receiver_type, :receiver_id, :message_text, FALSE)
        '''), {
            'sender_type': sender_type,
            'sender_id': sender_id,
            'receiver_type': receiver_type,
            'receiver_id': receiver_id,
            'message_text': message_text
        })
        conn.commit()
    
    @staticmethod
    def mark_as_read(conn, message_id):
        """Mark a message as read."""
        conn.execute(text('UPDATE messages SET is_read = TRUE WHERE id = :id'), 
                    {'id': message_id})
        conn.commit()
    
    @staticmethod
    def get_messages_for_admin(conn):
        """Get all messages for admin."""
        result = conn.execute(text('''
        SELECT m.id, m.sender_type, m.sender_id, m.message_text, m.is_read, m.created_at,
               CASE WHEN m.sender_type = 'company' THEN c.company_name ELSE 'Admin' END as sender_name
        FROM messages m
        LEFT JOIN companies c ON m.sender_type = 'company' AND m.sender_id = c.id
        WHERE m.receiver_type = 'admin'
        ORDER BY m.created_at DESC
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_messages_for_company(conn, company_id):
        """Get all messages for a specific company."""
        result = conn.execute(text('''
        SELECT m.id, m.sender_type, m.sender_id, m.message_text, m.is_read, m.created_at,
               CASE WHEN m.sender_type = 'admin' THEN 'Admin' ELSE c.company_name END as sender_name
        FROM messages m
        LEFT JOIN companies c ON m.sender_type = 'company' AND m.sender_id = c.id
        WHERE (m.receiver_type = 'company' AND m.receiver_id = :company_id)
           OR (m.sender_type = 'company' AND m.sender_id = :company_id)
        ORDER BY m.created_at DESC
        '''), {'company_id': company_id})
        return result.fetchall()


class EmployeeModel:
    """Employee data operations"""
    
    @staticmethod
    def get_all_employees(conn):
        """Get all employees from the database."""
        result = conn.execute(text('''
        SELECT e.id, e.username, e.full_name, e.profile_pic_url, e.is_active,
               b.branch_name, c.company_name
        FROM employees e
        JOIN branches b ON e.branch_id = b.id
        JOIN companies c ON b.company_id = c.id
        ORDER BY c.company_name, b.branch_name, e.full_name
        '''))
        return result.fetchall()
    
    @staticmethod
    def get_branch_employees(conn, branch_id):
        """Get all employees for a specific branch."""
        result = conn.execute(text('''
        SELECT id, username, full_name, profile_pic_url, is_active
        FROM employees
        WHERE branch_id = :branch_id
        ORDER BY full_name
        '''), {'branch_id': branch_id})
        return result.fetchall()
    
    @staticmethod
    def get_active_employees(conn):
        """Get all active employees."""
        result = conn.execute(text('''
        SELECT e.id, e.full_name, b.branch_name, c.company_name
        FROM employees e
        JOIN branches b ON e.branch_id = b.id
        JOIN companies c ON b.company_id = c.id
        WHERE e.is_active = TRUE 
          AND b.is_active = TRUE
          AND c.is_active = TRUE
        ORDER BY e.full_name
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
    def add_employee(conn, branch_id, username, password, full_name, profile_pic_url):
        """Add a new employee to the database."""
        default_pic = "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        
        conn.execute(text('''
        INSERT INTO employees (branch_id, username, password, full_name, profile_pic_url, is_active)
        VALUES (:branch_id, :username, :password, :full_name, :profile_pic_url, TRUE)
        '''), {
            'branch_id': branch_id,
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
