from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import os

# Setup
os.makedirs("screenshots", exist_ok=True)
service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()

driver.get("https://satellitemap.space")
time.sleep(5)

# STEP 1: Open Settings via gear icon
print("⚙️ Clicking the Settings icon...")
try:
    gear_icon = driver.find_element(By.CSS_SELECTOR, "img[src*='gear']")
    gear_icon.click()
    time.sleep(1)
except:
    try:
        gear_icon = driver.find_element(By.XPATH, "//button[contains(@class,'settings') or @aria-label='Settings']")
        gear_icon.click()
        time.sleep(1)
    except Exception as e:
        print("❌ Couldn't find settings gear icon:", e)

# STEP 2: Click on HOME menu inside settings
try:
    home_button = driver.find_element(By.XPATH, "//div[contains(text(),'HOME')]")
    home_button.click()
    time.sleep(1)
    print("🏠 Clicked 'HOME' in settings.")
except Exception as e:
    print("❌ Failed to click 'HOME':", e)

# STEP 3: Enter Lat/Lon
try:
    lat_input = driver.find_element(By.XPATH, "//label[contains(text(),'Latitude')]/following-sibling::input")
    lon_input = driver.find_element(By.XPATH, "//label[contains(text(),'Longitude')]/following-sibling::input")
    
    lat_input.clear()
    lat_input.send_keys("13.0093")
    
    lon_input.clear()
    lon_input.send_keys("77.6479")

    time.sleep(1)

    save_button = driver.find_element(By.XPATH, "//button[normalize-space()='Save']")
    save_button.click()
    print("📍 Entered geolocation and saved.")

    time.sleep(2)
except Exception as e:
    print("❌ Failed entering geolocation:", e)

# STEP 4: Rotate the globe
canvas = driver.find_element(By.TAG_NAME, "canvas")
action = ActionChains(driver)
action.move_to_element_with_offset(canvas, 100, 100)
action.click_and_hold().move_by_offset(150, 0).release().perform()
time.sleep(1)

# STEP 5: Zoom in
for _ in range(14):
    driver.execute_script("""
        const canvas = document.querySelector('canvas');
        const evt = new WheelEvent('wheel', {
            deltaY: -100,
            bubbles: true
        });
        canvas.dispatchEvent(evt);
    """)
    time.sleep(0.4)

driver.save_screenshot("screenshots/zoomed_globe.png")
print("📸 Screenshot saved: zoomed_globe.png")

# STEP 6: Switch to 2D view
try:
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        if b.text.strip().upper() == "2D":
            b.click()
            print("✅ Switched to 2D view.")
            break
    else:
        print("⚠️ 2D button not found (maybe already active).")
except Exception as e:
    print(f"❌ Error switching to 2D: {e}")

time.sleep(2)
driver.save_screenshot("screenshots/2D_view.png")

# STEP 7: Click satellite
print("🚁 Scanning for a satellite to click...")
clicked = False
canvas_width = canvas.size['width']
canvas_height = canvas.size['height']
center_x = canvas_width // 2
center_y = canvas_height // 2

for x_offset in range(-100, 101, 50):
    for y_offset in range(-100, 101, 50):
        safe_x = center_x + x_offset
        safe_y = center_y + y_offset

        if 0 < safe_x < canvas_width and 0 < safe_y < canvas_height:
            print(f"🔍 Trying click at offset ({x_offset}, {y_offset})")
            try:
                action.move_to_element_with_offset(canvas, x_offset, y_offset).click().perform()
                time.sleep(3)

                divs = driver.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    text = div.text.strip()
                    if text and ("NORAD" in text or "launch" in text or "altitude" in text):
                        print("✅ Satellite Found!")
                        print("-" * 40)
                        print(text)
                        print("-" * 40)
                        driver.save_screenshot("screenshots/orbit_path.png")
                        clicked = True
                        break
            except Exception as e:
                print(f"⚠️ Failed click at ({x_offset}, {y_offset}): {e}")

        if clicked:
            break
    if clicked:
        break

if not clicked:
    print("⚠️ Could not find a satellite.")

# STEP 8: Click "calculate" for projected passes
print("🧮 Trying to click the 'calculate' button for projected passes...")
try:
    time.sleep(2)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.is_displayed() and "calculate" in button.text.lower():
            button.click()
            print("✅ Clicked the 'calculate' button.")
            break
    time.sleep(3)
    driver.save_screenshot("screenshots/projected_passes.png")
    print("📸 Screenshot saved: projected_passes.png")
except Exception as e:
    print("❌ Error clicking 'calculate':", e)

# STEP 9: Done
driver.quit()
print("✅ Done! Browser closed.")
