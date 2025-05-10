import undetected_chromedriver as uc  # type:ignore
from selenium.webdriver.common.by import By  # type:ignore
from selenium.webdriver.support.ui import WebDriverWait  # type:ignore
from selenium.webdriver.support import expected_conditions as EC  #type:ignore
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # type:ignore
import pandas as pd  # type:ignore
import time
import random

def main():
    print("Starting browser with undetected_chromedriver...")
    options = uc.ChromeOptions()
    options.headless = False  # Set to True if you want headless mode
    driver = uc.Chrome(options=options)

    try:
        url = "https://www.olx.in/items/q-car-cover"
        print(f"Navigating to: {url}")
        driver.get(url)

        time.sleep(random.uniform(3, 5))  # let the page load
        driver.save_screenshot("olx_page.png")
        print("Screenshot saved as olx_page.png")

        print("Scrolling page like a human...")
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(random.uniform(1, 2))

        print("Waiting for product listings to load...")
        wait = WebDriverWait(driver, 15)
        try:
            items = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'li[data-aut-id="itemBox"]')
            ))
        except TimeoutException:
            print("Initial selector failed, trying fallback selectors...")
            selectors = [
                '.list-view li', 
                '.product-item', 
                '.item-card',
                'div[class*="item"]',
                'li[class*="list"]'
            ]
            items = []
            for selector in selectors:
                items = driver.find_elements(By.CSS_SELECTOR, selector)
                if items:
                    print(f"Found {len(items)} items with selector: {selector}")
                    break
            if not items:
                print("❌ No items found with any selector. Check screenshot or solve CAPTCHA.")
                input("If a CAPTCHA is visible, solve it and press Enter...")
                items = driver.find_elements(By.CSS_SELECTOR, 'li[data-aut-id="itemBox"]')

        print(f"Found {len(items)} items")

        # Debug: print HTML of first 2 items
        for i, item in enumerate(items[:2]):
            print(f"\nItem {i+1} HTML preview:\n{item.get_attribute('outerHTML')[:500]}...")

        data = []
        for i, item in enumerate(items[:10]):
            try:
                print(f"\nProcessing item {i+1}...")
                title = extract_with_multiple_selectors(item, [
                    'span[data-aut-id="itemTitle"]', 
                    '.title', 'h2', '[class*="title"]'
                ])
                price = extract_with_multiple_selectors(item, [
                    'span[data-aut-id="itemPrice"]', 
                    '.price', '[class*="price"]'
                ])
                location = extract_with_multiple_selectors(item, [
                    'span[data-aut-id="item-location"]', 
                    '.location', '[class*="location"]'
                ])
                try:
                    link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                except:
                    link = "N/A"

                print(f"  Title: {title}")
                print(f"  Price: {price}")
                print(f"  Location: {location}")
                print(f"  Link: {link}")

                data.append({
                    "Title": title,
                    "Price": price,
                    "Location": location,
                    "Link": link
                })

                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                print(f"❌ Error processing item {i+1}: {e}")

        if data:
            df = pd.DataFrame(data)
            df.to_csv("olx_car_covers.csv", index=False)
            print("\n✅ Data saved to olx_car_covers.csv")
            print(df.head())
        else:
            print("❌ No data collected. Check screenshot and HTML debug above.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        input("\nPress Enter to close the browser...")
        driver.quit()
        print("Browser closed")

def extract_with_multiple_selectors(element, selectors):
    """Try multiple selectors to extract text from an element"""
    for selector in selectors:
        try:
            found = element.find_element(By.CSS_SELECTOR, selector)
            return found.text.strip()
        except NoSuchElementException:
            continue
    return "N/A"

if __name__ == "__main__":
    main()
