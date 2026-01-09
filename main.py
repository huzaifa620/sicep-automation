from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def main():
    """Open Chrome and navigate to SISEC website"""
    driver = webdriver.Chrome()
    driver.get("https://sisec-app.vercel.app/")
    
    # Keep browser open for inspection
    input("Press Enter to close browser...")
    driver.quit()

if __name__ == "__main__":
    main()
