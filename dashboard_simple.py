
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
import json

# Page config
st.set_page_config(
    page_title="GhostAI firewall Dashboard",
    page_icon="🔍",
    layout="wide"
)

def load_data():
    """Load data from SQLite database"""
    try:
        conn = sqlite3.connect('data/ghostai_firewall.db')
        df = pd.read_sql_query('''
            SELECT * FROM dlp_findings 
            ORDER BY timestamp DESC 
            LIMIT 5000
        ''', conn)
        conn.close()
        
        # Clean and validate data
        if not df.empty:
            # Handle mixed timestamp formats
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', errors='coerce')
            # Remove any rows with invalid timestamps
            df = df.dropna(subset=['timestamp'])
            # Ensure numeric columns are properly typed
            df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
            df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

def main():
    st.title("🔍 GhostAI firewall Dashboard")
    st.markdown("Real-time Data Loss Prevention Analytics")
    
    # Add refresh button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    with col2:
        if st.button("📊 Run Quick Test"):
            # Run a quick test to generate new data
            import subprocess
            import sys
            subprocess.run([sys.executable, "-c", """
import sys, os
sys.path.insert(0, 'src')
from ghostai import Pipeline
pipeline = Pipeline()
for i in range(10):
    pipeline.run('Test SSN: 123-45-6789 and API key: sk-test123')
print('Generated 10 test records')
"""])
            st.rerun()
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    if df.empty:
        st.warning("No data available. Run some scans to see data here!")
        st.info("Try running: python -m ghostai 'My SSN is 123-45-6789'")
        return
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_scans = len(df)
        st.metric("Total Scans", total_scans)
    
    with col2:
        flagged_scans = len(df[df['score'] > 0])
        st.metric("Flagged Scans", flagged_scans)
    
    with col3:
        if total_scans > 0:
            detection_rate = (flagged_scans / total_scans) * 100
            st.metric("Detection Rate", f"{detection_rate:.1f}%")
        else:
            st.metric("Detection Rate", "0%")
    
    with col4:
        if not df.empty:
            avg_latency = df['latency_ms'].mean()
            st.metric("Avg Latency", f"{avg_latency:.1f}ms")
        else:
            st.metric("Avg Latency", "0ms")
    
    # Charts
    if not df.empty:
        # Detection rate over time
        st.subheader("📊 Detection Rate Over Time")
        df['hour'] = df['timestamp'].dt.floor('h')
        hourly_stats = df.groupby('hour').agg({
            'score': ['count', lambda x: (x > 0).sum()]
        }).round(2)
        hourly_stats.columns = ['total_scans', 'flagged_scans']
        hourly_stats['detection_rate'] = (hourly_stats['flagged_scans'] / hourly_stats['total_scans'] * 100).round(1)
        
        fig_time = px.line(
            hourly_stats.reset_index(),
            x='hour',
            y='detection_rate',
            title='Detection Rate by Hour'
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Score distribution
        st.subheader("📈 Score Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                df,
                x='score',
                nbins=20,
                title='Score Distribution'
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Flag breakdown
            all_flags = []
            for flags in df['flags']:
                if flags:
                    try:
                        flags_list = json.loads(flags) if isinstance(flags, str) else flags
                        all_flags.extend(flags_list)
                    except:
                        pass
            
            if all_flags:
                flag_counts = pd.Series(all_flags).value_counts()
                fig_flags = px.pie(
                    values=flag_counts.values,
                    names=flag_counts.index,
                    title='Flag Types Distribution'
                )
                st.plotly_chart(fig_flags, use_container_width=True)
            else:
                st.info("No flags detected")
        
        # Recent scans table
        st.subheader("🔍 Recent Scans")
        display_df = df[['timestamp', 'score', 'flags', 'latency_ms', 'session_id']].head(20)
        st.dataframe(display_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**GhostAI firewall Dashboard** - Real-time Data Loss Prevention Analytics")

if __name__ == "__main__":
    main()
