import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from database import Database
from messaging import MessagingService
import calendar
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import secrets

# Initialize database and messaging service
db = Database()
messaging = MessagingService()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

# Page config
st.set_page_config(
    page_title="HaazriBook - Staff Attendance & Salary Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set security headers
st.markdown("""
    <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Add session timeout
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
else:
    if datetime.now() - st.session_state.last_activity > timedelta(hours=1):
        st.session_state.clear()
        st.error("Session expired. Please login again.")
        st.stop()
    st.session_state.last_activity = datetime.now()

# Add this function to check if user is authenticated
def check_auth():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("Please login to access this page")
        st.stop()

# Import Google Fonts and Material Icons
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
""", unsafe_allow_html=True)

# Custom CSS with improved styling
st.markdown(f"""
    <style>
    /* Theme colors - Define these first */
    :root {{
        --primary: #2e7d32;
        --primary-light: #60ad5e;
        --primary-dark: #005005;
        --secondary: #6e6e6e;
        --background: #eef2f6;
        --surface: #ffffff;
        --text: #1a1f2f;
        --text-light: #4a5568;
        --accent: #009688;
        --error: #d32f2f;
        --success: #2e7d32;
        --border: #cfd8dc;
        --card-shadow: rgba(0, 0, 0, 0.1);
    }}
    
    /* Global styles */
    * {{
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
        color: var(--text);
    }}
    
    .stApp {{
        background-color: var(--background) !important;
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: #1a1f2f !important;
        border-right: 1px solid var(--border);
        box-shadow: 2px 0 8px var(--card-shadow);
    }}
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {{
        color: white !important;
    }}
    
    /* Card styling */
    .dashboard-card {{
        background: var(--surface);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px var(--card-shadow);
        margin-bottom: 2rem;
        border: 1px solid var(--border);
        color: var(--text) !important;
    }}
    
    .dashboard-card h3 {{
        color: var(--text) !important;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
    }}
    
    /* Form styling */
    [data-testid="stForm"] {{
        background-color: var(--surface) !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 4px 12px var(--card-shadow) !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {{
        background-color: #f8fafc !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: var(--text) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1) !important;
    }}
    
    /* Select boxes */
    .stSelectbox > div > div {{
        background-color: #f8fafc !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }}
    
    /* Data tables */
    .stDataFrame {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px var(--card-shadow) !important;
    }}
    
    .stDataFrame th {{
        background-color: #f1f5f9 !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        color: var(--text) !important;
        border-bottom: 2px solid var(--border) !important;
        text-transform: uppercase !important;
        font-size: 0.875rem !important;
    }}
    
    .stDataFrame td {{
        padding: 1rem !important;
        border-bottom: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: var(--primary) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-size: 0.875rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
    }}
    
    /* Force white text color for all button content */
    .stButton > button,
    .stButton > button span,
    .stButton > button p,
    .stButton > button div {{
        color: white !important;
    }}
    
    /* Style for button hover state */
    .stButton > button:hover {{
        background-color: var(--primary-dark) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
    }}
    
    /* Override any other color settings for button text */
    .stButton > button [data-testid="stMarkdownContainer"] * {{
        color: white !important;
    }}
    
    /* Login page specific styles */
    [data-testid="stForm"] {{
        background-color: var(--surface) !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 4px 12px var(--card-shadow) !important;
    }}
    
    /* Login form text */
    [data-testid="stForm"] label,
    [data-testid="stForm"] p,
    [data-testid="stForm"] span {{
        color: var(--text) !important;
    }}
    
    /* Login form inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input {{
        color: var(--text) !important;
        background-color: white !important;
    }}
    
    /* Login page title and subtitle */
    .login-title {{
        color: var(--text) !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .login-subtitle {{
        color: var(--text-light) !important;
        font-size: 1.1rem !important;
        margin-bottom: 2rem !important;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px var(--card-shadow);
        border: 1px solid var(--border);
        margin-bottom: 1rem;
    }}
    
    .metric-card h3 {{
        font-size: 1rem;
        color: var(--text-light);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }}
    
    .metric-card .value {{
        font-size: 2rem;
        font-weight: 600;
        color: var(--primary);
    }}
    
    /* Navigation menu */
    .nav-link {{
        padding: 0.75rem 1rem;
        color: rgba(255, 255, 255, 0.7) !important;
        text-decoration: none;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        transition: all 0.3s ease;
    }}
    
    .nav-link:hover {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
    }}
    
    .nav-link.active {{
        background-color: var(--primary);
        color: white !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text);
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    
    h1 {{
        font-size: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border);
        margin-bottom: 2rem;
    }}
    
    /* Labels */
    label {{
        color: var(--text) !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Form containers */
    [data-testid="column"] {{
        background: transparent !important;
        padding: 0.5rem !important;
    }}
    
    /* Alerts and messages */
    .stAlert {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 2px 4px var(--card-shadow) !important;
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--background);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--secondary);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary);
    }}
    
    /* Additional spacing utilities */
    .p-4 {{
        padding: 1.5rem !important;
    }}
    
    .mb-4 {{
        margin-bottom: 1.5rem !important;
    }}
    
    /* Fix for white text on white background */
    .stMarkdown {{
        color: var(--text) !important;
    }}
    
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    
    /* Fix for white headings */
    h1, h2, h3, h4, h5, h6 {{
        color: #1a1f2f !important;
        font-weight: 600 !important;
    }}
    
    .dashboard-card h3 {{
        color: #1a1f2f !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--border) !important;
    }}
    
    /* Fix for attendance checkboxes and labels */
    .stCheckbox {{
        color: #1a1f2f !important;
    }}
    
    .stCheckbox label {{
        color: #1a1f2f !important;
        font-weight: 500 !important;
    }}
    
    /* Fix for white text in cards */
    .dashboard-card {{
        color: #1a1f2f !important;
    }}
    
    /* Fix for page title */
    [data-testid="stMarkdownContainer"] h1 {{
        color: #1a1f2f !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-bottom: 2rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid var(--border) !important;
    }}
    
    /* Fix for any other text elements */
    p, span, label {{
        color: #1a1f2f !important;
    }}
    </style>
""", unsafe_allow_html=True)

def render_metric_card(title, value, icon, color="#2e7d32"):
    st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{title}</h3>
                <i class="material-icons-round" style="color: {color}; font-size: 2rem;">{icon}</i>
            </div>
            <div class="value" style="color: {color};">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <div style="display: inline-block; margin-bottom: 1rem;">
                    <svg width="80" height="80" viewBox="0 0 80 80">
                        <rect width="80" height="80" fill="none"/>
                        <path d="M20 15 H60 Q65 15 65 20 V60 Q65 65 60 65 H20 Q15 65 15 60 V20 Q15 15 20 15" 
                              stroke="#2e7d32" stroke-width="3" fill="none"/>
                        <path d="M25 40 L35 50 L55 30" stroke="#2e7d32" stroke-width="3" fill="none"/>
                    </svg>
                </div>
                <h1 class="login-title">HaazriBook</h1>
                <p class="login-subtitle">Staff Attendance & Salary Manager</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
            st.text_input("Username", key="login_username")
            st.text_input("Password", type="password", key="login_password")
            
            if st.form_submit_button("Login", use_container_width=True):
                username = st.session_state.login_username
                password = st.session_state.login_password
                role = db.verify_user(username, password)
                if role:
                    st.session_state.authenticated = True
                    st.session_state.user_role = role
                    st.session_state.username = username
                    st.session_state.last_activity = datetime.now()
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def main_app():
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="color: var(--primary); margin-bottom: 0;">HaazriBook</h2>
                <p style="color: var(--text-light); font-size: 0.875rem;">
                    Logged in as: {st.session_state.username}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        if st.session_state.user_role == "admin":
            selected = option_menu(
                menu_title=None,
                options=[
                    "Dashboard", "Staff Management", "Attendance",
                    "Holidays", "Advance Payments", "Reports",
                    "User Management", "Settings"
                ],
                icons=[
                    "speedometer2", "people", "calendar-check",
                    "calendar-event", "cash-coin", "file-earmark-text",
                    "person-gear", "gear"
                ],
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "icon": {"font-size": "1rem"},
                    "nav-link": {
                        "font-size": "0.9rem",
                        "text-align": "left",
                        "margin": "0.5rem 0",
                        "padding": "0.5rem 1rem",
                        "--hover-color": "rgba(46, 125, 50, 0.1)"
                    },
                    "nav-link-selected": {"background-color": "#2e7d32"}
                }
            )
        elif st.session_state.user_role == "manager":
            selected = option_menu(
                menu_title=None,
                options=[
                    "Dashboard", "Attendance", "Holidays",
                    "Advance Payments", "Reports"
                ],
                icons=[
                    "speedometer2", "calendar-check", "calendar-event",
                    "cash-coin", "file-earmark-text"
                ],
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "icon": {"font-size": "1rem"},
                    "nav-link": {
                        "font-size": "0.9rem",
                        "text-align": "left",
                        "margin": "0.5rem 0",
                        "padding": "0.5rem 1rem",
                        "--hover-color": "rgba(46, 125, 50, 0.1)"
                    },
                    "nav-link-selected": {"background-color": "#2e7d32"}
                }
            )
        else:  # viewer
            selected = option_menu(
                menu_title=None,
                options=["Dashboard", "Reports"],
                icons=["speedometer2", "file-earmark-text"],
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "icon": {"font-size": "1rem"},
                    "nav-link": {
                        "font-size": "0.9rem",
                        "text-align": "left",
                        "margin": "0.5rem 0",
                        "padding": "0.5rem 1rem",
                        "--hover-color": "rgba(46, 125, 50, 0.1)"
                    },
                    "nav-link-selected": {"background-color": "#2e7d32"}
                }
            )
        
        if st.button("Logout", key="logout"):
            logout()
    
    # Main content area
    if selected == "Dashboard":
        render_dashboard()
    elif selected == "Staff Management":
        render_staff_management()
    elif selected == "Attendance":
        render_attendance()
    elif selected == "Holidays":
        render_holidays()
    elif selected == "Advance Payments":
        render_advance_payments()
    elif selected == "Reports":
        render_reports()
    elif selected == "User Management":
        render_user_management()
    elif selected == "Settings":
        render_settings()

