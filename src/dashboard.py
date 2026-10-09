import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configure the page layout
st.set_page_config(page_title="Tech Job Market Dashboard", layout="wide")

def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    processed_path = os.path.join(current_dir, "..", "data", "processed", "cleaned_jobs.csv")
    try:
        df = pd.read_csv(processed_path)
        return df
    except FileNotFoundError:
        return None

def main():
    st.title("Tech Job Market Tracker")
    st.markdown("A live analysis of current tech job market demands and seniority distributions.")

    df = load_data()

    if df is None or df.empty:
        st.warning("No data found. Please run the scraper and cleaner scripts first.")
        return

    # Sidebar for interactive filtering
    st.sidebar.header("Filter Options")
    
    # Extract unique cities for the dropdown filter
    cities = sorted(df['Location_Clean'].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox("Select Location", options=["All"] + cities)

    # Apply the filter if a specific city is chosen
    if selected_city != "All":
        df = df[df['Location_Clean'] == selected_city]

    # Top-level metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Open Roles", len(df))
    with col2:
        st.metric("Unique Companies", df['Company'].nunique())
    with col3:
        st.metric("Most Common Seniority", df['Seniority'].mode()[0] if not df.empty else "N/A")

    st.markdown("---")

    # Interactive Visualizations
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Top Hiring Companies")
        # Count companies and take the top 10
        top_companies = df['Company'].value_counts().head(10).reset_index()
        top_companies.columns = ['Company', 'Count']
        
        # Create a horizontal bar chart
        fig_companies = px.bar(
            top_companies, 
            x='Count', 
            y='Company', 
            orientation='h',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig_companies.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_companies, use_container_width=True)

    with col_chart2:
        st.subheader("Role Seniority Breakdown")
        seniority_counts = df['Seniority'].value_counts().reset_index()
        seniority_counts.columns = ['Seniority', 'Count']
        
        # Create a donut chart
        fig_seniority = px.pie(
            seniority_counts, 
            names='Seniority', 
            values='Count',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Teal
        )
        st.plotly_chart(fig_seniority, use_container_width=True)

    st.markdown("---")
    st.subheader("Raw Data Preview")
    st.dataframe(df[['Title', 'Company', 'Location_Clean', 'Seniority', 'Link']].head(15))

if __name__ == "__main__":
    main()