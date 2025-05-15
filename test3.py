from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

chrome_options = Options()
chrome_options.add_argument("--headless=new")  # New headless mode in Chrome 109+


try:
    # Initialize WebDriver with error handling
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.conferencealerts.in/ai")
    

    
    # Multiple fallback selectors
    selectors = [
        ("CSS", "table.conf-table"),  # Primary selector
        ("XPATH", "//table[contains(@class,'conf-table')]"),  # Fallback 1
        ("XPATH", "//table")  # Fallback 2
    ]
    
    table = None
    for selector_type, selector in selectors:
        try:
            if selector_type == "CSS":
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            else:
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            break
        except:
            continue
    
    if not table:
        raise Exception("Could not locate conference table with any selector")
    
    print("✅ Successfully located conference table")
    
    # Extract data with error handling
    conferences = []
    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    print(f"Found {len(rows)} conference rows")
    
    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                date = cols[0].text.strip()
                name = cols[1].text.strip()
                venue = cols[2].text.strip()
                conferences.append(f"{date} | {name} | {venue}")
        except Exception as e:
            print(f"⚠️ Error processing row: {str(e)}")
            continue
    
    print("\n Conference Results:")
    print("="*80)
    for conf in conferences[:10]:  # Show first 10 results
        print(conf)
    print(f"\nTotal conferences found: {len(conferences)}")


finally:
    if 'driver' in locals():
        driver.quit()
    print("\n Browser session closed.")