import os
import subprocess
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# ✅ Install Chrome on Render
def install_chrome():
    """Ensures Chrome is installed on Render before running the scraper."""
    try:
        print("🔄 Installing Chrome...")
        os.system("wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        os.system("apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb")
        print("✅ Chrome installed successfully.")
    except Exception as e:
        print(f"❌ Error installing Chrome: {e}")

# ✅ Set Chrome Options
def get_chrome_options():
    """Sets correct Chrome options for headless execution on Render."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/google-chrome"  # ✅ Ensure correct Chrome path
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--no-sandbox")  # Required for Render
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support
    return chrome_options

# ✅ Home Route to Confirm API is Running
@app.route('/')
def home():
    return "Universal Scraper is running!", 200

# ✅ Run Selenium-based Universal Scraper
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    """Runs the Selenium-based universal scraper."""
    data = request.json
    property_url = data.get("url")

    if not property_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # ✅ Ensure Chrome is installed
        install_chrome()

        # ✅ Initialize ChromeDriver with correct binary path
        chrome_options = get_chrome_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ✅ Run Selenium scraper (Replace with your scraping logic)
        driver.get(property_url)
        page_title = driver.title
        driver.quit()

        return jsonify({
            "status": "Scraper started",
            "pageTitle": page_title
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Render Deployment Config
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
