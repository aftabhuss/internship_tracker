from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_linkedin_jobs(keyword="Data Science Intern", location="Budapest"):
    # Format the URL for LinkedIn's public job search (no login required)
    url = f"https://www.linkedin.com/jobs/search?keywords={keyword}&location={location}"
    print(f"Starting scraper for: {keyword} in {location}")
    
    with sync_playwright() as p:
        # Launch browser (headless=False means you can watch it work)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        
        # Wait for the job list container to appear on the screen
        print("Waiting for page to load...")
        page.wait_for_selector("ul.jobs-search__results-list", timeout=15000)
        
        # Simulate human scrolling to load more jobs dynamically
        print("Scrolling to load more jobs...")
        for _ in range(5):
            page.keyboard.press("End")
            time.sleep(1.5) # Wait for network requests to finish
            
        html = page.content()
        browser.close()
        
    # --- Parsing Layer (BeautifulSoup) ---
    print("Parsing HTML with BeautifulSoup...")
    soup = BeautifulSoup(html, 'html.parser')
    
    # LinkedIn wraps public job postings in a div with the class 'base-card'
    job_cards = soup.find_all("div", class_="base-card") 
    
    jobs_data = []
    for card in job_cards:
        try:
            # Extract text and strip white spaces
            title = card.find("h3", class_="base-search-card__title").text.strip()
            company = card.find("h4", class_="base-search-card__subtitle").text.strip()
            job_location = card.find("span", class_="job-search-card__location").text.strip()
            
            # Extract the URL and clean off tracking parameters
            link = card.find("a", class_="base-card__full-link")["href"].split("?")[0] 
            
            jobs_data.append({
                "Title": title,
                "Company": company,
                "Location": job_location,
                "Link": link
            })
        except AttributeError:
            # If a card is missing a field, skip it rather than crashing
            continue 
            
    # --- Storage Layer (Pandas) ---
    df = pd.DataFrame(jobs_data)
    
    # Dynamically find the absolute path to the data/raw folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(current_dir, "..", "data", "raw")
    filepath = os.path.join(raw_dir, "linkedin_jobs.csv")
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Success! Saved {len(df)} jobs to {filepath}")
    
    return df

if __name__ == "__main__":
    print("\n" + "="*30)
    print(" LinkedIn Job Scraper CLI")
    print("="*30)
    
    user_keyword = input("Enter the job role (e.g., Data Science Intern): ").strip()
    user_location = input("Enter the location (e.g., Budapest): ").strip()
    
    # Provide fallbacks if the user just presses Enter without typing anything
    if not user_keyword:
        user_keyword = "Data Science Intern"
    if not user_location:
        user_location = "Budapest"
        
    scrape_linkedin_jobs(keyword=user_keyword, location=user_location)