def render_dashboard():
    st.title("Dashboard")
    
    # Get current stats
    stats = db.get_dashboard_stats()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Total Staff",
            stats['total_staff'],
            "group",
            "#2e7d32"
        )
    
    with col2:
        render_metric_card(
            "Today's Attendance",
            f"{stats['avg_attendance']:.1f}%",
            "how_to_reg",
            "#1976d2"
        )
    
    with col3:
        render_metric_card(
            "Monthly Salary",
            f"₹{stats['total_salary']:,.2f}",
            "payments",
            "#d32f2f"
        )
    
    with col4:
        render_metric_card(
            "Pending Advances",
            f"₹{stats['total_advance']:,.2f}",
            "account_balance",
            "#f57c00"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="dashboard-card">
                <h3>Attendance Trend</h3>
        """, unsafe_allow_html=True)
        
        # Get attendance data for the last 6 months
        today = date.today()
        months_data = []
        
        for i in range(6):
            month = today.month - i
            year = today.year
            
            if month <= 0:
                month += 12
                year -= 1
            
            month_stats = db.get_dashboard_stats(year, month)
            months_data.append({
                'Month': f"{calendar.month_abbr[month]} {year}",
                'Attendance': month_stats['avg_attendance']
            })
        
        months_data.reverse()
        df = pd.DataFrame(months_data)
        
        fig = px.line(
            df,
            x='Month',
            y='Attendance',
            markers=True,
            line_shape="spline"
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis_title="Attendance %",
            xaxis_title=None,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        fig.update_traces(
            line_color="#2e7d32",
            marker=dict(size=8)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="dashboard-card">
                <h3>Recent Activity</h3>
        """, unsafe_allow_html=True)
        
        # Get today's attendance summary
        today_attendance = db.get_attendance(date.today())
        present_count = len(today_attendance[today_attendance['is_present']]) if not today_attendance.empty else 0
        total_count = len(today_attendance) if not today_attendance.empty else 1  # Prevent division by zero
        
        attendance_percentage = (present_count/total_count)*100 if total_count > 0 else 0
        
        st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <p style="color: var(--text-light); margin-bottom: 0.5rem;">Today's Attendance</p>
                <div style="display: flex; align-items: center;">
                    <div style="flex-grow: 1; height: 8px; background-color: #e8f5e9; border-radius: 4px;">
                        <div style="width: {attendance_percentage}%; height: 100%; background-color: #2e7d32; border-radius: 4px;"></div>
                    </div>
                    <span style="margin-left: 1rem; color: var(--text); font-weight: 500;">
                        {present_count}/{total_count}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Recent advances
        st.markdown("<h4>Recent Advances</h4>", unsafe_allow_html=True)
        pending_advances = db.get_pending_advances()
        
        if not pending_advances.empty:
            for _, row in pending_advances.head(5).iterrows():
                st.markdown(f"""
                    <div style="padding: 0.75rem; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <p style="margin: 0; color: var(--text); font-weight: 500;">{row['staff_name']}</p>
                                <small style="color: var(--text-light);">
                                    {row['pending_installments']} installments remaining
                                </small>
                            </div>
                            <div style="text-align: right;">
                                <p style="margin: 0; color: #d32f2f; font-weight: 500;">
                                    ₹{row['pending_amount']:,.2f}
                                </p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No pending advances")
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_attendance():
    st.title("Daily Attendance")
    
    # Date selection with calendar view
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("""
            <div class="dashboard-card">
                <h3>Select Date</h3>
        """, unsafe_allow_html=True)
        
        # Calendar view
        today = date.today()
        selected_date = st.date_input(
            "Date",
            value=today,
            max_value=today,
            key="attendance_date"
        )
        
        # Check if selected date is a holiday
        is_holiday = db.is_holiday(selected_date)
        if is_holiday:
            holiday_info = db.get_holidays(selected_date.year, selected_date.month)
            holiday_name = holiday_info[holiday_info['date'] == str(selected_date)]['name'].iloc[0]
            st.markdown(f"""
                <div style="background-color: #e8f5e9; color: #2e7d32; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <i class="material-icons-round" style="vertical-align: middle; margin-right: 0.5rem;">event</i>
                    Holiday: {holiday_name}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="dashboard-card">
                <h3>Mark Attendance</h3>
        """, unsafe_allow_html=True)
        
        # Get attendance data
        attendance_df = db.get_attendance(selected_date)
        
        if not attendance_df.empty:
            with st.form("attendance_form", clear_on_submit=False):
                # Select all checkbox
                select_all = st.checkbox(
                    "Select All",
                    value=False,
                    key="select_all"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Create columns for better layout
                cols = st.columns(3)
                attendance_data = {}
                
                for idx, row in attendance_df.iterrows():
                    col_idx = idx % 3
                    with cols[col_idx]:
                        default_value = True if select_all else bool(row['is_present'])
                        attendance_data[row['id']] = st.checkbox(
                            row['name'],
                            value=default_value,
                            key=f"att_{row['id']}"
                        )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("Save Attendance", use_container_width=True):
                    for staff_id, is_present in attendance_data.items():
                        db.mark_attendance(staff_id, selected_date, is_present)
                    st.success("Attendance saved successfully!")
                    st.rerun()
        else:
            st.info("No staff members found. Please add staff first.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Monthly overview
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Monthly Overview</h3>
    """, unsafe_allow_html=True)
    
    # Month and year selection
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox(
            "Year",
            options=range(today.year-1, today.year+1),
            index=1,
            key="overview_year"
        )
    
    with col2:
        selected_month = st.selectbox(
            "Month",
            options=range(1, 13),
            format_func=lambda x: calendar.month_name[x],
            index=today.month-1,
            key="overview_month"
        )
    
    # Get monthly attendance data
    monthly_df = db.get_monthly_attendance(selected_year, selected_month)
    
    if not monthly_df.empty:
        # Create a styled table view
        st.dataframe(
            monthly_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to Excel", use_container_width=True):
                # Add export functionality
                pass
        
        with col2:
            if st.button("Send Summary to Staff", use_container_width=True):
                for _, row in monthly_df.iterrows():
                    success, message = messaging.send_attendance_summary(
                        row['id'],
                        selected_year,
                        selected_month
                    )
                    if success:
                        st.success(f"Sent to {row['name']}")
                    else:
                        st.error(f"Failed to send to {row['name']}: {message}")
    else:
        st.info("No attendance data available for the selected month.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_staff_management():
    st.title("Staff Management")
    
    # Add new staff form
    st.markdown("""
        <div class="dashboard-card">
            <h3>Add New Staff</h3>
    """, unsafe_allow_html=True)
    
    with st.form("add_staff_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name")
        with col2:
            phone = st.text_input("Phone")
        with col3:
            monthly_salary = st.number_input("Monthly Salary", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("Add Staff", use_container_width=True):
            if name and monthly_salary > 0:
                db.add_staff(name, phone, monthly_salary)
                st.success(f"Added {name} to staff")
                st.rerun()
            else:
                st.error("Please fill in all required fields")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Staff list
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Staff List</h3>
    """, unsafe_allow_html=True)
    
    staff_df = db.get_all_staff()
    
    if not staff_df.empty:
        # Display staff data in an editable format
        edited_df = st.data_editor(
            staff_df,
            hide_index=True,
            column_config={
                "id": None,  # Hide ID column
                "created_at": None,  # Hide timestamp
                "name": "Name",
                "phone": "Phone",
                "monthly_salary": st.column_config.NumberColumn(
                    "Monthly Salary",
                    format="₹%.2f"
                )
            },
            disabled=["id"],
            key="staff_editor"
        )
        
        # Check for changes and update
        if not edited_df.equals(staff_df):
            for idx, row in edited_df.iterrows():
                original = staff_df.loc[idx]
                if not row.equals(original):
                    db.update_staff(
                        row['id'],
                        row['name'],
                        row['phone'],
                        row['monthly_salary']
                    )
            st.success("Staff information updated")
            st.rerun()
        
        # Delete staff option
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            staff_to_delete = st.selectbox(
                "Select staff to delete",
                options=staff_df['id'].tolist(),
                format_func=lambda x: staff_df[staff_df['id'] == x]['name'].iloc[0]
            )
        
        with col2:
            if st.button("Delete Selected Staff", type="primary", use_container_width=True):
                if st.session_state.user_role == "admin":
                    db.delete_staff(staff_to_delete)
                    st.success("Staff deleted successfully")
                    st.rerun()
                else:
                    st.error("Only admin can delete staff")
    else:
        st.info("No staff members found. Add staff using the form above.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_holidays():
    st.title("Holiday Management")
    
    # Add new holiday
    st.markdown("""
        <div class="dashboard-card">
            <h3>Add New Holiday</h3>
    """, unsafe_allow_html=True)
    
    with st.form("add_holiday_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            holiday_date = st.date_input("Date")
        with col2:
            holiday_name = st.text_input("Holiday Name")
        
        if st.form_submit_button("Add Holiday", use_container_width=True):
            if holiday_name:
                db.add_holiday(holiday_date, holiday_name)
                st.success(f"Added {holiday_name} to holidays")
                st.rerun()
            else:
                st.error("Please enter a holiday name")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Holiday list
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Holiday List</h3>
    """, unsafe_allow_html=True)
    
    # Year and month selection
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox(
            "Year",
            options=range(date.today().year-1, date.today().year+2),
            index=1
        )
    
    with col2:
        selected_month = st.selectbox(
            "Month",
            options=range(1, 13),
            format_func=lambda x: calendar.month_name[x],
            index=date.today().month-1
        )
    
    holidays_df = db.get_holidays(selected_year, selected_month)
    
    if not holidays_df.empty:
        # Display holidays
        st.dataframe(
            holidays_df,
            hide_index=True,
            column_config={
                "id": None,
                "created_at": None,
                "date": "Date",
                "name": "Holiday Name"
            },
            use_container_width=True
        )
        
        # Delete holiday option
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            holiday_to_delete = st.selectbox(
                "Select holiday to delete",
                options=holidays_df['id'].tolist(),
                format_func=lambda x: f"{holidays_df[holidays_df['id'] == x]['name'].iloc[0]} ({holidays_df[holidays_df['id'] == x]['date'].iloc[0]})"
            )
        
        with col2:
            if st.button("Delete Selected Holiday", type="primary", use_container_width=True):
                if st.session_state.user_role == "admin":
                    db.delete_holiday(holiday_to_delete)
                    st.success("Holiday deleted successfully")
                    st.rerun()
                else:
                    st.error("Only admin can delete holidays")
    else:
        st.info("No holidays found for the selected month")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_advance_payments():
    st.title("Advance Payments")
    
    # Add new advance
    st.markdown("""
        <div class="dashboard-card">
            <h3>New Advance Payment</h3>
    """, unsafe_allow_html=True)
    
    with st.form("add_advance_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        staff_df = db.get_all_staff()
        
        with col1:
            staff_id = st.selectbox(
                "Staff Member",
                options=staff_df['id'].tolist(),
                format_func=lambda x: staff_df[staff_df['id'] == x]['name'].iloc[0]
            )
        
        with col2:
            amount = st.number_input("Amount", min_value=0.0, step=1000.0)
        
        with col3:
            repayment_months = st.number_input(
                "Repayment Months",
                min_value=1,
                max_value=12,
                value=1
            )
        
        if st.form_submit_button("Add Advance", use_container_width=True):
            if amount > 0:
                db.add_advance(staff_id, amount, date.today(), repayment_months)
                st.success("Advance payment added successfully")
                
                # Send notification
                messaging.send_advance_notification(staff_id, amount, date.today())
                st.rerun()
            else:
                st.error("Please enter a valid amount")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Pending advances
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Pending Advances</h3>
    """, unsafe_allow_html=True)
    
    pending_advances = db.get_pending_advances()
    
    if not pending_advances.empty:
        st.dataframe(
            pending_advances,
            hide_index=True,
            column_config={
                "advance_id": None,
                "staff_id": None,
                "staff_name": "Staff Name",
                "total_amount": st.column_config.NumberColumn(
                    "Total Amount",
                    format="₹%.2f"
                ),
                "advance_date": "Date",
                "pending_amount": st.column_config.NumberColumn(
                    "Pending Amount",
                    format="₹%.2f"
                ),
                "pending_installments": "Remaining Installments"
            },
            use_container_width=True
        )
    else:
        st.info("No pending advances")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_reports():
    st.title("Reports")
    
    # Month selection
    st.markdown("""
        <div class="dashboard-card">
            <h3>Monthly Report</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox(
            "Year",
            options=range(date.today().year-1, date.today().year+1),
            index=1,
            key="report_year"
        )
    
    with col2:
        selected_month = st.selectbox(
            "Month",
            options=range(1, 13),
            format_func=lambda x: calendar.month_name[x],
            index=date.today().month-1,
            key="report_month"
        )
    
    # Generate report
    report_df = db.get_monthly_report(selected_year, selected_month)
    
    if not report_df.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_salary = report_df['calculated_salary'].sum()
            st.metric(
                "Total Salary",
                f"₹{total_salary:,.2f}"
            )
        
        with col2:
            total_advance = report_df['total_advance'].sum()
            st.metric(
                "Total Advances",
                f"₹{total_advance:,.2f}"
            )
        
        with col3:
            final_payout = report_df['final_salary'].sum()
            st.metric(
                "Final Payout",
                f"₹{final_payout:,.2f}"
            )
        
        # Detailed report
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            report_df,
            hide_index=True,
            column_config={
                "id": None,
                "phone": None,
                "created_at": None,
                "name": "Staff Name",
                "monthly_salary": st.column_config.NumberColumn(
                    "Monthly Salary",
                    format="₹%.2f"
                ),
                "days_present": "Days Present",
                "calculated_salary": st.column_config.NumberColumn(
                    "Calculated Salary",
                    format="₹%.2f"
                ),
                "total_advance": st.column_config.NumberColumn(
                    "Advance Deduction",
                    format="₹%.2f"
                ),
                "final_salary": st.column_config.NumberColumn(
                    "Final Salary",
                    format="₹%.2f"
                )
            },
            use_container_width=True
        )
        
        # Export options
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to Excel", use_container_width=True):
                # Add export functionality
                pass
        
        with col2:
            if st.button("Send Reports to Staff", use_container_width=True):
                for _, row in report_df.iterrows():
                    success, message = messaging.send_attendance_summary(
                        row['id'],
                        selected_year,
                        selected_month
                    )
                    if success:
                        st.success(f"Sent to {row['name']}")
                    else:
                        st.error(f"Failed to send to {row['name']}: {message}")
    else:
        st.info("No data available for the selected month")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_user_management():
    st.title("User Management")
    
    if st.session_state.user_role != "admin":
        st.error("Only admin users can access this page")
        return
    
    # Add new user
    st.markdown("""
        <div class="dashboard-card">
            <h3>Add New User</h3>
    """, unsafe_allow_html=True)
    
    with st.form("add_user_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
        with col3:
            role = st.selectbox(
                "Role",
                options=["admin", "manager", "viewer"]
            )
        
        if st.form_submit_button("Add User", use_container_width=True):
            if username and password:
                db.create_user(username, password, role)
                st.success(f"Added user {username}")
                st.rerun()
            else:
                st.error("Please fill in all fields")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # User list
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>User List</h3>
    """, unsafe_allow_html=True)
    
    users_df = db.get_all_users()
    
    if not users_df.empty:
        st.dataframe(
            users_df,
            hide_index=True,
            column_config={
                "id": None,
                "username": "Username",
                "role": "Role"
            },
            use_container_width=True
        )
        
        # Delete user option
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            user_to_delete = st.selectbox(
                "Select user to delete",
                options=users_df[users_df['username'] != 'admin']['id'].tolist(),
                format_func=lambda x: users_df[users_df['id'] == x]['username'].iloc[0]
            )
        
        with col2:
            if st.button("Delete Selected User", type="primary", use_container_width=True):
                db.delete_user(user_to_delete)
                st.success("User deleted successfully")
                st.rerun()
    else:
        st.info("No users found")
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_settings():
    st.title("Settings")
    
    if st.session_state.user_role != "admin":
        st.error("Only admin users can access this page")
        return
    
    # Working days settings
    st.markdown("""
        <div class="dashboard-card">
            <h3>Working Days</h3>
    """, unsafe_allow_html=True)
    
    working_days = db.get_working_days()
    
    new_working_days = st.number_input(
        "Number of working days per month",
        min_value=1,
        max_value=31,
        value=working_days
    )
    
    if new_working_days != working_days:
        if st.button("Save Working Days", use_container_width=True):
            db.set_working_days(new_working_days)
            st.success("Working days updated successfully")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Theme settings
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Theme Settings</h3>
    """, unsafe_allow_html=True)
    
    theme = st.selectbox(
        "Select theme",
        options=["light", "dark"],
        index=0 if st.session_state.theme == "light" else 1
    )
    
    if theme != st.session_state.theme:
        if st.button("Apply Theme", use_container_width=True):
            st.session_state.theme = theme
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Messaging settings
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Messaging Settings</h3>
            <p>Configure WhatsApp/SMS notifications</p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        twilio_sid = st.text_input(
            "Twilio Account SID",
            value=db.get_setting('twilio_sid', ''),
            type="password"
        )
    
    with col2:
        twilio_token = st.text_input(
            "Twilio Auth Token",
            value=db.get_setting('twilio_token', ''),
            type="password"
        )
    
    twilio_number = st.text_input(
        "Twilio Phone Number",
        value=db.get_setting('twilio_number', '')
    )
    
    if st.button("Save Messaging Settings", use_container_width=True):
        db.set_setting('twilio_sid', twilio_sid)
        db.set_setting('twilio_token', twilio_token)
        db.set_setting('twilio_number', twilio_number)
        st.success("Messaging settings saved successfully")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Theme switch
st.markdown("""
    <div class="theme-switch" onclick="switchTheme()">
        <i class="material-icons-round" style="font-size: 1.5rem;">dark_mode</i>
    </div>
    
    <script>
    function switchTheme() {
        // Theme switching logic
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        location.reload();
    }
    </script>
""", unsafe_allow_html=True)

# Add logout functionality
def logout():
    st.session_state.clear()
    st.experimental_rerun()

# Main application flow
if not st.session_state.authenticated:
    login_page()
else:
    main_app() 