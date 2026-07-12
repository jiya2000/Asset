from playwright.sync_api import sync_playwright
import time
import os

def run():
    # Ensure docs/assets dir exists
    os.makedirs('c:/Users/HP/Downloads/AssetFlow/docs/assets', exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        
        # Login
        page.goto('http://localhost:5173/login')
        page.fill('input[type="email"]', 'arjun.sharma@assetflow.com')
        page.fill('input[type="password"]', 'password123')
        page.click('button[type="submit"]')
        time.sleep(3) # wait for login and dashboard to load
        
        # Open notification dropdown to show it off
        try:
            # The bell is inside a button. We can click the Bell icon's parent button.
            page.locator('button:has(svg.lucide-bell)').click()
            time.sleep(0.5)
        except Exception as e:
            print("Could not open notifications", e)

        # Dashboard screenshot
        page.screenshot(path='c:/Users/HP/Downloads/AssetFlow/docs/assets/dashboard_real.png')
        
        # Assets page screenshot
        page.goto('http://localhost:5173/assets')
        time.sleep(2)
        page.screenshot(path='c:/Users/HP/Downloads/AssetFlow/docs/assets/assets_real.png')
        
        # Maintenance page screenshot
        page.goto('http://localhost:5173/maintenance')
        time.sleep(2)
        page.screenshot(path='c:/Users/HP/Downloads/AssetFlow/docs/assets/maintenance_real.png')
        
        browser.close()

if __name__ == '__main__':
    run()
