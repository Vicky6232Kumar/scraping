import requests
import logging

def fetch_html_with_splash(url, wait=2.0):
    params = {
        'url': url,
        'wait': 2.0,  # Wait for JavaScript to execute
        'timeout': 30,
        'images': 0    # Disable images for faster loading
    }
    splash_url = 'http://localhost:8050/render.html'
    try:
        response = requests.get(splash_url, params=params)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Splash request failed: {str(e)}")
        raise
