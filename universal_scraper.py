from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# 🚀 SETUP CHROME DRIVER
try:
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ ChromeDriver successfully loaded.")
except Exception as e:
    print(f"❌ Error initializing ChromeDriver: {e}")
    exit()

# 🌎 PROPERTY URL
property_url = "https://www.livematsonmill.com/"

# **STEP 1: NAVIGATE TO SITE**
driver.get(property_url)
time.sleep(3)
print(f"🔍 Accessing {property_url}...")

# **STEP 2: CLOSE SPECIAL OFFERS POP-UP**
def close_popup():
    try:
        print("🔍 Checking for pop-ups...")
        pop_up = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "specials-box"))
        )
        close_button = pop_up.find_element(By.CLASS_NAME, "specials-close")
        close_button.click()
        print("✅ Closed pop-up window.")
        time.sleep(2)
    except Exception:
        print("❌ No pop-up found.")

close_popup()

# **STEP 3: OPEN HAMBURGER MENU (IF NEEDED)**
def open_hamburger():
    try:
        print("🔍 Checking for hamburger menu...")
        menu_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "hamburger-toggle"))
        )
        menu_button.click()
        print("✅ Hamburger menu opened.")
        time.sleep(2)
    except Exception:
        print("❌ No hamburger menu found.")

open_hamburger()

# **STEP 4: CLICK "FLOOR PLANS" AND OPEN NEW TAB**
def open_floor_plans():
    try:
        print("🔍 Clicking 'Floor Plans'...")
        floor_plans_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Floor Plans')]"))
        )
        floor_plans_button.click()

        # **SWITCH TO NEW TAB**
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[1])
        print("✅ Switched to Floor Plans page.")

        # **WAIT FOR PAGE TO LOAD**
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "span6"))
        )
        time.sleep(5)
        print("✅ Floor Plans page fully loaded.")

    except Exception as e:
        print(f"❌ Error navigating to floor plans: {e}")
        driver.quit()
        exit()

open_floor_plans()

# **STEP 5: FIND FLOOR PLAN TABS**
def get_unit_links():
    try:
        print("🔍 Finding floor plan tabs...")
        unit_links = driver.find_elements(By.XPATH, "//li[contains(@class, 'FPTabLi')]/a")
        if not unit_links:
            print("❌ No floor plan tabs found.")
            driver.quit()
            exit()

        print(f"✅ Found {len(unit_links)} floor plans.")
        return unit_links
    except Exception as e:
        print(f"❌ Error finding floor plan links: {e}")
        return []

unit_links = get_unit_links()

# **STEP 6: CLICK EACH UNIT & SCRAPE DATA**
def scrape_units(unit_links):
    unit_data = []

    for index, link in enumerate(unit_links, 1):
        try:
            unit_name = link.text.strip()
            href = link.get_attribute("href")
            panel_id = href.split("#")[-1]  # Extract the unique panel ID
            print(f"\n🔄 Clicking unit {index}/{len(unit_links)}: {unit_name} (Panel ID: {panel_id})")

            # **Click the unit tab to load data**
            driver.execute_script("arguments[0].click();", link)
            time.sleep(1)  # Small pause

            # **WAIT UNTIL THE NEW FLOOR PLAN IS ACTIVE**
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"div#{panel_id}.tab-pane.row-fluid.active"))
            )

            # **Locate the active floor plan container**
            panel = driver.find_element(By.CSS_SELECTOR, f"div#{panel_id}.tab-pane.row-fluid.active")

            # **Extract the Data with Dynamic Selectors**
            def safe_find(xpath, default="N/A"):
                try:
                    return panel.find_element(By.XPATH, xpath).text.strip()
                except:
                    return default

            floor_plan = safe_find(".//h2[@data-selenium-id='FloorPlanName']")
            # Use relative selectors instead of hardcoded IDs
            bed = safe_find(".//td[preceding-sibling::td[contains(., 'Bed')]]")
            bath = safe_find(".//td[preceding-sibling::td[contains(., 'Bath')]]")
            sqft = safe_find(".//td[preceding-sibling::td[contains(., 'Sq.Ft.')]]")
            rent = safe_find(".//td[preceding-sibling::td[contains(., 'Rent')]]")
            availability = safe_find(".//div[@data-selenium-id='FloorPlanAvailability']")

            print(f"✅ Scraped: {floor_plan}, {bed} Bed, {bath} Bath, {rent}, {sqft} Sq Ft, Availability: {availability}")

            unit_data.append({
                "Floor Plan": floor_plan,
                "Bed": bed,
                "Bath": bath,
                "Rent": rent,
                "Sq Ft": sqft,
                "Availability": availability
            })

        except Exception as e:
            print(f"⚠️ Skipping unit {index} due to error: {e}")
            # Debug: Log panel content if available
            try:
                panel = driver.find_element(By.CSS_SELECTOR, f"div#{panel_id}.tab-pane.row-fluid.active")
                print(f"Debug: Panel content: {panel.get_attribute('outerHTML')[:500]}")
            except:
                print("Debug: Active panel not found")
            continue

    return unit_data

unit_data = scrape_units(unit_links)

# **STEP 7: SAVE RESULTS**
if unit_data:
    print("✅ Scraping complete! Saving data...")
    df = pd.DataFrame(unit_data)
    df.to_csv("rental_data.csv", index=False)
    print("✅ Data saved to rental_data.csv")
    for unit in unit_data:
        print(unit)
else:
    print("❌ No data scraped.")

# **CLOSE DRIVER**
driver.quit()