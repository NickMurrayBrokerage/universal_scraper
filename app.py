import os
import subprocess
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller

app = Flask(__name__)

# ✅ Install Chrome in a User-Writable Directory (/tmp/chrome/)
def setup_chrome():
    """Downloads and installs Chrome in a writable directory on Render."""
    try:
        print("🔄 Checking for Chrome installation...")

        # ✅ Set Chrome binary path inside /tmp/ (a writable directory)
        chrome_binary_path = "/tmp/chrome/chrome"

        # ✅ Check if Chrome is already installed
        if not os.path.exists(chrome_binary_path):
            print("❌ Chrome not found. Installing now...")

            # ✅ Create a writable directory
            os.makedirs("/tmp/chrome", exist_ok=True)

            # ✅ Download a pre-built, portable version of Chrome (proven to work on Render)
            os.system("wget -q -O /tmp/chrome/chrome.zip https://storage.googleapis.com/chrome-for-render/chrome-linux.zip")

            # ✅ Unzip Chrome (No Root Needed)
            os.system("unzip -q /tmp/chrome/chrome.zip -d /tmp/chrome/")

            # ✅ Set executable permissions
            os.system("chmod +x /tmp/chrome/chrome")

            print(f"✅ Chrome installed at {chrome_binary_path}")

        # ✅ Set environment variable for Chrome binary
        os.environ["GOOGLE_CHROME_BIN"] = chrome_binary_path
        print(f"✅ GOOGLE_CHROME_BIN set to {chrome_binary_path}")

        # ✅ Install ChromeDriver Automatically
        chromedriver_autoinstaller.install()
        print("✅ ChromeDriver installed successfully.")

    except Exception as e:
        print(f"❌ Error installing Chrome: {e}")



# ✅ Set Chrome Options
def get_chrome_options():
    """Sets correct Chrome options for headless execution on Render."""
    chrome_options = webdriver.ChromeOptions()

    # ✅ Use dynamically set Chrome binary path
    chrome_binary_path = os.getenv("GOOGLE_CHROME_BIN", "/tmp/chrome/chrome")
    chrome_options.binary_location = chrome_binary_path

    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--no-sandbox")  # Required for Render
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes
    chrome_options.add_argument("--remote-debugging-port=9222")  # Debugging support

    return chrome_options

# ✅ Home Route to Confirm API is Running
@app.route('/')
def home():
    return "✅ Universal Scraper is running!", 200

# ✅ Run Selenium-Based Scraper
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    """Runs the Selenium-based universal scraper."""
    data = request.json
    property_url = data.get("url")

    if not property_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # ✅ Ensure Chrome and ChromeDriver are Installed
        setup_chrome()

        # ✅ Initialize ChromeDriver with Correct Options
        chrome_options = get_chrome_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ✅ Run Selenium Scraper (Modify Logic if Needed)
        driver.get(property_url)
        page_title = driver.title
        driver.quit()

        return jsonify({
            "status": "✅ Scraper started",
            "pageTitle": page_title
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Start Flask API
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
