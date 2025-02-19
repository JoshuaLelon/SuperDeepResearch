#!/usr/bin/env python3
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    try:
        print("Starting browser...")
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options)
        print("Browser started successfully")
        
        print("Navigating to Google...")
        driver.get('https://google.com')
        time.sleep(2)
        
        print("Looking for search input...")
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        if search_input:
            print("Found search input, entering query...")
            search_input.send_keys("undetected-chromedriver test")
            search_input.submit()
            time.sleep(3)
            print("Search completed")
        else:
            print("Could not find search input")
            
        print("Stopping browser...")
        driver.quit()
        print("Browser stopped successfully")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    print("Starting test...")
    main()
    print("Test completed") 