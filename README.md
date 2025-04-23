# HaazriBook - Staff Attendance & Salary Manager

A streamlined web application for managing staff attendance, salary calculations, and advance payments.

## Features

- Staff Management
- Daily Attendance Tracking
- Holiday Management
- Advance Payment Management
- Monthly Reports
- Multi-user Access with Role-based Permissions
- Dashboard with Real-time Analytics

## Local Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Default Login Credentials

- Username: admin
- Password: admin

## Deployment

### Option 1: Streamlit Cloud (Recommended)

1. Push your code to a GitHub repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Deploy your app by selecting your repository
5. The app will be automatically deployed and accessible via a public URL

### Option 2: Local Server

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   streamlit run app.py --server.port 8080
   ```

## Database

The application uses SQLite for data storage. The database file (`staff.db`) will be created automatically when the application runs for the first time.

## Security Notes

1. Change the default admin password after first login
2. Backup the `staff.db` file regularly
3. Keep your deployment credentials secure

## Support

For any issues or questions, please open an issue in the GitHub repository. 