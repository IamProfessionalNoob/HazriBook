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
import io

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
    
    # Get today's attendance summary
    today_attendance = db.get_attendance(date.today())
    present_count = len(today_attendance[today_attendance['is_present']]) if not today_attendance.empty else 0
    total_count = len(today_attendance) if not today_attendance.empty else 1  # Prevent division by zero
    
    attendance_percentage = (present_count/total_count)*100 if total_count > 0 else 0
    
    # Get staff outstanding amounts
    outstanding_df = db.get_staff_outstanding()
    total_outstanding = outstanding_df['outstanding'].sum() if not outstanding_df.empty else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card(
            "Today's Attendance",
            f"{present_count}/{total_count} ({attendance_percentage:.1f}%)",
            "👥",
            color="#2e7d32"
        )
    
    with col2:
        render_metric_card(
            "Total Staff",
            str(total_count),
            "👨‍💼",
            color="#1976d2"
        )
    
    with col3:
        render_metric_card(
            "Total Outstanding",
            f"₹{total_outstanding:,.2f}",
            "💰",
            color="#d32f2f"
        )
    
    # Display staff with outstanding amounts
    if not outstanding_df.empty:
        st.subheader("Staff with Outstanding Amounts")
        st.dataframe(
            outstanding_df[['name', 'total_advance', 'total_paid', 'outstanding']],
            hide_index=True,
            column_config={
                "name": "Staff Name",
                "total_advance": st.column_config.NumberColumn(
                    "Total Advance",
                    format="₹%.2f"
                ),
                "total_paid": st.column_config.NumberColumn(
                    "Total Paid",
                    format="₹%.2f"
                ),
                "outstanding": st.column_config.NumberColumn(
                    "Outstanding",
                    format="₹%.2f"
                )
            }
        )
    
    # Recent Activity section
    st.markdown("""
        <h3>Recent Activity</h3>
    """, unsafe_allow_html=True)

