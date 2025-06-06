from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime
import time

class OpportunityScraper:

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
    
    ############## iit Kharagpur ##########

    def scrape_opportunity_iitkgp(self, url, driver):
        try:
            print(f"Scraping URL: {url}")
            driver.get(url)

            selectors = [
                ("CSS", "table.conf-table"),
                ("XPATH", "/html/body/div/div/div/div[2]/div/div/div/div/div/div[1]/div[2]"),
                ("XPATH", "//*[@id='tempJobDiv']")
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
                        if len(cols) >= 1:
                            lines = cols[0].get_attribute('innerHTML').split('<br>')
                            conference = {}
                            last_date = cols[3].text.strip()
                            conference["close_date"] = last_date
                            for line in lines:
                                try:
                                    temp = line.strip()
                                    if "<b>" in temp and "</b>" in temp:
                                            key_start = temp.find("<b>") + 3
                                            key_end = temp.find("</b>")
                                            key = temp[key_start:key_end].strip().rstrip(":")
                                            val = temp[key_end+4:].strip()
                                            if(key == "Position"):
                                                conference["post"] = val
                                            elif(key == "Department"):
                                                conference["department"] = val
                                except Exception as e:
                                    print(f"Error parsing line: {line}, {e}")
                                    continue

                            try:
                                apply_col = cols[4]
                                link_tag = apply_col.find_element(By.TAG_NAME, "a")
                                apply_link = link_tag.get_attribute("href")
                            except:
                                try:
                                    apply_link = apply_col.get_attribute("onclick") or ""
                                    if "location.href=" in apply_link:
                                        start = apply_link.find("'") + 1
                                        end = apply_link.find("'", start)
                                        apply_link = apply_link[start:end]
                                    else:
                                        apply_link = ""
                                except:
                                    apply_link = ""

                            
                            conference["link"] = apply_link
                            conference["location"] = "IIT Kharagpur"

                            if conference:
                                conferences.append(conference)
                    except Exception as e:
                        print(f"Error processing row: {str(e)}")
                        continue

                # pagination code
                try:
                    next_li = driver.find_element(By.CSS_SELECTOR, "li.page-next")
                    if "disabled" in next_li.get_attribute("class"):
                        break

                    next_link = next_li.find_element(By.TAG_NAME, "a")
                    next_link.click()

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
                "opportunities": conferences,
                "logo" : "https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/Profile-63d6e61e-271a-40e1-8823-677921fd2fa4-20240917T174527750Z.webp",
                "institute" : "Indian Institute of Technology Kharagpur"
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }       
        
    ############## iit Roorkee ##########

    def scrape_opportunity_iitr(self, url, driver):
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
            link = table.find_element(By.CLASS_NAME,"publicationListItem").find_element(By.TAG_NAME,"a").get_attribute("href")
            if not items:
                items = table.find_elements(By.XPATH, ".//p")

            opportunities = []
            for item in items:
                try:
                    text = item.text.strip()
                    position_match = re.search(r'position\(s\) of (.*?) in Dept\.', text)
                    position = position_match.group(1).strip() if position_match else "NA"

                    # Extract department
                    department_match = re.search(r'Dept\. of (.*?) \(Last date', text)
                    department = department_match.group(1).strip() if department_match else "NA"

                    # Extract last date
                    last_date_match = re.search(r'Last date to apply: (.*?)\)', text)
                    last_date = last_date_match.group(1).strip() if last_date_match else "NA"

                    opportunity = {
                        "post": position,
                        "department": department,
                        "link": link,
                        "close_date": last_date,
                        "location": "IIT Roorke"
                    }
                    if text:
                        opportunities.append(opportunity)
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue

            return {
                "status": "success",
                "opportunities": opportunities,
                "logo" : "https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/Profile-c40d918a-50d7-4f06-bdcb-97b69b78adff-20240917T175035690Z.webp",
                "institute" : "Indian Institute of Technology Roorkee"
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }

                        ############## iit Guwahati ##########

    def scrape_opportunity_iitg(self, url,driver):

            try:                
                print(f"Scraping URL: {url}")
                driver.get(url)
                
                selectors = [
                    ("CSS", "table.conf-table"),
                    ("XPATH", "/html/body/div/div/section[2]/div/div/div/div/div/div[2]/div"),
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
                            if len(cols) >= 2:
                                total_info = cols[1].find_element(By.TAG_NAME,"a").text.strip()
                                
                        
                                match = re.search(r'project positions? in the (.*?)(?=[,.]\s|\s*\()', total_info, re.IGNORECASE)

                                if match:
                                    dept = match.group(1).strip()
                                    post = f"Project position in the {dept}"
                                else:
                                    post = "NA"
                                    dept = "NA"

                            

                                lnk = cols[1].find_element(By.TAG_NAME,"a").get_attribute('href')
                                close_date = "NA"
                                conference = {
                                
                                    "post": post,
                                    "department": dept,
                                    "link" :lnk,
                                    "close_date":close_date ,
                                    "location" : "IIT Guwahati"
                                    
                                }

                            conferences.append(conference)
                        
                        except Exception as e:
                            print(f"Error processing row: {str(e)}")
                            continue

                    # Handle pagination using class "page-next"
                    try:
                        # next_li = driver.find_element(By.CSS_SELECTOR, "li.DataTables_Table_0_next")
                        next_li = driver.find_element(By.ID, "DataTables_Table_0_next")
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
                    "opportunities": conferences,
                    "logo" : "https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/Profile-5a576b2a-76bf-43a3-bdce-0268c48a95de-20241008T095054381Z.webp",
                    "institute" : "Indian Institute of Technology Guwahati"
                }

            except Exception as e:
                return {
                    "status": "error",
                    "url_scraped": url,
                    "message": str(e)
                }

    ############## iit Kanpur ##########

    def scrape_opportunity_iitk(self, url,driver):

        try:
            
            print(f"Scraping URL: {url}")
            driver.get(url)
            
            selectors = [
                ("CSS", "html body div#all div#back div#contentarea div#wrapper2.shownocolumns div#main div.item-page div.int-cont div.right-box table.vacan"),
                ("XPATH", "//html/body/div[3]/div/div/div[2]/div/div[2]/div/div[2]/table"),
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

         
            print(f"Scraping page {page}")
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 2:
                        conference = {
                            "post":cols[0].text.strip() ,
                            "department": cols[1].text.strip(),
                            "link" :cols[5].find_element(By.TAG_NAME,"a").get_attribute("href"),
                            "close_date":cols[4].text.strip() ,
                            "location" : "IIT Kanpur"
                        }
                        conferences.append(conference)
                    
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    continue

            # Handle pagination using class "page-next"
            

            return {
                "status": "success",
                "opportunities": conferences,
                "logo" : "https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/Profile-03033d59-8689-4257-81c6-adc370eafec7-20240917T174344536Z.webp",
                "institute" : "Indian Institute of Technology Kanpur"
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }

    ############## iit Bombay ##########

    def scrape_opportunity_iitb(self, url, driver):
        try:
            opportunities = []
            seen_links = set()  # Track links to avoid duplicates across all pages
            current_url = url

            while True:
                print(f"Scraping URL: {current_url}")
                driver.get(current_url)
                
                # Wait for opportunities to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "career-wrap"))
                )
                
                # Find all opportunity containers
                wraps = driver.find_elements(By.CLASS_NAME, "career-wrap")
                
                for wrap in wraps:
                    try:
                        # Scroll into view to avoid element interception issues
                        driver.execute_script("arguments[0].scrollIntoView(true);", wrap)
                        
                        # Find title and content elements within the wrap
                        title = wrap.find_element(By.CLASS_NAME, "accordion-section-title")
                        content = wrap.find_element(By.CLASS_NAME, "accordion-section-content")
                        
                        # Click title if content is not visible
                        if not content.is_displayed():
                            driver.execute_script("arguments[0].click();", title)
                            WebDriverWait(driver, 10).until(
                                EC.visibility_of(content)
                            )
                            time.sleep(0.1)  # Brief delay for content stability
                        
                        # Extract the application link
                        try:
                            link_element = content.find_element(By.CLASS_NAME, "load-more-btn").find_element(By.TAG_NAME, "a")
                            link = link_element.get_attribute('href')
                        except Exception as e:
                            print(f"Error extracting link: {e}")
                            link = "NA"
                        
                        # Skip if link is duplicate
                        if link in seen_links:
                            continue
                        seen_links.add(link)
                        
                        # Parse content paragraphs
                        content_dict = {}
                        paragraphs = content.find_elements(By.TAG_NAME, "p")
                        for p in paragraphs:
                            try:
                                strong = p.find_element(By.TAG_NAME, "strong")
                                key = strong.text.strip().rstrip(':')
                                # Extract text after the key, handling colons
                                full_text = p.text.strip()
                                value = full_text.replace(f"{key}:", "", 1).strip()
                                if not value:  # Fallback if replacement didn't work
                                    value = full_text.split(":", 1)[1].strip() if ":" in full_text else full_text
                                content_dict[key] = value
                            except:
                                continue  # Skip paragraphs without strong tags
                        
                        # Build opportunity dictionary
                        opportunity = {
                            "post": content_dict.get("Position Title", "NA"),
                            "department": content_dict.get("Department", "NA"),
                            "link": link,
                            "close_date": content_dict.get("Closing Date", "NA"),
                            "location": content_dict.get("Location", "IIT Bombay")
                        }
                        opportunities.append(opportunity)
                    
                    except Exception as e:
                        print(f"Error processing opportunity: {e}")
                        continue
                
                # Check for next page
                try:
                    next_button = driver.find_element(By.CLASS_NAME, "next")
                    next_link = next_button.get_attribute("href")
                    
                    if not next_link or next_link == current_url:
                        break
                    current_url = next_link
                    time.sleep(2)  # Allow next page to load
                except Exception as e:
                    print(f"Pagination ended: {e}")
                    break
            
            return {
                "status": "success",
                "opportunities": opportunities,
                "logo" :"https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/Profile-6dc44ebc-6776-4884-8a7b-09020144f033-20241007T035730093Z.webp",
                "institute" : "Indian Institute of Technology Bombay"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }

    ############## iisc Banglore ##########

    def scrape_opportunity_iisc(self, url,driver):

            try:
                
                print(f"Scraping URL: {url}")
                driver.get(url)
                
                selectors = [
                    ("CSS", "table.conf-table"),
                    ("XPATH", "/html/body/div/section/div/div/div[2]"),
                    # ("XPATH", "//*[@id=\"tempJobDiv\"]")
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
                
                opportunities = []
                page = 1
                while True:
                    print(f"Scraping page {page}")
                    rows = table.find_elements(By.XPATH, ".//tbody/tr")
                    for row in rows:
                        try:
                            cols = row.find_elements(By.TAG_NAME, "td")
                            if len(cols) >= 2:
                                temp = cols[1].text.strip()
                                dept = temp.split('\n')[0]
                                close_date = cols[3].text.strip()

                                if close_date == "" or close_date == "-":
                                    close_date = "NA"

                                if dept == "":
                                    dept = "NA"

                                conference = {
                                    "post": cols[0].text.strip(),
                                    "department": dept,
                                    "link" : cols[2].find_element(By.TAG_NAME,"a").get_attribute('href'),
                                    "close_date": close_date,
                                    "location" : "IISc Banglore"
                                    
                                }
                            opportunities.append(conference)
                        
                        except Exception as e:
                            print(f"Error processing row: {str(e)}")
                            continue

                    # Handle pagination using class "page-next"
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, "a.paginate_button.next")
                        next_classes = next_button.get_attribute("class")

                        if "disabled" in next_classes:
                            break  # No more pages

                        next_button.click()

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
                    "opportunities": opportunities,
                    "logo" : "https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/iisc.jpg",
                    "institute" : "Indian Institute of Science Banglore",
                }

            except Exception as e:
                return {
                    "status": "error",
                    "url_scraped": url,
                    "message": str(e)
                }

    ############## iit madras ##########

    def scrape_opportunity_iitm(self, url, driver):
        try:
            print(f"Scraping URL: {url}")
            driver.get(url)

            # Wait for all advertisement blocks
            ads = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "post-slide2"))
            )

            print(f"Found {len(ads)} advertisements")

            opportunities = []

            for ad in ads:
                try:
                    title_elem = ad.find_element(By.TAG_NAME, "h4")
                    desc_elem = ad.find_element(By.CLASS_NAME, "post-description")

                    # Extract title
                    title = title_elem.text.strip()

                    # Extract ad number, date, and post
                    desc_text = desc_elem.text.strip()

                    # Extract links (Detailed Advertisement, Departments, Apply/Update)
                    links = ad.find_elements(By.TAG_NAME, "a")
                    detailed_ad_url = ""
                  
                    for link in links:
                        href = link.get_attribute("href")
                        text = link.text.strip().lower()
                        if "detailed advertisement" in text:
                            detailed_ad_url = href
                        elif "departments and areas" in text or "areas" in text:
                            dept_url = href
                        elif "apply" in text or "update" in text:
                            apply_url = href

                    # Check for any alert or status messages
                    try:
                        alert_elem = ad.find_element(By.CLASS_NAME, "alert-warning")
                        status = alert_elem.text.strip()
                    except:
                        status = "NA"

                    opportunity = {
                        "post": title,
                        "link": detailed_ad_url,
                        "location" :"IIT Madras",
                        "close_date": status,
                        "department": "NA" 
                    }
                    opportunities.append(opportunity)

                except Exception as e:
                    print(f"Error processing ad block: {e}")
                    continue

            return {
                "status": "success",
                "opportunities": opportunities,
                "logo" : "https://s3.ap-south-1.amazonaws.com/tayog.in/institute_logo/Profile-143d00e6-3792-4c40-8d4f-52f4ea3c3ed0-20240917T173949705Z.webp",
                "institute" : "Indian Institute of Technology Madras"
            }

        except Exception as e:
            return {
                "status": "error",
                "url_scraped": url,
                "message": str(e)
            }