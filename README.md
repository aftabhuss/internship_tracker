# Tech Job Market Tracker & AI Analyzer 📊🤖

A fully integrated ETL web application that scrapes live job market data, cleans unstructured text, and leverages Large Language Models (LLMs) to dynamically extract in-demand skills for tech roles (Data Science, AI, and Software Engineering).

## The Business Problem
Standard job search advice relies on outdated assumptions. To optimize applications and understand real-time market demands, I engineered this tool to scrape live job boards, structure the messy data, and visually analyze which companies are actively hiring, the required seniority levels, and the specific tech stacks being requested.

## Architecture & Tech Stack
This project follows a professional ETL (Extract, Transform, Load) architecture, wrapped in a modern web UI:
*   **Extraction Layer (Playwright):** Bypasses complex background APIs (like LinkedIn's GraphQL/SDUI payloads) using headless browser automation to render JavaScript and scrape raw DOM elements dynamically.
*   **Transformation Layer (Pandas + Groq LLM):** 
    *   *Structural Cleaning:* Uses Pandas and Regex to deduplicate records, standardize locations, and categorize seniority.
    *   *Semantic Enrichment:* Integrates the Groq API (`llama3-8b-8192`) via strict JSON-mode prompting to dynamically read job titles and extract core technical skills (e.g., Python, React, Cloud).
*   **Presentation Layer (Streamlit & Plotly):** A responsive, dark-mode compatible web dashboard featuring interactive metric cards and charts.

## Project Structure
```text
internship_tracker/
│
├── data/
│   ├── raw/                 # Unprocessed Playwright CSV outputs
│   └── processed/           # Cleaned & AI-enriched Pandas DataFrames
│
├── src/
│   ├── scraper.py           # Headless browser automation module
│   ├── cleaner.py           # Pandas cleaning & Groq JSON-mode skill extraction
│   └── dashboard.py         # Main Streamlit web application
│
├── .env                     # Local secrets (API keys)
├── .gitignore
├── requirements.txt
└── README.md