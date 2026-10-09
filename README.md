# Tech Job Market Tracker 📊

An automated data pipeline and interactive dashboard designed to track, scrape, and analyze current tech job market demands, focusing on Data Science, AI, and Software Engineering roles.

## The Problem
Standard job search advice relies on outdated assumptions about what skills and seniorities are currently in demand. To optimize my internship applications, I built this tool to scrape live job market data, clean the unstructured text, and visually analyze which companies are hiring and what experience levels they expect.

## Architecture & Tech Stack
This project follows a professional ETL (Extract, Transform, Load) architecture:
*   **Extraction Layer (Playwright & BeautifulSoup):** Bypasses complex background APIs (like LinkedIn's GraphQL/SDUI payloads) by using headless browser automation to render JavaScript and scrape raw HTML directly from the DOM.
*   **Transformation Layer (Pandas):** Cleans messy location data, standardizes job titles, categorizes roles (e.g., Data Analytics, Software Engineering), and extracts seniority levels using Regex and string matching.
*   **Presentation Layer (Streamlit & Plotly):** A responsive web dashboard that visualizes hiring trends and seniority distributions dynamically.
*   **Development Workflow:** Built leveraging AI-assisted development tools (Cursor/Emergent) to rapidly prototype the extraction pipeline and UI components.

## Project Structure
```text
internship_tracker/
│
├── data/
│   ├── raw/                 # Unprocessed HTML/CSV data
│   └── processed/           # Cleaned Pandas DataFrames
│
├── src/
│   ├── scraper.py           # Playwright automation & CLI interface
│   ├── cleaner.py           # Pandas text cleaning & feature engineering
│   └── dashboard.py         # Streamlit UI & Plotly visualizations
│
├── .gitignore
├── requirements.txt
└── README.md