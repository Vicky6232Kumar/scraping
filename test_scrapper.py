from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from app.scraper.event_scraper import EventScraper

# Chrome options configuration
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Path to your Chrome binary
chrome_options.add_argument("--headless")  # Run headlessly

# Specify the path to chromedriver directly (no need for WebDriver Manager)
chromedriver_path = "/usr/local/bin/chromedriver"  # Path to your chromedriver binary
service = Service(chromedriver_path)

# Start the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize the scraper
scraper = EventScraper(driver)

# Scrape events
events = scraper.scrape_events("https://www.conferencealerts.in/ai", pages=1)
print(f"Scraped {len(events)} events")

# Quit the driver
driver.quit()
