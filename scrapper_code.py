from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

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



@app.route('/opportunity', methods=['GET'])
def get_conferences():

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    url = request.args.get('url', 'https://iitr.ac.in/Careers/Project%20Jobs.html')  # Default URL if none provided
    
    data = scrape_opportunity_iitr(url,driver)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)