from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import subprocess
import os
import chromedriver_autoinstaller

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

# ✅ Home Route to Confirm API is Running
@app.route('/')
def home():
    return "Universal Scraper is running!", 200

# ✅ Playwright-based Scraper
@app.route('/extract', methods=['POST'])
def extract_data():
    """Scrapes rental data using Playwright."""
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)

        try:
            property_name = page.inner_text("h1")  # Adjust selector as needed
            address = page.inner_text(".property-address")  # Modify based on website
            rent_elements = page.query_selector_all(".rent-price")
            rents = [rent.inner_text() for rent in rent_elements]
            amenities = [a.inner_text() for a in page.query_selector_all(".amenities-list li")]

            browser.close()

            return jsonify({
                "propertyName": property_name,
                "address": address,
                "rents": rents,
                "amenities": amenities
            })
        
        except Exception as e:
            browser.close()
            return jsonify({"error": str(e)}), 500

# ✅ Run Selenium-based Universal Scraper
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    """Runs the Selenium-based universal scraper."""
    data = request.json
    property_url = data.get("url")

    if not property_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # ✅ Ensure Chrome is installed before running the scraper
        install_chrome()

        # ✅ Run Selenium scraper and capture output
        result = subprocess.run(
            ["python", "universal_scraper.py", "--url", property_url],
            capture_output=True, text=True
        )

        return jsonify({
            "status": "Scraper started",
            "output": result.stdout
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Render Deployment Config
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
