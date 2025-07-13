from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import os

# Create screenshots folder
os.makedirs("screenshots", exist_ok=True)

# Setup Chrome WebDriver
service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Step 1: Open the satellite map website
driver.get("https://satellitemap.space")
time.sleep(5)

# Step 2: Slightly rotate the globe
canvas = driver.find_element(By.TAG_NAME, "canvas")
action = ActionChains(driver)
action.move_to_element_with_offset(canvas, 100, 100)
action.click_and_hold().move_by_offset(150, 0).release().perform()
time.sleep(1)

# Step 3: Zoom in to reveal satellites
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

time.sleep(2)
driver.save_screenshot("screenshots/zoomed_globe.png")
print("📸 Screenshot saved: zoomed_globe.png")

# Step 4: Switch to 2D view
try:
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in buttons:
        if b.text.strip().upper() == "2D":
            b.click()
            print("✅ Switched to 2D view.")
            break
    else:
        print("⚠ 2D button not found (maybe already active).")
except Exception as e:
    print(f"❌ Error switching to 2D: {e}")

time.sleep(2)
driver.save_screenshot("screenshots/2D_view.png")
print("📸 Screenshot saved: 2D_view.png")

# Step 5: Click a general satellite region (safe bounds)
print("🛰 Scanning for a satellite to click...")

clicked = False
canvas_width = canvas.size['width']
canvas_height = canvas.size['height']
center_x = canvas_width // 2
center_y = canvas_height // 2

# Define small grid around center to try clicking satellites
for x_offset in range(-100, 101, 50):   # -100, -50, 0, 50, 100
    for y_offset in range(-100, 101, 50):
        safe_x = center_x + x_offset
        safe_y = center_y + y_offset

        if 0 < safe_x < canvas_width and 0 < safe_y < canvas_height:
            print(f"🔍 Trying click at offset ({x_offset}, {y_offset})")
            try:
                action.move_to_element_with_offset(canvas, x_offset, y_offset).click().perform()
                time.sleep(3)

                # Check for satellite info
                divs = driver.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    text = div.text.strip()
                    if text and ("NORAD" in text or "launch" in text or "altitude" in text):
                        print("✅ Satellite Found!")
                        print("-" * 40)
                        print(text)
                        print("-" * 40)

                        driver.save_screenshot("screenshots/orbit_path.png")
                        print("📸 Screenshot saved: orbit_path.png")
                        clicked = True
                        break
            except Exception as e:
                print(f"⚠ Failed click at ({x_offset}, {y_offset}): {e}")

        if clicked:
            break
    if clicked:
        break

if not clicked:
    print("⚠ Could not find a satellite — try adjusting zoom or canvas coordinates.")

# Step 6: Detect satellite info panel (if any)
print("📡 Looking for satellite info panel...")
try:
    time.sleep(2)
    divs = driver.find_elements(By.TAG_NAME, "div")
    found_info = False

    for div in divs:
        text = div.text.strip()
        if text and ("NORAD" in text or "launch" in text or "altitude" in text or "Passes" in text):
            print("✅ Satellite Info Panel Detected:")
            print("-" * 40)
            print(text)
            print("-" * 40)
            found_info = True
            break

    driver.save_screenshot("screenshots/final_info_any_satellite.png")
    print("📸 Screenshot saved: final_info_any_satellite.png")

    if not found_info:
        print("⚠ Satellite info panel not found. Try changing the click location.")

except Exception as e:
    print(f"❌ Error while checking satellite info: {e}")

# Step 7: Close browser
driver.quit()
print("✅ Done! Browser closed.")