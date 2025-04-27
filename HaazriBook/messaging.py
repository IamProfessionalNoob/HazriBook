import os
from twilio.rest import Client
from database import Database

class MessagingService:
    def __init__(self):
        self.db = Database()
        self.twilio_account_sid = self.db.get_setting('twilio_account_sid')
        self.twilio_auth_token = self.db.get_setting('twilio_auth_token')
        self.twilio_from_number = self.db.get_setting('twilio_from_number')
        
        if self.twilio_account_sid and self.twilio_auth_token:
            self.client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.client = None
    
    def is_configured(self):
        return self.client is not None
    
    def configure(self, account_sid, auth_token, from_number):
        self.db.set_setting('twilio_account_sid', account_sid)
        self.db.set_setting('twilio_auth_token', auth_token)
        self.db.set_setting('twilio_from_number', from_number)
        
        self.twilio_account_sid = account_sid
        self.twilio_auth_token = auth_token
        self.twilio_from_number = from_number
        
        self.client = Client(account_sid, auth_token)
    
    def send_message(self, to_number, message):
        if not self.is_configured():
            return False, "Twilio is not configured. Please set up your Twilio credentials in the settings."
        
        try:
            self.client.messages.create(
                body=message,
                from_=self.twilio_from_number,
                to=to_number
            )
            return True, "Message sent successfully."
        except Exception as e:
            return False, f"Failed to send message: {str(e)}"
    
    def send_attendance_summary(self, staff_id, year, month):
        """Send monthly attendance summary to a staff member"""
        staff_df = self.db.get_all_staff()
        staff = staff_df[staff_df['id'] == staff_id].iloc[0]
        
        if not staff['phone']:
            return False, "Staff member does not have a phone number."
        
        # Get attendance data
        report_df = self.db.get_monthly_report(year, month)
        staff_report = report_df[report_df['staff_id'] == staff_id].iloc[0]
        
        # Format message
        message = (
            f"Dear {staff['name']},\n\n"
            f"Your attendance summary for {year}-{month:02d}:\n"
            f"You were present on {int(staff_report['days_present'])} days.\n"
            f"Salary: ₹{staff_report['calculated_salary']:,.2f}\n"
            f"Advance: ₹{staff_report['total_advance']:,.2f}\n"
            f"Final: ₹{staff_report['final_salary']:,.2f}\n\n"
            f"Thank you for your hard work!"
        )
        
        return self.send_message(staff['phone'], message)
    
    def send_advance_notification(self, staff_id, amount, date):
        """Send notification about a new advance payment"""
        staff_df = self.db.get_all_staff()
        staff = staff_df[staff_df['id'] == staff_id].iloc[0]
        
        if not staff['phone']:
            return False, "Staff member does not have a phone number."
        
        # Format message
        message = (
            f"Dear {staff['name']},\n\n"
            f"An advance payment of ₹{amount:,.2f} has been recorded on {date}.\n"
            f"This will be deducted from your salary.\n\n"
            f"Thank you!"
        )
        
        return self.send_message(staff['phone'], message)
    
    def send_repayment_reminder(self, staff_id, amount, due_date):
        """Send reminder about pending advance repayment"""
        staff_df = self.db.get_all_staff()
        staff = staff_df[staff_df['id'] == staff_id].iloc[0]
        
        if not staff['phone']:
            return False, "Staff member does not have a phone number."
        
        # Format message
        message = (
            f"Dear {staff['name']},\n\n"
            f"This is a reminder that you have an advance repayment of ₹{amount:,.2f} "
            f"due on {due_date}.\n\n"
            f"Please ensure this is deducted from your salary.\n\n"
            f"Thank you!"
        )
        
        return self.send_message(staff['phone'], message) 