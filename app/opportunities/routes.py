# app/opportunities/routes.py
from flask import Blueprint, jsonify, request
from app import cache

from app.scraper.event_scraper import EventScraper
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('/api/opportunities/<opp_type>')
def get_opportunities(opp_type):
    if opp_type in cache["opportunities"]:
        return jsonify({
            "data": cache["opportunities"][opp_type],
            "last_updated": cache["last_updated"]
        })
    return jsonify({"error": "Invalid opportunity type"}), 404

@opportunities_bp.route('/api/opportunity', methods=['GET'])
def get_opportunity():
    # url = request.args.get('url')
    url = request.args.get('url') 
    # purpose = request.get('purpose')  #purpose will contain value -- (opportunity or confrence) 
    iit_name = request.args.get('iit_name') #if purpose is opporunity then for "iit_name"
    
    print("hiii")
    print("URL:", url, type(url))
    print("IIT Name:", iit_name, type(iit_name))
    # i am only inititating the driver for the once 
    # And have move this code in this section fronm the file  ---- 

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
   
    try:
        scraper = EventScraper(driver)

        match iit_name:
            case "iitkgp":
                data = scraper.scrape_opportunity_iitkgp(url,driver)
                return jsonify(data)
            case "iitk":
                data = scraper.scrape_opportunity_iitk(url,driver)
                return jsonify(data)
            case "iitr":
                data = scraper.scrape_opportunity_iitr(url,driver)
                return jsonify(data)
            case "iitd":
                data = scraper.scrape_opportunity_iitd(url,driver)
                return jsonify(data)
            case "iitb":
                data = scraper.scrape_opportunity_iitb(url,driver)
                return jsonify(data)
            case "iitm":
                data = scraper.scrape_opportunity_iitm(url,driver)
                return jsonify(data)
            case "iitg":
                data = scraper.scrape_opportunity_iitg(url,driver)
                return jsonify(data)
            case "iith":
                data = scraper.scrape_opportunity_iith(url,driver)
                return jsonify(data)
            case _:
                return jsonify({
                    "status": "error",
                    "message": f"Unsupported IIT name: {iit_name}"
                }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        driver.quit()