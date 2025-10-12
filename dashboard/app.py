"""
Streamlit Dashboard for GhostAI DLP SDK
Real-time monitoring and analytics for DLP scan results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Page configuration
st.set_page_config(
    page_title="GhostAI DLP Dashboard",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .alert-low {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def get_database_connection():
    """Get database connection."""
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://ghostai:ghostai123@db:5432/ghostai"
    )
    try:
        engine = create_engine(database_url)
        return engine
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def load_scan_data(engine, hours: int = 24):
    """Load scan data from database."""
    try:
        query = text("""
            SELECT 
                id, session_id, score, flags, severity, environment,
                latency_ms, user_agent, ip_address, created_at
            FROM dlp_findings 
            WHERE created_at >= NOW() - INTERVAL ':hours hours'
            ORDER BY created_at DESC
        """)
        
        df = pd.read_sql(query, engine, params={"hours": hours})
        return df
    except SQLAlchemyError as e:
        st.error(f"Database query failed: {e}")
        return pd.DataFrame()

def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">🕵️‍♂️ GhostAI DLP Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("📊 Dashboard Controls")
    
    # Time range selector
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days"],
        index=2
    )
    
    time_mapping = {
        "Last 1 hour": 1,
        "Last 6 hours": 6,
        "Last 24 hours": 24,
        "Last 7 days": 168
    }
    
    hours = time_mapping[time_range]
    
    # Environment filter
    environment_filter = st.sidebar.multiselect(
        "Environment",
        ["docker", "local", "kubernetes", "aws_lambda", "gcp"],
        default=["docker", "local", "kubernetes", "aws_lambda", "gcp"]
    )
    
    # Get database connection
    engine = get_database_connection()
    if not engine:
        st.error("❌ Cannot connect to database. Please check your connection settings.")
        return
    
    # Load data
    with st.spinner("Loading scan data..."):
        df = load_scan_data(engine, hours)
    
    if df.empty:
        st.warning("⚠️ No scan data found for the selected time range.")
        return
    
    # Filter by environment
    if environment_filter:
        df = df[df['environment'].isin(environment_filter)]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_scans = len(df)
        st.metric("Total Scans", total_scans)
    
    with col2:
        high_risk_scans = len(df[df['score'] >= 0.7])
        st.metric("High Risk Scans", high_risk_scans, delta=f"{high_risk_scans/total_scans*100:.1f}%" if total_scans > 0 else "0%")
    
    with col3:
        avg_latency = df['latency_ms'].mean() if not df.empty else 0
        st.metric("Avg Latency", f"{avg_latency:.1f}ms")
    
    with col4:
        unique_sessions = df['session_id'].nunique() if not df.empty else 0
        st.metric("Active Sessions", unique_sessions)
    
    # Charts section
    st.header("📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        st.subheader("Risk Score Distribution")
        fig_score = px.histogram(
            df, 
            x='score', 
            nbins=20,
            title="Distribution of Risk Scores",
            labels={'score': 'Risk Score', 'count': 'Number of Scans'}
        )
        fig_score.update_layout(showlegend=False)
        st.plotly_chart(fig_score, use_container_width=True)
    
    with col2:
        # Severity breakdown
        st.subheader("Severity Breakdown")
        severity_counts = df['severity'].value_counts()
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Scans by Severity Level"
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    # Time series
    st.subheader("📊 Scan Activity Over Time")
    
    # Resample data by hour for time series
    df_time = df.copy()
    df_time['created_at'] = pd.to_datetime(df_time['created_at'])
    df_time.set_index('created_at', inplace=True)
    
    hourly_scans = df_time.resample('H').size()
    hourly_high_risk = df_time[df_time['score'] >= 0.7].resample('H').size()
    
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=hourly_scans.index,
        y=hourly_scans.values,
        mode='lines+markers',
        name='Total Scans',
        line=dict(color='#1f77b4')
    ))
    fig_time.add_trace(go.Scatter(
        x=hourly_high_risk.index,
        y=hourly_high_risk.values,
        mode='lines+markers',
        name='High Risk Scans',
        line=dict(color='#ff4444')
    ))
    
    fig_time.update_layout(
        title="Scan Activity Over Time",
        xaxis_title="Time",
        yaxis_title="Number of Scans",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Recent scans table
    st.header("🔍 Recent Scans")
    
    # Display options
    col1, col2 = st.columns([3, 1])
    with col1:
        show_columns = st.multiselect(
            "Select columns to display",
            ['session_id', 'score', 'flags', 'severity', 'environment', 'latency_ms', 'created_at'],
            default=['session_id', 'score', 'flags', 'severity', 'environment', 'latency_ms', 'created_at']
        )
    
    with col2:
        max_rows = st.number_input("Max rows", min_value=10, max_value=1000, value=100)
    
    # Display table
    display_df = df[show_columns].head(max_rows)
    
    # Color code rows by severity
    def highlight_severity(row):
        if row['severity'] == 'Critical':
            return ['background-color: #ffebee'] * len(row)
        elif row['severity'] == 'High':
            return ['background-color: #fff3e0'] * len(row)
        elif row['severity'] == 'Medium':
            return ['background-color: #f3e5f5'] * len(row)
        else:
            return ['background-color: #e8f5e8'] * len(row)
    
    styled_df = display_df.style.apply(highlight_severity, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    # Environment breakdown
    st.header("🌍 Environment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scans by Environment")
        env_counts = df['environment'].value_counts()
        fig_env = px.bar(
            x=env_counts.index,
            y=env_counts.values,
            title="Scan Count by Environment",
            labels={'x': 'Environment', 'y': 'Number of Scans'}
        )
        st.plotly_chart(fig_env, use_container_width=True)
    
    with col2:
        st.subheader("Avg Latency by Environment")
        env_latency = df.groupby('environment')['latency_ms'].mean().reset_index()
        fig_latency = px.bar(
            env_latency,
            x='environment',
            y='latency_ms',
            title="Average Latency by Environment",
            labels={'environment': 'Environment', 'latency_ms': 'Average Latency (ms)'}
        )
        st.plotly_chart(fig_latency, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**GhostAI DLP SDK Dashboard** | Built with Streamlit and Plotly")

if __name__ == "__main__":
    main()
