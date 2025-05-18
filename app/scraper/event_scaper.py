from bs4 import BeautifulSoup
from app.splash_client import fetch_html_with_splash

from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EventScraper:
    # def scrape_events(self, url):
    #     html = fetch_html_with_splash(url)
    #     soup = BeautifulSoup(html, 'html.parser')
    #     table = soup.find('table', {'class': 'conf-table'}) or soup.find('table')
    #     if not table:
    #         raise Exception("Conference table not found")
    #     conferences = []
    #     for row in table.find_all('tr'):
    #         cols = row.find_all('td')
    #         if len(cols) >= 3:
    #             conferences.append({
    #                 "date": cols[0].get_text(strip=True),
    #                 "name": cols[1].get_text(strip=True),
    #                 "venue": cols[2].get_text(strip=True)
    #             })
    #     return {
    #             "status": "success",
    #             "url_scraped": url,
    #             "conference_count": len(conferences),
    #             "conferences": conferences
    #     }
    

    def scrape_conferences(self,url):
        chrome_options = Options()
   
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36")

        service = Service('/usr/local/bin/chromedriver')
        # driver = get_driver(headless=True)
        # url = 'https://www.conferencealerts.in/agriculture'
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            print(f"Scraping URL: {url}")
            driver.get(url)

            # Wait for main table or div
            selectors = [
                ("CSS", "table.conf-table"),
                ("XPATH", "/html/body/div[5]/div/div[1]/div[2]/div"),
                ("XPATH", "//table")
            ]

            table = None
            for selector_type, selector in selectors:
                try:
                    if selector_type == "CSS":
                        table = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    else:
                        table = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    break
                except Exception:
                    continue

            if not table:
                raise Exception("Could not locate conference table with any selector")

            conferences = []
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:
                        link_element = row.find_element(By.TAG_NAME, "a")
                        href = link_element.get_attribute("href")

                        # Open link in new tab
                        driver.execute_script("window.open(arguments[0]);", href)
                        driver.switch_to.window(driver.window_handles[-1])

                        # Wait for dynamic elements to load
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "text-xl"))
                        )
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'group/card')]"))
                        )

                        data = {}
                        title = driver.find_element(By.CLASS_NAME, "text-xl")
                        data['name'] = title.text.strip()

                        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'group/card')]")
                        for card in cards:
                            try:
                                key_elem = card.find_element(By.TAG_NAME, "h3")
                                key = key_elem.text.strip()

                                value_container = card.find_element(By.CLASS_NAME, "text-orange-400")
                                links = value_container.find_elements(By.TAG_NAME, "a")
                                value = links[0].get_attribute("href") if links else value_container.text.strip()
                                
                                match key:
                                    case "Event Serial ID":
                                        data["id"] = value
                                    case "Starting Date":
                                        data["start_date"] = value
                                    case "Ending Date":
                                        data["end_date"] = value
                                    case "Abstracts Deadline":
                                        data["abstract_dl"] = value
                                    case "Event Enquiry Email Address":
                                        data["enq_email"] = value.split("mailto:")[1]
                                    case "Website":
                                        data["website"] = value
                                    case "Organized by":
                                        data["organizer"] = value
                                    case "Venue":
                                        value_container = card.find_element(By.CLASS_NAME, "text-orange-400")
                                        data["venue"] = value_container.text.strip()
                                    case "About the Event/Conference":
                                        data["about"] = value
                                    case "Contact Person":
                                        data["contact_person"] = value 
                                    case default:
                                        data[key] = value
                                        
                            except Exception as e:
                                print(f"Skipping card due to error: {e}")
                                continue

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                        conferences.append(data)
                except Exception as e:
                    print(f"Error processing row: {e}")
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
        finally:
            driver.quit()

        
        
