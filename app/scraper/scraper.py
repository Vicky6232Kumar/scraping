from selenium import webdriver
from selenium.webdriver.common.by import By

class WebScraper:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def scrape_events(self, url):
        self.driver.get(url)
        # Dummy example: replace with real selectors
        events = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".event-row")
        for row in rows:
            events.append({
                "title": row.find_element(By.CSS_SELECTOR, ".event-title").text,
                "date": row.find_element(By.CSS_SELECTOR, ".event-date").text,
                # Add more fields as needed
            })
        return events

    def scrape_opportunities(self, url):
        self.driver.get(url)
        opportunities = []
        rows = self.driver.find_elements(By.CSS_SELECTOR, ".opportunity-row")
        for row in rows:
            opportunities.append({
                "title": row.find_element(By.CSS_SELECTOR, ".opp-title").text,
                "organization": row.find_element(By.CSS_SELECTOR, ".opp-org").text,
                # Add more fields as needed
            })
        return opportunities

    def quit(self):
        self.driver.quit()
