import os
import subprocess
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["TERM"] = "dumb"

def setup_chrome():
    """Sets up Chrome and ChromeDriver for Render."""
    chrome_binary_path = os.environ.get("GOOGLE_CHROME_BIN", "/usr/local/bin/chrome")
    chromedriver_path = "/tmp/chromedriver"

    try:
        if not os.path.exists(chromedriver_path):
            logger.info("❌ ChromeDriver not found. Installing now...")
            chromedriver_path = chromedriver_autoinstaller.install()  # Returns path
            if not chromedriver_path:
                raise Exception("Failed to install ChromeDriver")
            os.system(f"chmod +x {chromedriver_path}")
            logger.info(f"✅ ChromeDriver installed at {chromedriver_path}")

        os.environ["GOOGLE_CHROME_BIN"] = chrome_binary_path
        os.environ["PATH"] += os.pathsep + os.path.dirname(chromedriver_path)
        logger.info(f"✅ Chrome setup complete: {chrome_binary_path}")
        return chromedriver_path

    except Exception as e:
        logger.error(f"❌ Error setting up Chrome: {e}")
        raise

def get_chrome_options():
    chrome_binary_path = os.environ.get("GOOGLE_CHROME_BIN", "/usr/local/bin/chrome")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_binary_path
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    return chrome_options
  
@app.route('/')
def home():
    return "✅ Universal Scraper is running!", 200

@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    """Runs the Selenium-based universal scraper."""
    data = request.json
    property_url = data.get("url")

    if not property_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        chromedriver_path = setup_chrome()
        chrome_options = get_chrome_options()
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(property_url)
        page_title = driver.title
        driver.quit()

        return jsonify({
            "status": "✅ Scraper started",
            "pageTitle": page_title
        })

    except Exception as e:
        logger.error(f"❌ Scraper error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)