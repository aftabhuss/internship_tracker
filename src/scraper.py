from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import urllib.parse

def scrape_linkedin_jobs(keyword, location):
    # Properly encode the user's input so spaces and special characters don't break the URL
    safe_keyword = urllib.parse.quote_plus(keyword)
    safe_location = urllib.parse.quote_plus(location)
    
    url = f"https://www.linkedin.com/jobs/search?keywords={safe_keyword}&location={safe_location}"
    print(f"Starting scraper for: {keyword} in {location}")
    
    with sync_playwright() as p:
        # Changed headless to True for a seamless background experience while using the UI
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        print("Waiting for page to load...")
        try:
            page.wait_for_selector("ul.jobs-search__results-list", timeout=15000)
            
            print("Scrolling to load more jobs...")
            for _ in range(5):
                page.keyboard.press("End")
                time.sleep(1.5) 
                
            html = page.content()
        except Exception as e:
            print(f"Error loading page: {e}")
            html = ""
        finally:
            browser.close()
            
    if not html:
        return pd.DataFrame()
        
    print("Parsing HTML with BeautifulSoup...")
    soup = BeautifulSoup(html, 'html.parser')
    job_cards = soup.find_all("div", class_="base-card") 
    
    jobs_data = []
    for card in job_cards:
        try:
            title = card.find("h3", class_="base-search-card__title").text.strip()
            company = card.find("h4", class_="base-search-card__subtitle").text.strip()
            job_location = card.find("span", class_="job-search-card__location").text.strip()
            link = card.find("a", class_="base-card__full-link")["href"].split("?")[0] 
            
            jobs_data.append({
                "Title": title,
                "Company": company,
                "Location": job_location,
                "Link": link
            })
        except AttributeError:
            continue 
            
    df = pd.DataFrame(jobs_data)
    
    # Save the raw data if we found any jobs
    if not df.empty:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(current_dir, "..", "data", "raw")
        os.makedirs(raw_dir, exist_ok=True)
        filepath = os.path.join(raw_dir, "linkedin_jobs.csv")
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Success! Saved {len(df)} jobs to {filepath}")
    else:
        print("No jobs found for this search.")
    
    return df

if __name__ == "__main__":
    # Keeping a simple fallback for CLI testing
    print("LinkedIn Job Scraper CLI")
    test_kw = input("Enter job role: ")
    test_loc = input("Enter location: ")
    scrape_linkedin_jobs(test_kw, test_loc)