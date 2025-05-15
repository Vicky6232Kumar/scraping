from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver


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
   
    def scrape_conferences(self,url,driver):
        # url = 'https://www.conferencealerts.in/india'
        # chrome_options = Options()
        # chrome_options.add_argument("--headless=new")

        try:
            # service = Service('/usr/local/bin/chromedriver')
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"Scraping URL: {url}")  # Debug print
            driver.get(url)
            
            selectors = [
                ("CSS", "table.conf-table"),
                ("XPATH", "//table[contains(@class,'conf-table')]"),
                ("XPATH", "//table")
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
            
            conferences = []
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            
            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:
                        conference = {
                            "date": cols[0].text.strip(),
                            "name": cols[1].text.strip(),
                            "venue": cols[2].text.strip()
                        }
                        conferences.append(conference)
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    continue

            return {
                "status": "success",
                "url_scraped": url,
                "conference_count": len(conferences),
                "conferences": conferences
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }
        # finally:
            # if 'driver' in locals():
            #     driver.quit()


    def scrape_opportunity_iitkgp(self,url,driver):
        # chrome_options = Options()
        # chrome_options.add_argument("--headless=new")

        try:
            # service = Service('/usr/local/bin/chromedriver')
            # driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"Scraping URL: {url}")
            driver.get(url)
            
            selectors = [
                ("CSS", "table.conf-table"),
                ("XPATH", "/html/body/div/div/div/div[2]/div/div/div/div/div/div[1]/div[2]"),
                ("XPATH", "//*[@id=\"tempJobDiv\"]")
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
            
            conferences = []
            page = 1
            while True:
                print(f"Scraping page {page}")
                rows = table.find_elements(By.XPATH, ".//tbody/tr")
                for row in rows:
                    try:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if len(cols) >= 3:
                            conference = {
                                "date": cols[0].text.strip(),
                                "name": cols[1].text.strip(),
                                "venue": cols[2].text.strip()
                            }
                            conferences.append(conference)
                    except Exception as e:
                        print(f"Error processing row: {str(e)}")
                        continue

                # Handle pagination using class "page-next"
                try:
                    next_li = driver.find_element(By.CSS_SELECTOR, "li.page-next")
                    next_classes = next_li.get_attribute("class")
                    if "disabled" in next_classes:
                        break 

                
                    next_link = next_li.find_element(By.TAG_NAME, "a")
                    next_link.click()

                    # Wait for the page to update
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(rows[0])
                    )
                    time.sleep(1)

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

                    page += 1
                except Exception as e:
                    print("Pagination ended or failed:", e)
                    break

            return {
                "status": "success",
                "url_scraped": url,
                "conference_count": len(conferences),
                "conferences": conferences
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }
        finally:
            if 'driver' in locals():
                driver.quit()
                
    def scrape_opportunity_iitr(url, driver):
        try:
            print(f"Scraping URL: {url}")
            driver.get(url)

            selectors = [
                ("CSS", "div.ui.publication-list"),
                ("XPATH", "//div[contains(@class, 'publication-list')]"),
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
                except Exception as e:
                    print(f"Failed selector: {selector_type} -> {selector} | Error: {e}")
                    continue

            if not table:
                raise Exception("Could not locate the content container with any selector")
            else:
                print("Table found")

            items = table.find_elements(By.CLASS_NAME, "intro-text")
            if not items:
                items = table.find_elements(By.XPATH, ".//p")

            opportunities = []
            for item in items:
                try:
                    text = item.text.strip()
                    if text:
                        opportunities.append({"text": text})
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            return {
                "status": "success",
                "url_scraped": url,
                "opportunity_count": len(opportunities),
                "opportunities": opportunities
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }
        finally:
            if 'driver' in locals():
                driver.quit()
