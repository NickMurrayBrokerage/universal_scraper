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
    """Ensures Chrome and ChromeDriver are installed correctly on Render."""
    chrome_dir = "/tmp/chrome"
    chrome_binary_path = f"{chrome_dir}/chrome"
    chromedriver_path = "/tmp/chromedriver"

    try:
        if not os.path.exists(chrome_binary_path):
            logger.info("❌ Chrome not found. Installing now...")
            os.makedirs(chrome_dir, exist_ok=True)
            os.system(f"wget -q -O {chrome_dir}/chrome.zip https://storage.googleapis.com/chrome-for-render/chrome-linux.zip")
            os.system(f"unzip -q {chrome_dir}/chrome.zip -d {chrome_dir}")
            os.system(f"chmod +x {chrome_binary_path}")
            logger.info(f"✅ Chrome installed at {chrome_binary_path}")

        if not os.path.exists(chromedriver_path):
            logger.info("❌ ChromeDriver not found. Installing now...")
            chromedriver_autoinstaller.install()
            os.system(f"mv $(which chromedriver) {chromedriver_path}")
            os.system(f"chmod +x {chromedriver_path}")
            logger.info("✅ ChromeDriver installed successfully.")

        os.environ["GOOGLE_CHROME_BIN"] = chrome_binary_path
        os.environ["PATH"] += os.pathsep + chrome_dir
        return chromedriver_path

    except Exception as e:
        logger.error(f"❌ Error installing Chrome: {e}")
        raise

def get_chrome_options():
    """Sets correct Chrome options for headless execution on Render."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/tmp/chrome/chrome"
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