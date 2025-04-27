import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import bcrypt
import json
import calendar

class Database:
    def __init__(self, db_name="staff.db"):
        print(f"Using database file: {db_name}")
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
                    salary_cycle_start INTEGER DEFAULT 1,
                    salary_cycle_end INTEGER DEFAULT 31,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Salary history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salary_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER,
                    salary REAL NOT NULL,
                    effective_from DATE NOT NULL,
                    effective_to DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES staff (id)
                )
            ''')

            # Attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER,
                    date DATE NOT NULL,
                    is_present BOOLEAN DEFAULT 1,
                    is_holiday BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES staff (id),
                    UNIQUE(staff_id, date)
                )
            ''')

            # Advances table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS advances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER,
                    amount REAL NOT NULL,
                    date DATE NOT NULL,
                    repayment_type TEXT CHECK(repayment_type IN ('OneTime', 'Weekly', 'Monthly')),
                    emi_amount REAL,
                    total_emi_count INTEGER,
                    remaining_amount REAL,
                    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Completed')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES staff (id)
                )
            ''')

            # Advance repayments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS advance_repayments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    advance_id INTEGER,
                    amount REAL NOT NULL,
                    due_date DATE NOT NULL,
                    is_paid BOOLEAN DEFAULT 0,
                    paid_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (advance_id) REFERENCES advances (id)
                )
            ''')

            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

            # Insert default settings if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value)
                VALUES 
                    ('working_days', '26'),
                    ('salary_cycle_start', '1'),
                    ('salary_cycle_end', '31')
            ''')
            
            # Insert default admin user 'Krish' if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role)
                VALUES ('Krish', ?, 'admin')
            ''', (self._hash_password('Krish@9777'),))
            
            # Add hidden column to staff table if it doesn't exist
            try:
                cursor.execute("ALTER TABLE staff ADD COLUMN hidden INTEGER DEFAULT 0")
            except Exception as e:
                pass  # Ignore if column already exists
            
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

    def update_user(self, user_id, new_username=None, new_password=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if new_username and new_password:
                hashed_password = self._hash_password(new_password)
                cursor.execute('''
                    UPDATE users SET username = ?, password = ? WHERE id = ?
                ''', (new_username, hashed_password, user_id))
            elif new_username:
                cursor.execute('''
                    UPDATE users SET username = ? WHERE id = ?
                ''', (new_username, user_id))
            elif new_password:
                hashed_password = self._hash_password(new_password)
                cursor.execute('''
                    UPDATE users SET password = ? WHERE id = ?
                ''', (hashed_password, user_id))
            conn.commit()

    # Staff Management
    def add_staff(self, name, phone, monthly_salary, salary_cycle_start, salary_cycle_end):
        try:
            # Check for duplicate phone number
            cursor = self.get_connection().cursor()
            cursor.execute("SELECT id FROM staff WHERE phone = ?", (phone,))
            if cursor.fetchone():
                return False, "A staff member with this phone number already exists"
            
            cursor.execute("""
                INSERT INTO staff (name, phone, monthly_salary, salary_cycle_start, salary_cycle_end)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, monthly_salary, salary_cycle_start, salary_cycle_end))
            self.get_connection().commit()
            return True, "Staff added successfully"
        except Exception as e:
            return False, f"Error adding staff: {str(e)}"

    def get_all_staff(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM staff WHERE hidden IS NULL OR hidden = 0 ORDER BY name", conn)

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
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE staff SET hidden = 1 WHERE id = ?", (staff_id,))
                conn.commit()
            return True, "Staff member hidden successfully"
        except Exception as e:
            return False, f"Error hiding staff: {str(e)}"

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
    
    def get_holidays(self, year=None, month=None, start_date=None, end_date=None):
        """Get all holidays within a date range"""
        try:
            with self.get_connection() as conn:
                if year is not None and month is not None:
                    # Get holidays for a specific month
                    first_day = f"{year}-{month:02d}-01"
                    last_day = f"{year}-{month:02d}-31"
                    return pd.read_sql_query('''
                        SELECT id, date, name FROM holidays 
                        WHERE date BETWEEN ? AND ?
                        ORDER BY date
                    ''', conn, params=(first_day, last_day))
                elif start_date and end_date:
                    return pd.read_sql_query('''
                        SELECT id, date, name FROM holidays 
                        WHERE date BETWEEN ? AND ?
                        ORDER BY date
                    ''', conn, params=(start_date, end_date))
                else:
                    return pd.read_sql_query('''
                        SELECT id, date, name FROM holidays 
                        ORDER BY date
                    ''', conn)
        except Exception as e:
            print(f"Error in get_holidays: {e}")
            return pd.DataFrame(columns=['id', 'date', 'name'])

    def delete_holiday(self, holiday_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM holidays WHERE id = ?', (holiday_id,))
            conn.commit()
    
    def is_holiday(self, date):
        """Check if a given date is a holiday"""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute('SELECT 1 FROM holidays WHERE date = ?', (date,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error in is_holiday: {e}")
            return False

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
            
            # Convert numeric values to boolean
            attendance_df['is_present'] = attendance_df['is_present'].astype(bool)
            attendance_df['is_holiday'] = attendance_df['is_holiday'].astype(bool)
            
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
                            result_df[holiday_date] = 'Leave'
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

    def get_salary_cycle(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key IN ("salary_cycle_start", "salary_cycle_end")')
            results = cursor.fetchall()
            return {
                'start': int(results[0][0]),
                'end': int(results[1][0])
            }

    def set_salary_cycle(self, start_day, end_day):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE settings SET value = ? WHERE key = "salary_cycle_start"', (str(start_day),))
            cursor.execute('UPDATE settings SET value = ? WHERE key = "salary_cycle_end"', (str(end_day),))
            conn.commit()

    def update_staff_salary(self, staff_id, new_salary, effective_from):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # End the previous salary record
            cursor.execute('''
                UPDATE salary_history 
                SET effective_to = ? 
                WHERE staff_id = ? AND effective_to IS NULL
            ''', (effective_from, staff_id))
            
            # Add new salary record
            cursor.execute('''
                INSERT INTO salary_history (staff_id, salary, effective_from)
                VALUES (?, ?, ?)
            ''', (staff_id, new_salary, effective_from))
            
            # Update current salary in staff table
            cursor.execute('''
                UPDATE staff 
                SET monthly_salary = ? 
                WHERE id = ?
            ''', (new_salary, staff_id))
            
            conn.commit()

    def get_staff_salary_history(self, staff_id):
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT * FROM salary_history 
                WHERE staff_id = ? 
                ORDER BY effective_from DESC
            ''', conn, params=(staff_id,))

    def add_advance_with_emi(self, staff_id, amount, date, repayment_type, emi_amount=None, emi_count=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO advances (
                    staff_id, amount, date, repayment_type, 
                    emi_amount, total_emi_count, remaining_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (staff_id, amount, date, repayment_type, emi_amount, emi_count, amount))
            conn.commit()
            return cursor.lastrowid

    def get_advance_details(self, advance_id):
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT * FROM advances WHERE id = ?
            ''', conn, params=(advance_id,)).iloc[0]

    def update_advance_remaining(self, advance_id, paid_amount):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE advances 
                SET remaining_amount = remaining_amount - ?,
                    status = CASE 
                        WHEN remaining_amount - ? <= 0 THEN 'Completed'
                        ELSE status 
                    END
                WHERE id = ?
            ''', (paid_amount, paid_amount, advance_id))
            conn.commit()

    def auto_mark_attendance(self, date):
        """Automatically mark attendance for all staff on a given date"""
        try:
            # Check if it's a holiday
            cursor = self.get_connection().cursor()
            cursor.execute('SELECT 1 FROM holidays WHERE date = ?', (date,))
            is_holiday = cursor.fetchone() is not None

            # Get all staff
            cursor.execute('SELECT id FROM staff')
            staff_list = cursor.fetchall()

            # Mark attendance for each staff
            for staff in staff_list:
                cursor.execute('''
                    INSERT OR REPLACE INTO attendance (staff_id, date, is_present, is_holiday)
                    VALUES (?, ?, ?, ?)
                ''', (staff[0], date, True, is_holiday))

            self.get_connection().commit()
            return True
        except Exception as e:
            print(f"Error in auto_mark_attendance: {e}")
            return False

    def add_holiday(self, date, name):
        """Add a new holiday"""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute('''
                INSERT INTO holidays (date, name)
                VALUES (?, ?)
            ''', (date, name))
            self.get_connection().commit()
            return True
        except Exception as e:
            print(f"Error in add_holiday: {e}")
            return False

    def remove_holiday(self, date):
        """Remove a holiday"""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute('DELETE FROM holidays WHERE date = ?', (date,))
            self.get_connection().commit()
            return True
        except Exception as e:
            print(f"Error in remove_holiday: {e}")
            return False

    def get_holidays(self, year=None, month=None, start_date=None, end_date=None):
        """Get all holidays within a date range"""
        try:
            with self.get_connection() as conn:
                if year is not None and month is not None:
                    # Get holidays for a specific month
                    first_day = f"{year}-{month:02d}-01"
                    last_day = f"{year}-{month:02d}-31"
                    return pd.read_sql_query('''
                        SELECT id, date, name FROM holidays 
                        WHERE date BETWEEN ? AND ?
                        ORDER BY date
                    ''', conn, params=(first_day, last_day))
                elif start_date and end_date:
                    return pd.read_sql_query('''
                        SELECT id, date, name FROM holidays 
                        WHERE date BETWEEN ? AND ?
                        ORDER BY date
                    ''', conn, params=(start_date, end_date))
                else:
                    return pd.read_sql_query('''
                        SELECT id, date, name FROM holidays 
                        ORDER BY date
                    ''', conn)
        except Exception as e:
            print(f"Error in get_holidays: {e}")
            return pd.DataFrame(columns=['id', 'date', 'name'])

    def is_holiday(self, date):
        """Check if a given date is a holiday"""
        try:
            cursor = self.get_connection().cursor()
            cursor.execute('SELECT 1 FROM holidays WHERE date = ?', (date,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error in is_holiday: {e}")
            return False

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

    def get_attendance_calendar(self, year, month):
        """Get attendance calendar for a specific month."""
        with self.get_connection() as conn:
            # Get the first and last day of the month
            first_day = date(year, month, 1)
            if month == 12:
                last_day = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(year, month + 1, 1) - timedelta(days=1)
            
            # Get all staff
            staff_df = pd.read_sql_query("SELECT id, name FROM staff", conn)
            
            # Get all attendance records for the month
            attendance_df = pd.read_sql_query('''
                SELECT staff_id, date, is_present, is_holiday
                FROM attendance
                WHERE date BETWEEN ? AND ?
            ''', conn, params=(first_day, last_day))
            
            # Create a pivot table for the calendar view
            if not attendance_df.empty:
                pivot_df = attendance_df.pivot(
                    index='staff_id', 
                    columns='date', 
                    values='is_present'
                ).fillna(False)
                
                # Merge with staff names
                result_df = staff_df.merge(pivot_df, left_on='id', right_index=True)
                
                # Rename columns to show dates
                result_df = result_df.rename(columns={col: col.strftime('%d') for col in result_df.columns if isinstance(col, pd.Timestamp)})
                
                return result_df
            else:
                return staff_df

    def get_staff_salary_cycle(self, staff_id):
        """Get salary cycle for a specific staff member."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT salary_cycle_start, salary_cycle_end 
                FROM staff 
                WHERE id = ?
            ''', (staff_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'start': int(result[0]) if result[0] else 1,
                    'end': int(result[1]) if result[1] else 31
                }
            return {'start': 1, 'end': 31}  # Default values

    def set_staff_salary_cycle(self, staff_id, start_day, end_day):
        """Set salary cycle for a specific staff member."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE staff 
                SET salary_cycle_start = ?, salary_cycle_end = ?
                WHERE id = ?
            ''', (start_day, end_day, staff_id))
            conn.commit()

    def get_all_advances(self):
        """Get all advance payments."""
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT a.*, s.name as staff_name
                FROM advances a
                JOIN staff s ON a.staff_id = s.id
                ORDER BY a.date DESC
            ''', conn)

    def add_advance_repayment(self, advance_id, amount, due_date):
        """Add a new advance repayment record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO advance_repayments (advance_id, amount, due_date)
                VALUES (?, ?, ?)
            ''', (advance_id, amount, due_date))
            conn.commit()
            return cursor.lastrowid

    def mark_repayment_paid(self, repayment_id, paid_date=None):
        """Mark an advance repayment as paid."""
        if paid_date is None:
            paid_date = date.today()
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE advance_repayments
                SET is_paid = 1, paid_date = ?
                WHERE id = ?
            ''', (paid_date, repayment_id))
            conn.commit()

    def get_pending_repayments(self, staff_id=None, start_date=None, end_date=None):
        """Get all pending advance repayments."""
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    ar.id as repayment_id,
                    ar.advance_id,
                    s.id as staff_id,
                    s.name as staff_name,
                    a.amount as total_advance,
                    ar.amount as repayment_amount,
                    ar.due_date,
                    a.date as advance_date
                FROM advance_repayments ar
                JOIN advances a ON ar.advance_id = a.id
                JOIN staff s ON a.staff_id = s.id
                WHERE ar.is_paid = 0
            '''
            
            params = []
            if staff_id:
                query += ' AND s.id = ?'
                params.append(staff_id)
            if start_date:
                query += ' AND ar.due_date >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND ar.due_date <= ?'
                params.append(end_date)
                
            query += ' ORDER BY ar.due_date'
            
            return pd.read_sql_query(query, conn, params=params)

    def get_advance_repayment_history(self, advance_id):
        """Get repayment history for a specific advance."""
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT 
                    ar.*,
                    CASE 
                        WHEN ar.is_paid = 1 THEN 'Paid'
                        ELSE 'Pending'
                    END as status
                FROM advance_repayments ar
                WHERE ar.advance_id = ?
                ORDER BY ar.due_date
            ''', conn, params=(advance_id,))

    def get_staff_outstanding(self, staff_id=None):
        """Get outstanding amounts for staff (advances - repayments)"""
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    s.id,
                    s.name,
                    COALESCE(SUM(a.amount), 0) as total_advance,
                    COALESCE(SUM(CASE WHEN ar.is_paid = 1 THEN ar.amount ELSE 0 END), 0) as total_paid,
                    COALESCE(SUM(a.amount), 0) - COALESCE(SUM(CASE WHEN ar.is_paid = 1 THEN ar.amount ELSE 0 END), 0) as outstanding
                FROM staff s
                LEFT JOIN advances a ON s.id = a.staff_id
                LEFT JOIN advance_repayments ar ON a.id = ar.advance_id
            '''
            
            params = []
            if staff_id:
                query += ' WHERE s.id = ?'
                params.append(staff_id)
            
            query += ' GROUP BY s.id, s.name'
            query += ' HAVING outstanding > 0'
            
            return pd.read_sql_query(query, conn, params=params)

    def get_attendance_range(self, start_date, end_date):
        """Get attendance data for a date range."""
        try:
            query = """
                SELECT a.id, a.staff_id, a.date, a.is_present, a.is_holiday, s.name
                FROM attendance a
                JOIN staff s ON a.staff_id = s.id
                WHERE a.date BETWEEN ? AND ?
                ORDER BY a.date, s.name
            """
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (start_date, end_date))
                rows = cursor.fetchall()
            if not rows:
                return pd.DataFrame(columns=['id', 'staff_id', 'date', 'is_present', 'is_holiday', 'name'])
            return pd.DataFrame(rows, columns=['id', 'staff_id', 'date', 'is_present', 'is_holiday', 'name'])
        except Exception as e:
            print(f"Error getting attendance range: {e}")
            return pd.DataFrame(columns=['id', 'staff_id', 'date', 'is_present', 'is_holiday', 'name']) 