from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from datetime import datetime
import time
import logging

class EventScraper:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, 20)

    def _parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").isoformat()
        except ValueError:
            return None

    def scrape_events(self, url, pages=15):
        try:
            self.driver.get(url)
            events = []
            for page in range(1, pages + 1):
                try:
                    # Wait for table to load
                    table = self.wait.until(
                        EC.presence_of_element_located((By.ID, "event_table"))
                    )
                    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
                    for row in rows:
                        cols = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                        if len(cols) >= 4:
                            events.append({
                                "title": cols[0],
                                "startDate": self._parse_date(cols[1]),
                                "venue": cols[2],
                                "organizer": cols[3],
                                "isOnline": "virtual" in cols[2].lower()
                            })

                    # Only try to paginate if not on last page
                    if page < pages:
                        self._click_next_page(page + 1)
                        time.sleep(2)
                except Exception as e:
                    self.logger.error(f"Page {page} error: {str(e)}")
                    break
            return events
        except Exception as e:
            self.logger.error(f"Event scraping failed: {str(e)}")
            return []

    def _click_next_page(self, page_num):
        try:
            # Wait until the pagination link is clickable
            next_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"a.pagination-link[data-page='{page_num}']")
                )
            )
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(0.5)  # Let scroll finish

            # Try normal click first
            try:
                next_btn.click()
            except ElementClickInterceptedException:
                # Fallback: force click with JS
                self.driver.execute_script("arguments[0].click();", next_btn)
        except TimeoutException:
            self.logger.error(f"Pagination link for page {page_num} not found or not clickable.")
        except Exception as e:
            self.logger.error(f"Error clicking next page {page_num}: {str(e)}")
