from bs4 import BeautifulSoup
import requests
from datetime import datetime
import logging

class OpportunityScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
