import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import bcrypt
import json
import calendar

class Database:
    def __init__(self, db_name="staff.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Staff table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS staff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    monthly_salary REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER,
                    date DATE NOT NULL,
                    is_present BOOLEAN DEFAULT 0,
                    is_holiday BOOLEAN DEFAULT 0,
                    FOREIGN KEY (staff_id) REFERENCES staff (id),
                    UNIQUE(staff_id, date)
                )
            ''')

            # Advance payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS advances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER,
                    amount REAL NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (staff_id) REFERENCES staff (id)
                )
            ''')

            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            # Users table for multi-user access
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Advance repayment schedule table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS advance_repayments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    advance_id INTEGER,
                    amount REAL NOT NULL,
                    due_date DATE NOT NULL,
                    is_paid BOOLEAN DEFAULT 0,
                    FOREIGN KEY (advance_id) REFERENCES advances (id)
                )
            ''')

            # Holidays table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holidays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            ''')

            # Insert default working days if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value)
                VALUES ('working_days', '26')
            ''')
            
            # Insert default admin user if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role)
                VALUES ('admin', ?, 'admin')
            ''', (self._hash_password('admin'),))
            
            conn.commit()

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    # User Management
    def create_user(self, username, password, role):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            hashed_password = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, role))
            conn.commit()
            return cursor.lastrowid
    
    def verify_user(self, username, password):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password, role FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            if result and self._check_password(password, result[0]):
                return result[1]  # Return role
            return None
    
    def get_all_users(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT id, username, role FROM users", conn)
    
    def delete_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()

    # Staff Management
    def add_staff(self, name, phone, monthly_salary):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO staff (name, phone, monthly_salary)
                VALUES (?, ?, ?)
            ''', (name, phone, monthly_salary))
            conn.commit()
            return cursor.lastrowid

    def get_all_staff(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM staff ORDER BY name", conn)

    def update_staff(self, staff_id, name, phone, monthly_salary):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE staff
                SET name = ?, phone = ?, monthly_salary = ?
                WHERE id = ?
            ''', (name, phone, monthly_salary, staff_id))
            conn.commit()

    def delete_staff(self, staff_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM staff WHERE id = ?', (staff_id,))
            conn.commit()

    # Holiday Management
    def add_holiday(self, date, name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO holidays (date, name)
                VALUES (?, ?)
            ''', (date, name))
            conn.commit()
            
            # Mark all staff as present on this holiday
            staff_df = self.get_all_staff()
            for _, staff in staff_df.iterrows():
                self.mark_attendance(staff['id'], date, True, True)
            
            return cursor.lastrowid
    
    def get_holidays(self, year=None, month=None):
        with self.get_connection() as conn:
            if year and month:
                # Get holidays for a specific month
                first_day = f"{year}-{month:02d}-01"
                last_day = f"{year}-{month:02d}-31"
                return pd.read_sql_query('''
                    SELECT * FROM holidays
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date
                ''', conn, params=(first_day, last_day))
            else:
                # Get all holidays
                return pd.read_sql_query('''
                    SELECT * FROM holidays
                    ORDER BY date
                ''', conn)
    
    def delete_holiday(self, holiday_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM holidays WHERE id = ?', (holiday_id,))
            conn.commit()
    
    def is_holiday(self, date):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM holidays WHERE date = ?', (date,))
            result = cursor.fetchone()
            return result is not None

    # Attendance Management
    def mark_attendance(self, staff_id, date, is_present, is_holiday=False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO attendance (staff_id, date, is_present, is_holiday)
                VALUES (?, ?, ?, ?)
            ''', (staff_id, date, is_present, is_holiday))
            conn.commit()

    def get_attendance(self, date):
        with self.get_connection() as conn:
            # Check if the date is a holiday
            is_holiday = self.is_holiday(date)
            
            # Get attendance data
            attendance_df = pd.read_sql_query('''
                SELECT 
                    s.id, 
                    s.name, 
                    COALESCE(a.is_present, 0) as is_present,
                    COALESCE(a.is_holiday, 0) as is_holiday
                FROM staff s
                LEFT JOIN attendance a ON s.id = a.staff_id AND a.date = ?
                ORDER BY s.name
            ''', conn, params=(date,))
            
            # If it's a holiday, mark all staff as present
            if is_holiday:
                attendance_df['is_present'] = True
                attendance_df['is_holiday'] = True
            
            return attendance_df
    
    def get_monthly_attendance(self, year, month):
        with self.get_connection() as conn:
            # Get the first and last day of the month
            first_day = f"{year}-{month:02d}-01"
            last_day = f"{year}-{month:02d}-31"
            
            # Get all staff
            staff_df = pd.read_sql_query("SELECT id, name FROM staff", conn)
            
            # Get all attendance records for the month
            attendance_df = pd.read_sql_query('''
                SELECT staff_id, date, is_present, is_holiday
                FROM attendance
                WHERE date BETWEEN ? AND ?
            ''', conn, params=(first_day, last_day))
            
            # Get all holidays for the month
            holidays_df = self.get_holidays(year, month)
            
            # Create a pivot table for the calendar view
            if not attendance_df.empty:
                pivot_df = attendance_df.pivot(
                    index='staff_id', 
                    columns='date', 
                    values='is_present'
                ).fillna(False)
                
                # Merge with staff names
                result_df = staff_df.merge(pivot_df, left_on='id', right_index=True)
                
                # Add holiday information
                if not holidays_df.empty:
                    for _, holiday in holidays_df.iterrows():
                        holiday_date = holiday['date']
                        if holiday_date in result_df.columns:
                            result_df[holiday_date] = True
                            # Add a note that this is a holiday
                            result_df.rename(columns={holiday_date: f"{holiday_date} (Holiday: {holiday['name']})"}, inplace=True)
                
                return result_df
            else:
                return staff_df

    def get_monthly_attendance_for_staff(self, staff_id, year, month):
        """Get attendance records for a specific staff member in a given month."""
        with self.get_connection() as conn:
            # Get all dates in the month
            first_day = date(year, month, 1)
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)
            
            # Get attendance records
            attendance = pd.read_sql_query('''
                WITH RECURSIVE dates(date) AS (
                    SELECT date(?)
                    UNION ALL
                    SELECT date(date, '+1 day')
                    FROM dates
                    WHERE date < date(?)
                )
                SELECT 
                    d.date,
                    COALESCE(a.is_present, 0) as is_present,
                    COALESCE(
                        (SELECT 1 FROM holidays h WHERE h.date = d.date),
                        0
                    ) as is_holiday
                FROM dates d
                LEFT JOIN attendance a ON d.date = a.date AND a.staff_id = ?
            ''', conn, params=(first_day, last_day, staff_id))
            
            # Convert date strings to datetime
            attendance['date'] = pd.to_datetime(attendance['date'])
            
            # Ensure boolean columns
            attendance['is_present'] = attendance['is_present'].astype(bool)
            attendance['is_holiday'] = attendance['is_holiday'].astype(bool)
            
            return attendance

    def get_working_days_in_month(self, year, month):
        """Get the number of working days in a month (excluding holidays)."""
        # Get total days in month
        _, num_days = calendar.monthrange(year, month)
        
        # Get holidays in this month
        query = """
            SELECT COUNT(*) as holiday_count
            FROM holidays
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (str(year), str(month).zfill(2)))
            holiday_count = cursor.fetchone()[0]
            
            # Return total days minus holidays
            return num_days - holiday_count

    # Advance Management
    def add_advance(self, staff_id, amount, date, repayment_months=1):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO advances (staff_id, amount, date)
                VALUES (?, ?, ?)
            ''', (staff_id, amount, date))
            advance_id = cursor.lastrowid
            
            # Create repayment schedule
            if repayment_months > 1:
                monthly_amount = amount / repayment_months
                for i in range(repayment_months):
                    # Calculate due date (first day of next month + i months)
                    due_date = date.replace(day=1)
                    for _ in range(i+1):
                        if due_date.month == 12:
                            due_date = due_date.replace(year=due_date.year + 1, month=1)
                        else:
                            due_date = due_date.replace(month=due_date.month + 1)
                    
                    cursor.execute('''
                        INSERT INTO advance_repayments (advance_id, amount, due_date)
                        VALUES (?, ?, ?)
                    ''', (advance_id, monthly_amount, due_date))
            else:
                # Single payment due next month
                due_date = date.replace(day=1)
                if due_date.month == 12:
                    due_date = due_date.replace(year=due_date.year + 1, month=1)
                else:
                    due_date = due_date.replace(month=due_date.month + 1)
                
                cursor.execute('''
                    INSERT INTO advance_repayments (advance_id, amount, due_date)
                    VALUES (?, ?, ?)
                ''', (advance_id, amount, due_date))
            
            conn.commit()
            return advance_id

    def get_advances(self, staff_id, start_date, end_date):
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT * FROM advances
                WHERE staff_id = ? AND date BETWEEN ? AND ?
                ORDER BY date
            ''', conn, params=(staff_id, start_date, end_date))
    
    def get_pending_advances(self, staff_id=None):
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    a.id as advance_id,
                    s.id as staff_id,
                    s.name as staff_name,
                    a.amount as total_amount,
                    a.date as advance_date,
                    SUM(CASE WHEN ar.is_paid = 0 THEN ar.amount ELSE 0 END) as pending_amount,
                    COUNT(CASE WHEN ar.is_paid = 0 THEN 1 END) as pending_installments
                FROM advances a
                JOIN staff s ON a.staff_id = s.id
                LEFT JOIN advance_repayments ar ON a.id = ar.advance_id
            '''
            
            params = []
            if staff_id:
                query += ' WHERE s.id = ?'
                params.append(staff_id)
            
            query += ' GROUP BY a.id, s.id, s.name, a.amount, a.date'
            query += ' HAVING pending_amount > 0'
            
            return pd.read_sql_query(query, conn, params=params)
    
    def mark_repayment_paid(self, repayment_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE advance_repayments
                SET is_paid = 1
                WHERE id = ?
            ''', (repayment_id,))
            conn.commit()

    # Settings Management
    def get_working_days(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = "working_days"')
            result = cursor.fetchone()
            return int(result[0]) if result else 26

    def set_working_days(self, days):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES ("working_days", ?)
            ''', (str(days),))
            conn.commit()
    
    def get_setting(self, key, default=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, str(value)))
            conn.commit()

    # Report Generation
    def get_monthly_report(self, year, month):
        """Generate monthly attendance and salary report."""
        # Get working days for this month
        working_days = self.get_working_days_in_month(year, month)
        
        # Get all staff
        staff = self.get_all_staff()
        report_data = []
        
        for _, staff_member in staff.iterrows():
            staff_id = staff_member['id']
            
            # Get attendance for the month
            attendance = self.get_monthly_attendance_for_staff(staff_id, year, month)
            # Count days present (including holidays)
            days_present = len(attendance[attendance['is_present'] | attendance['is_holiday']])
            
            # Calculate salary based on attendance
            attendance_ratio = days_present / working_days if working_days > 0 else 0
            calculated_salary = staff_member['monthly_salary'] * attendance_ratio
            
            # Get pending advances
            advance_deduction = self.get_advance_deduction(staff_id, year, month)
            
            report_data.append({
                'id': staff_id,
                'name': staff_member['name'],
                'monthly_salary': staff_member['monthly_salary'],
                'days_present': days_present,
                'working_days': working_days,
                'calculated_salary': calculated_salary,
                'total_advance': advance_deduction,
                'final_salary': calculated_salary - advance_deduction
            })
        
        return pd.DataFrame(report_data)
    
    # Dashboard Analytics
    def get_dashboard_stats(self, year=None, month=None):
        with self.get_connection() as conn:
            if year is None or month is None:
                today = date.today()
                year = today.year
                month = today.month
            
            # Total staff
            staff_count = pd.read_sql_query("SELECT COUNT(*) as count FROM staff", conn).iloc[0]['count']
            
            # Average attendance percentage
            first_day = f"{year}-{month:02d}-01"
            last_day = f"{year}-{month:02d}-31"
            
            attendance_stats = pd.read_sql_query('''
                SELECT 
                    COUNT(DISTINCT staff_id) as total_staff,
                    SUM(CASE WHEN is_present = 1 OR is_holiday = 1 THEN 1 ELSE 0 END) as total_present,
                    COUNT(*) as total_days
                FROM attendance
                WHERE date BETWEEN ? AND ?
            ''', conn, params=(first_day, last_day))
            
            if not attendance_stats.empty and attendance_stats.iloc[0]['total_days'] > 0:
                avg_attendance = (attendance_stats.iloc[0]['total_present'] / attendance_stats.iloc[0]['total_days']) * 100
            else:
                avg_attendance = 0
            
            # Total salary paid this month
            report_df = self.get_monthly_report(year, month)
            total_salary = report_df['final_salary'].sum() if not report_df.empty else 0
            
            # Total advance given this month
            advances_df = pd.read_sql_query('''
                SELECT SUM(amount) as total_advance
                FROM advances
                WHERE date BETWEEN ? AND ?
            ''', conn, params=(first_day, last_day))
            
            total_advance = advances_df.iloc[0]['total_advance'] if not advances_df.empty and advances_df.iloc[0]['total_advance'] is not None else 0
            
            return {
                'total_staff': staff_count,
                'avg_attendance': avg_attendance,
                'total_salary': total_salary,
                'total_advance': total_advance
            }

    def get_advance_deduction(self, staff_id, year, month):
        """Calculate advance deductions for a staff member in a given month."""
        with self.get_connection() as conn:
            # Get the first and last day of the month
            first_day = date(year, month, 1)
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)
            
            # Get advance repayments due in this month
            query = '''
                SELECT SUM(ar.amount) as total_deduction
                FROM advance_repayments ar
                JOIN advances a ON ar.advance_id = a.id
                WHERE a.staff_id = ?
                AND ar.due_date BETWEEN ? AND ?
                AND ar.is_paid = 0
            '''
            
            result = pd.read_sql_query(query, conn, params=(staff_id, first_day, last_day))
            return float(result['total_deduction'].iloc[0]) if not result.empty and result['total_deduction'].iloc[0] is not None else 0.0

    def change_password(self, username, current_password, new_password):
        """Change a user's password after verifying their current password."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # First verify the current password
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if not result:
                return False, "User not found"
            
            if not self._check_password(current_password, result[0]):
                return False, "Current password is incorrect"
            
            # Hash and update the new password
            hashed_password = self._hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password = ?
                WHERE username = ?
            ''', (hashed_password, username))
            conn.commit()
            
            return True, "Password updated successfully" 