import streamlit as st
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
from fetcher_email import authenticate_gmail, fetch_latest_unread_emails
from classify_gemini import classify_emails_with_gemini

st.set_page_config(page_title="Job Email Classifier", layout="wide")
st.title("📬 Job Search Email Classifier Dashboard")

# Auto-refresh settings
auto_refresh = st.sidebar.checkbox("Auto-refresh (30 seconds)", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 300, 30)

if auto_refresh:
    # This will auto-refresh the page at the specified interval
    st.markdown(f"""
    <script>
        setTimeout(function(){{
            window.location.reload();
        }}, {refresh_interval * 1000});
    </script>
    """, unsafe_allow_html=True)

def load_results():
    """Load results from the background service"""
    try:
        with open("email_results.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def display_results(emails_data):
    """Display the classification results"""
    if not emails_data:
        st.info("No classified emails found. Make sure the background service is running.")
        return
    
    df = pd.DataFrame(emails_data)
    
    # Show stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Classified", len(df))
    with col2:
        latest_time = max([email.get('processed_at', '') for email in emails_data])
        st.metric("Last Updated", latest_time[:19] if latest_time else "N/A")
    with col3:
        job_related = len(df[df['label'] != 'Not Job related'])
        st.metric("Job Related", job_related)
    
    # Pie chart
    fig = px.pie(df, names='label', title='📊 Email Classification Distribution')
    st.plotly_chart(fig, use_container_width=True)
    
    # Filter options
    st.subheader("📋 Email Details")
    
    # Filter by label
    selected_labels = st.multiselect(
        "Filter by category:",
        options=df['label'].unique(),
        default=df['label'].unique()
    )
    
    filtered_df = df[df['label'].isin(selected_labels)]
    
    # Display filtered results
    st.dataframe(
        filtered_df[['subject', 'from', 'date', 'label', 'processed_at']],
        use_container_width=True
    )

# Main content
tab1, tab2 = st.tabs(["📊 Dashboard", "🔧 Manual Control"])

with tab1:
    st.subheader("Automated Classification Results")
    emails_data = load_results()
    display_results(emails_data)

with tab2:
    st.subheader("Manual Email Processing")
    service = authenticate_gmail()
    
    if st.button("🔄 Fetch & Classify Latest 10 Unread Emails"):
        with st.spinner("Fetching emails..."):
            emails = fetch_latest_unread_emails(service)
        
        if not emails:
            st.warning("No unread emails found.")
        else:
            with st.spinner("Classifying emails with Gemini..."):
                labels = classify_emails_with_gemini(emails)
            
            for email, label in zip(emails, labels):
                email["label"] = label

            df = pd.DataFrame(emails)
            st.success(f"🎉 Classified {len(df)} emails.")

            fig = px.pie(df, names='label', title='📊 Email Classification Distribution')
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("📋 Email Details")
            st.dataframe(df[['subject', 'from', 'date', 'label']])

# Sidebar info
st.sidebar.markdown("### 🤖 Background Service Status")
try:
    with open("email_results.json", 'r') as f:
        data = json.load(f)
        if data:
            last_update = max([email.get('processed_at', '') for email in data])
            st.sidebar.success(f"✅ Active\nLast update: {last_update[:19]}")
        else:
            st.sidebar.warning("⚠️ No data found")
except FileNotFoundError:
    st.sidebar.error("❌ Background service not running")

st.sidebar.markdown("### 📝 Instructions")
st.sidebar.markdown("""
1. Run `python background_classifier.py` in terminal
2. Keep it running in background
3. Dashboard updates automatically every 30 minutes
""")