import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Import our custom modules
from scraper import scrape_linkedin_jobs
from cleaner import clean_jobs_data

# Load environment variables from the .env file
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Tech Job Market Tracker", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed" # Automatically hide the sidebar
)

# --- Header ---
st.title("Tech Job Market Tracker 📊")
st.markdown("A live ETL pipeline evaluating current hiring demands and seniority distributions.")
st.markdown("---")

# --- Modern UI Layout: Main Page Search Bar ---
with st.form(key="search_form"):
    # Create a 3-column layout mimicking a modern search engine bar
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # label_visibility="collapsed" hides the ugly text label and uses the placeholder instead
        search_role = st.text_input("Job Role", value="Data Science Intern", placeholder="Job Role (e.g., Data Science Intern)", label_visibility="collapsed")
    with col2:
        search_location = st.text_input("Location", value="Budapest", placeholder="Location (e.g., Budapest)", label_visibility="collapsed")
    with col3:
        submit_button = st.form_submit_button(label="🔍 Search Live Jobs", use_container_width=True)

# --- Modern UI Layout: Hidden Settings ---
with st.expander("⚙️ Advanced Settings (LLM Skill Extraction)"):
    st.markdown("Automatically extract required skills from job titles using the Groq API.")
    default_key = os.environ.get("GROQ_API_KEY", "")
    api_key = st.text_input("Groq API Key", type="password", value=default_key)

# Placeholder for dynamic content
data_container = st.empty()

# --- Application Logic ---
if submit_button:
    with data_container.container():
        with st.status("Executing ETL Pipeline...", expanded=True) as status:
            st.write(f"Launching headless browser for '{search_role}' in {search_location}...")
            raw_df = scrape_linkedin_jobs(keyword=search_role, location=search_location)
            
            if raw_df is not None and not raw_df.empty:
                st.write("Raw data extracted. Initializing transformation layer...")
                if api_key:
                    st.write("Connecting to Groq LLM for skill extraction...")
                clean_df = clean_jobs_data(raw_df, groq_api_key=api_key)
                status.update(label="Pipeline Complete!", state="complete", expanded=False)
            else:
                status.update(label="Extraction Failed. No jobs found.", state="error")
                clean_df = None

        if clean_df is not None and not clean_df.empty:
            
            # Metrics Row (Native Streamlit formatting perfectly adapts to Dark Mode)
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            metric_col1.metric("Total Open Roles", len(clean_df))
            metric_col2.metric("Unique Companies", clean_df['Company'].nunique())
            metric_col3.metric("Primary Target City", clean_df['Location_Clean'].mode()[0])
            metric_col4.metric("Most Common Seniority", clean_df['Seniority'].mode()[0])

            st.markdown("---")

            # Charts Row
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.subheader("Top Hiring Companies")
                top_companies = clean_df['Company'].value_counts().head(10).reset_index()
                top_companies.columns = ['Company', 'Count']
                fig_companies = px.bar(
                    top_companies, x='Count', y='Company', 
                    orientation='h', color='Count', color_continuous_scale='Blues'
                )
                fig_companies.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_companies, use_container_width=True)

            with chart_col2:
                # Check if the LLM successfully categorized the skills
                if 'Inferred_Skill' in clean_df.columns and not (clean_df['Inferred_Skill'] == "Unspecified").all():
                    st.subheader("LLM Inferred Skill Demand")
                    skill_counts = clean_df['Inferred_Skill'].value_counts().head(7).reset_index()
                    skill_counts.columns = ['Skill', 'Count']
                    fig_skills = px.pie(
                        skill_counts, names='Skill', values='Count', hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Teal
                    )
                    st.plotly_chart(fig_skills, use_container_width=True)
                else:
                    st.subheader("Role Seniority Breakdown")
                    seniority_counts = clean_df['Seniority'].value_counts().reset_index()
                    seniority_counts.columns = ['Seniority', 'Count']
                    fig_seniority = px.pie(
                        seniority_counts, names='Seniority', values='Count', hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Teal
                    )
                    st.plotly_chart(fig_seniority, use_container_width=True)

            st.markdown("---")
            st.subheader("Processed Market Data")
            st.dataframe(
                clean_df[['Title', 'Company', 'Location_Clean', 'Seniority', 'Inferred_Skill', 'Link']],
                use_container_width=True,
                hide_index=True
            )
else:
    with data_container.container():
        st.info("Enter a job role and location above, then click 'Search Live Jobs' to begin.")