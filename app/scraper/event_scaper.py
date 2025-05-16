from bs4 import BeautifulSoup
from app.splash_client import fetch_html_with_splash

class EventScraper:
    def scrape_events(self, url):
        html = fetch_html_with_splash(url)
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'conf-table'}) or soup.find('table')
        if not table:
            raise Exception("Conference table not found")
        conferences = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                conferences.append({
                    "date": cols[0].get_text(strip=True),
                    "name": cols[1].get_text(strip=True),
                    "venue": cols[2].get_text(strip=True)
                })
        return {
                "status": "success",
                "url_scraped": url,
                "conference_count": len(conferences),
                "conferences": conferences
        }
