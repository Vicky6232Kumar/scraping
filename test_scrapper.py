from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app.scraper.event_scraper import EventScraper
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = "/usr/bin/google-chrome"
chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = Chrome(service=service, options=chrome_options)

scraper = EventScraper(driver)
events = scraper.scrape_events("https://www.conferencealerts.in/ai", pages=1)
print(f"Scraped {len(events)} events")
driver.quit()
