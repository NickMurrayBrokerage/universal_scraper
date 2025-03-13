from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import subprocess

app = Flask(__name__)

# ✅ Home Route to Confirm API is Running
@app.route('/')
def home():
    return "Universal Scraper is running!", 200

# ✅ Existing Playwright Scraper
@app.route('/extract', methods=['POST'])
def extract_data():
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

# ✅ New Endpoint to Run Universal Scraper
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    data = request.json
    property_url = data.get("url")

    if not property_url:
        return jsonify({"error": "No URL provided"}), 400

    # Run the Selenium-based universal scraper
    result = subprocess.run(["python", "universal_scraper.py", property_url], capture_output=True, text=True)

    return jsonify({"status": "Scraper started", "output": result.stdout})

# ✅ Render Deployment Config
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
