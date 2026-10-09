import pandas as pd
import os
import re

def clean_jobs_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(current_dir, "..", "data", "raw", "linkedin_jobs.csv")
    processed_path = os.path.join(current_dir, "..", "data", "processed", "cleaned_jobs.csv")

    print(f"Loading raw data from: {raw_path}")
    try:
        df = pd.read_csv(raw_path)
    except FileNotFoundError:
        print("Error: Raw CSV not found. Run scraper.py first!")
        return

    initial_count = len(df)
    
    # 1. Remove Duplicates
    df = df.drop_duplicates(subset=['Title', 'Company'])
    print(f"Dropped {initial_count - len(df)} duplicate job postings.")

    # 2. Clean Location: Extract just the primary city
    # This splits "Budapest, Budapest, Hungary" and keeps just "Budapest"
    df['Location_Clean'] = df['Location'].apply(lambda x: str(x).split(',')[0].strip())

    # 3. Universal Feature Engineering: Extract Seniority Level
    def extract_seniority(title):
        title = str(title).lower()
        if any(word in title for word in ['intern', 'gyakornok', 'trainee', 'student', 'co-op']):
            return 'Intern / Trainee'
        elif any(word in title for word in ['junior', 'jr', 'entry']):
            return 'Junior'
        elif any(word in title for word in ['senior', 'sr', 'lead', 'head', 'manager', 'director']):
            return 'Senior / Lead'
        else:
            return 'Mid-Level / Unspecified'

    df['Seniority'] = df['Title'].apply(extract_seniority)
    
    # 4. Clean Titles: Remove weird punctuation and symbols
    df['Title_Clean'] = df['Title'].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s-]', '', str(x)).strip())

    # 5. Save the Processed Data
    # Ensure the processed directory exists
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False, encoding='utf-8')
    
    print(f"Successfully saved {len(df)} cleaned records to {processed_path}")

if __name__ == "__main__":
    clean_jobs_data()