def render_attendance():
    st.title("Attendance Management")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📝 Mark Attendance", "📊 Attendance Overview"])
    
    with tab1:
        # Date selection with calendar widget
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_date = st.date_input(
                "Select Date",
                value=date.today(),
                max_value=date.today()
            )
        with col2:
            if st.button("Today", use_container_width=True):
                selected_date = date.today()
                st.rerun()
        
        # Get attendance data for selected date
        attendance_df = db.get_attendance(selected_date)
        
        # Show summary metrics
        total_staff = len(attendance_df)
        present_count = len(attendance_df[attendance_df['is_present']])
        holiday_count = len(attendance_df[attendance_df['is_holiday']])
        absent_count = total_staff - present_count - holiday_count
        
        # Display metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card(
                "Total Staff",
                str(total_staff),
                "group",
                "#1976d2"
            )
        with col2:
            render_metric_card(
                "Present",
                str(present_count),
                "check_circle",
                "#2e7d32"
            )
        with col3:
            render_metric_card(
                "Absent",
                str(absent_count),
                "cancel",
                "#d32f2f"
            )
        with col4:
            render_metric_card(
                "On Holiday",
                str(holiday_count),
                "beach_access",
                "#ff9800"
            )
        
        # Create a form for marking attendance
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("attendance_form"):
            st.markdown("""
                <div class="dashboard-card">
                    <h3>Mark Attendance</h3>
            """, unsafe_allow_html=True)
            
            # Create a table-like layout
            for i in range(0, len(attendance_df), 2):
                col1, col2 = st.columns(2)
                
                # First staff member
                with col1:
                    if i < len(attendance_df):
                        staff = attendance_df.iloc[i]
                        st.markdown(f"""
                            <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                                <h4 style="margin-bottom: 0.5rem;">{staff['name']}</h4>
                        """, unsafe_allow_html=True)
                        
                        status = st.radio(
                            f"Status for {staff['name']}",
                            ["Present", "Absent", "Holiday"],
                            horizontal=True,
                            key=f"status_{staff['id']}",
                            index=0 if staff['is_present'] else (2 if staff['is_holiday'] else 1)
                        )
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Second staff member
                with col2:
                    if i + 1 < len(attendance_df):
                        staff = attendance_df.iloc[i + 1]
                        st.markdown(f"""
                            <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
                                <h4 style="margin-bottom: 0.5rem;">{staff['name']}</h4>
                        """, unsafe_allow_html=True)
                        
                        status = st.radio(
                            f"Status for {staff['name']}",
                            ["Present", "Absent", "Holiday"],
                            horizontal=True,
                            key=f"status_{staff['id']}",
                            index=0 if staff['is_present'] else (2 if staff['is_holiday'] else 1)
                        )
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Save Attendance", use_container_width=True)
            
            if submitted:
                for _, staff in attendance_df.iterrows():
                    status = st.session_state[f"status_{staff['id']}"]
                    is_present = status == "Present"
                    is_holiday = status == "Holiday"
                    db.mark_attendance(staff['id'], selected_date, is_present, is_holiday)
                
                st.success("Attendance saved successfully!")
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        # Attendance Overview
        st.markdown("""
            <div class="dashboard-card">
                <h3>Monthly Attendance Overview</h3>
        """, unsafe_allow_html=True)
        
        # Month selection
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox(
                "Year",
                options=range(date.today().year-1, date.today().year+2),
                index=1,
                key="overview_year"
            )
        with col2:
            selected_month = st.selectbox(
                "Month",
                options=range(1, 13),
                format_func=lambda x: calendar.month_name[x],
                index=date.today().month-1,
                key="overview_month"
            )
        
        # Get monthly attendance data
        start_date = date(selected_year, selected_month, 1)
        end_date = date(selected_year, selected_month, calendar.monthrange(selected_year, selected_month)[1])
        monthly_attendance = db.get_attendance_range(start_date, end_date)
        
        if not monthly_attendance.empty:
            # Prepare data for charts
            daily_stats = monthly_attendance.groupby('date').agg({
                'is_present': 'sum',
                'is_holiday': 'sum',
                'id': 'count'
            }).reset_index()
            daily_stats['absent'] = daily_stats['id'] - daily_stats['is_present'] - daily_stats['is_holiday']
            
            # Create attendance trend chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['is_present'],
                name='Present',
                line=dict(color='#2e7d32', width=2),
                fill='tonexty'
            ))
            
            fig.add_trace(go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['absent'],
                name='Absent',
                line=dict(color='#d32f2f', width=2),
                fill='tonexty'
            ))
            
            fig.add_trace(go.Scatter(
                x=daily_stats['date'],
                y=daily_stats['is_holiday'],
                name='Holiday',
                line=dict(color='#ff9800', width=2),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title='Daily Attendance Trend',
                xaxis_title='Date',
                yaxis_title='Number of Staff',
                hovermode='x unified',
                showlegend=True,
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Staff-wise attendance summary
            staff_summary = monthly_attendance.groupby('name').agg({
                'is_present': 'sum',
                'is_holiday': 'sum',
                'date': 'count'
            }).reset_index()
            
            staff_summary['absent'] = staff_summary['date'] - staff_summary['is_present'] - staff_summary['is_holiday']
            staff_summary['attendance_rate'] = (staff_summary['is_present'] / (staff_summary['date'] - staff_summary['is_holiday'])) * 100
            
            # Display staff summary
            st.markdown("<br><h4>Staff-wise Attendance Summary</h4>", unsafe_allow_html=True)
            st.dataframe(
                staff_summary,
                hide_index=True,
                column_config={
                    'name': 'Staff Name',
                    'is_present': 'Days Present',
                    'is_holiday': 'Holidays',
                    'absent': 'Days Absent',
                    'attendance_rate': st.column_config.NumberColumn(
                        'Attendance Rate',
                        format="%.1f%%"
                    )
                }
            )
            
            # Export and Share options
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                # Prepare Excel data
                def create_excel_report():
                    # Create a more detailed report
                    report_data = {
                        'Staff Name': staff_summary['name'],
                        'Days Present': staff_summary['is_present'],
                        'Days Absent': staff_summary['absent'],
                        'Holidays': staff_summary['is_holiday'],
                        'Attendance Rate (%)': staff_summary['attendance_rate'].round(2),
                        'Month': calendar.month_name[selected_month],
                        'Year': selected_year
                    }
                    df = pd.DataFrame(report_data)
                    
                    # Create Excel file in memory
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Attendance Summary', index=False)
                        workbook = writer.book
                        worksheet = writer.sheets['Attendance Summary']
                        
                        # Add formatting
                        header_format = workbook.add_format({
                            'bold': True,
                            'bg_color': '#2e7d32',
                            'font_color': 'white',
                            'border': 1
                        })
                        
                        # Format headers
                        for col_num, value in enumerate(df.columns.values):
                            worksheet.write(0, col_num, value, header_format)
                            worksheet.set_column(col_num, col_num, 15)
                        
                        # Add percentage format for attendance rate
                        percent_format = workbook.add_format({'num_format': '0.00%'})
                        worksheet.set_column('E:E', 15, percent_format)
                    
                    return output.getvalue()
                
                excel_data = create_excel_report()
                st.download_button(
                    label="📥 Download Excel Report",
                    data=excel_data,
                    file_name=f"attendance_report_{selected_year}_{calendar.month_name[selected_month]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                if st.button("Send WhatsApp Summary", use_container_width=True):
                    with st.spinner("Sending summaries..."):
                        success_count = 0
                        for _, row in staff_summary.iterrows():
                            success, _ = messaging.send_attendance_summary(
                                row['name'],
                                selected_year,
                                selected_month,
                                {
                                    'present': int(row['is_present']),
                                    'absent': int(row['absent']),
                                    'holidays': int(row['is_holiday']),
                                    'rate': float(row['attendance_rate'])
                                }
                            )
                            if success:
                                success_count += 1
                        
                        st.success(f"Successfully sent {success_count} out of {len(staff_summary)} summaries")
        else:
            st.info("No attendance data available for the selected month")
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_staff_management():
    st.title("Staff Management")
    
    # Add new staff
    with st.expander("➕ Add New Staff", expanded=True):
        st.markdown("""
            <div class="dashboard-card">
                <h3>New Staff Details</h3>
        """, unsafe_allow_html=True)
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name", placeholder="Enter staff name")
                phone = st.text_input("Phone Number", placeholder="Enter phone number")
            
            with col2:
                salary = st.number_input("Monthly Salary (₹)", min_value=0.0, step=1000.0)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Salary Cycle**")
                cycle_col1, cycle_col2 = st.columns(2)
                with cycle_col1:
                    cycle_start = st.number_input("Start Day", min_value=1, max_value=31, value=1)
                with cycle_col2:
                    cycle_end = st.number_input("End Day", min_value=1, max_value=31, value=31)
            
            if st.form_submit_button("Add Staff", use_container_width=True):
                if name and phone and salary:
                    db.add_staff(name, phone, salary, cycle_start, cycle_end)
                    st.success("Staff added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # View and manage staff
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Current Staff</h3>
    """, unsafe_allow_html=True)
    
    staff_df = db.get_all_staff()
    if not staff_df.empty:
        for _, staff in staff_df.iterrows():
            with st.expander(f"👤 {staff['name']} - ₹{staff['monthly_salary']:,.2f}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                        <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
                            <p><strong>Phone:</strong> {staff['phone']}</p>
                            <p><strong>Salary Cycle:</strong> {staff['salary_cycle_start']} to {staff['salary_cycle_end']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Salary History
                    st.subheader("Salary History")
                    salary_history = db.get_staff_salary_history(staff['id'])
                    if not salary_history.empty:
                        st.dataframe(
                            salary_history[['effective_from', 'effective_to', 'salary']],
                            hide_index=True,
                            column_config={
                                "effective_from": "From",
                                "effective_to": "To",
                                "salary": st.column_config.NumberColumn(
                                    "Salary",
                                    format="₹%.2f"
                                )
                            }
                        )
                    else:
                        st.info("No salary history available")
                
                with col2:
                    # Update Salary
                    with st.form(f"update_salary_{staff['id']}"):
                        st.subheader("Update Salary")
                        new_salary = st.number_input(
                            "New Salary (₹)",
                            min_value=0.0,
                            value=float(staff['monthly_salary']),
                            step=1000.0
                        )
                        effective_from = st.date_input("Effective From")
                        if st.form_submit_button("Update Salary", use_container_width=True):
                            db.update_staff_salary(staff['id'], new_salary, effective_from)
                            st.success("Salary updated successfully!")
                            st.rerun()
                    
                    # Salary Cycle Settings
                    st.subheader("Salary Cycle Settings")
                    cycle = db.get_staff_salary_cycle(staff['id'])
                    with st.form(f"update_cycle_{staff['id']}"):
                        cycle_col1, cycle_col2 = st.columns(2)
                        with cycle_col1:
                            start_day = st.number_input("Start Day", min_value=1, max_value=31, value=cycle['start'])
                        with cycle_col2:
                            end_day = st.number_input("End Day", min_value=1, max_value=31, value=cycle['end'])
                        if st.form_submit_button("Update Salary Cycle", use_container_width=True):
                            db.set_staff_salary_cycle(staff['id'], start_day, end_day)
                            st.success("Salary cycle updated successfully!")
                            st.rerun()
    else:
        st.info("No staff members found. Add your first staff member above.")
    
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
    with st.expander("💰 Add New Advance", expanded=True):
        st.markdown("""
            <div class="dashboard-card">
                <h3>New Advance Details</h3>
        """, unsafe_allow_html=True)
        
        with st.form("add_advance_form"):
            staff_df = db.get_all_staff()
            col1, col2 = st.columns(2)
            
            with col1:
                staff_id = st.selectbox(
                    "Select Staff",
                    staff_df['id'],
                    format_func=lambda x: staff_df[staff_df['id'] == x]['name'].iloc[0]
                )
                amount = st.number_input("Amount (₹)", min_value=0.0, step=1000.0)
            
            with col2:
                advance_date = st.date_input("Date")
                repayment_type = st.selectbox(
                    "Repayment Type",
                    ['OneTime', 'Weekly', 'Monthly'],
                    format_func=lambda x: {
                        'OneTime': 'One Time Payment',
                        'Weekly': 'Weekly Installments',
                        'Monthly': 'Monthly Installments'
                    }[x]
                )
            
            if repayment_type != 'OneTime':
                st.markdown("**Installment Details**")
                col1, col2 = st.columns(2)
                with col1:
                    emi_amount = st.number_input("EMI Amount (₹)", min_value=0.0, step=1000.0)
                with col2:
                    emi_count = st.number_input("Number of EMIs", min_value=1)
            
            if st.form_submit_button("Add Advance", use_container_width=True):
                if repayment_type == 'OneTime':
                    db.add_advance_with_emi(staff_id, amount, advance_date, repayment_type)
                else:
                    db.add_advance_with_emi(staff_id, amount, advance_date, repayment_type, emi_amount, emi_count)
                st.success("Advance added successfully!")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # View and manage advances
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="dashboard-card">
            <h3>Current Advances</h3>
    """, unsafe_allow_html=True)
    
    advances_df = db.get_all_advances()
    if not advances_df.empty:
        for _, advance in advances_df.iterrows():
            staff_name = staff_df[staff_df['id'] == advance['staff_id']]['name'].iloc[0]
            with st.expander(
                f"💵 {staff_name} - ₹{advance['amount']:,.2f} ({advance['repayment_type']})",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                        <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
                            <p><strong>Date:</strong> {advance['date']}</p>
                            <p><strong>Status:</strong> {advance['status']}</p>
                            <p><strong>Remaining Amount:</strong> ₹{advance['remaining_amount']:,.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if advance['repayment_type'] != 'OneTime':
                        st.markdown(f"""
                            <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 8px; margin-top: 1rem;">
                                <p><strong>EMI Amount:</strong> ₹{advance['emi_amount']:,.2f}</p>
                                <p><strong>Total EMIs:</strong> {advance['total_emi_count']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    # Add repayment
                    if advance['status'] == 'Active':
                        with st.form(f"add_repayment_{advance['id']}"):
                            st.subheader("Add Payment")
                            paid_amount = st.number_input(
                                "Payment Amount (₹)",
                                min_value=0.0,
                                max_value=float(advance['remaining_amount']),
                                step=1000.0
                            )
                            if st.form_submit_button("Add Payment", use_container_width=True):
                                db.update_advance_remaining(advance['id'], paid_amount)
                                st.success("Payment added successfully!")
                                st.rerun()
    else:
        st.info("No advances found. Add a new advance above.")
    
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
    
    # Salary Cycle Settings
    st.subheader("Salary Cycle Settings")
    cycle = db.get_salary_cycle()
    col1, col2 = st.columns(2)
    with col1:
        start_day = st.number_input("Salary Cycle Start Day", min_value=1, max_value=31, value=cycle['start'])
    with col2:
        end_day = st.number_input("Salary Cycle End Day", min_value=1, max_value=31, value=cycle['end'])
    
    if st.button("Update Salary Cycle"):
        db.set_salary_cycle(start_day, end_day)
        st.success("Salary cycle updated successfully!")

    # Working Days Setting
    st.subheader("Working Days Setting")
    working_days = st.number_input("Default Working Days per Month", min_value=1, max_value=31, value=26)
    if st.button("Update Working Days"):
        db.update_setting('working_days', str(working_days))
        st.success("Working days updated successfully!")

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
    # Auto-mark attendance for today if not already marked
    today = date.today()
    today_attendance = db.get_attendance(today)
    if today_attendance.empty:
        db.auto_mark_attendance(today)
    main_app() 