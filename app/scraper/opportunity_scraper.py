from bs4 import BeautifulSoup
import requests
from datetime import datetime
import logging
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

class OpportunityScraper:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(driver, 20)

    def _parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").isoformat()
        except:
            return None

    def _parse_stipend(self, stipend_str):
        return stipend_str.replace('Rs.', '').strip()

    def _parse_link(self, link_cell):
        link = link_cell.find('a')
        return link['href'] if link else None
    
    def scrape_opportunities(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            opportunities = []
            
            for row in soup.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 6:
                    opportunities.append({
                        "title": cells[0].text.strip(),
                        "organization": cells[1].text.strip(),
                        "deadline": self._parse_date(cells[4].text.strip()),
                        "stipend": self._parse_stipend(cells[3].text.strip()),
                        "link": self._parse_link(cells[-1])
                    })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Opportunity scraping failed: {str(e)}")
            return []
    
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

