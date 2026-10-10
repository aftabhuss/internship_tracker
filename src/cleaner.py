import pandas as pd
import re
import os
import json
from groq import Groq

def clean_jobs_data(df, groq_api_key=None):
    if df is None or df.empty:
        return pd.DataFrame()

    initial_count = len(df)
    
    # 1. Remove Duplicates
    df = df.drop_duplicates(subset=['Title', 'Company']).copy()
    
    # 2. Clean Location
    df['Location_Clean'] = df['Location'].apply(lambda x: str(x).split(',')[0].strip())

    # 3. Standardize Seniority
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
    df['Title_Clean'] = df['Title'].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s-]', '', str(x)).strip())

    # 4. Bulletproof LLM Integration (JSON Mode)
    df['Inferred_Skill'] = "Unspecified"
    
    if groq_api_key:
        try:
            client = Groq(api_key=groq_api_key)
            unique_titles = df['Title_Clean'].unique().tolist()
            
            prompt = (
                "You are a technical data extraction tool. Extract the single most prominent technical skill "
                "or domain (e.g., Python, SAP, VBA, AI, React, Finance, Cloud) from the following job titles. "
                "Output ONLY a valid JSON object where the keys are the exact job titles provided, "
                "and the values are the extracted skills. If no specific skill is mentioned, output 'General'.\n\n"
                f"Titles: {unique_titles}"
            )
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1,
                # This explicitly forces the LLM to output valid JSON
                response_format={"type": "json_object"} 
            )
            
            # Parse the JSON string safely into a Python dictionary
            skill_mapping = json.loads(chat_completion.choices[0].message.content)
            
            # Map the exact keys directly to the dataframe
            if skill_mapping:
                df['Inferred_Skill'] = df['Title_Clean'].map(skill_mapping).fillna("General")
                
        except Exception as e:
            # If it still fails, the error will print to your terminal so you can debug it
            print(f"LLM Processing Failed: {e}")

    # 5. Save the Processed Data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    processed_path = os.path.join(current_dir, "..", "data", "processed", "cleaned_jobs.csv")
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False, encoding='utf-8')
    
    return df