from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

USERNAME = "imss2612025@outlook.com"
PASSWORD = "sisec2026"
BASE_URL = "https://sisec-app.vercel.app/"
CURP = "LAAL760213MZSZLZ08"
NSS = "75927607616"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def login(driver):
    wait = WebDriverWait(driver, 10)
    
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "email")))
    email_input.clear()
    email_input.click()
    email_input.send_keys(USERNAME)
    
    password_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    password_input.clear()
    password_input.click()
    password_input.send_keys(PASSWORD)
    
    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
    driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
    time.sleep(0.5)
    
    try:
        login_button.click()
    except:
        driver.execute_script("arguments[0].click();", login_button)
    
    time.sleep(2)
    
    try:
        error_elements = driver.find_elements(By.CSS_SELECTOR, "[data-error='true'], .error, .text-destructive, [role='alert']")
        if error_elements:
            error_text = error_elements[0].text.strip()
            if error_text:
                raise Exception(f"Login failed: {error_text}")
    except Exception as e:
        if "Login failed" in str(e):
            raise
        pass
    
    try:
        wait.until(EC.staleness_of(email_input))
    except:
        try:
            wait.until(lambda d: len(d.find_elements(By.NAME, "email")) == 0)
        except:
            current_url = driver.current_url
            if current_url == BASE_URL or "login" in current_url.lower():
                raise Exception("Login failed - still on login page")

def main():
    driver = None
    try:
        driver = setup_driver()
        
        print("Navigating to SISEC website...")
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        
        print("Logging in...")
        login(driver)
        print("[OK] Login successful")
        
        print("Navigating to semanas-cotizadas...")
        driver.get(f"{BASE_URL}semanas-cotizadas")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print("Clicking 'Nueva consulta' button...")
        wait = WebDriverWait(driver, 10)
        nueva_consulta_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nueva consulta')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", nueva_consulta_button)
        time.sleep(0.5)
        
        try:
            nueva_consulta_button.click()
        except:
            driver.execute_script("arguments[0].click();", nueva_consulta_button)
        
        print("Waiting for popup...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"][data-state="open"]')))
        
        print("Filling CURP...")
        curp_input = wait.until(EC.element_to_be_clickable((By.NAME, "curp")))
        curp_input.clear()
        curp_input.click()
        curp_input.send_keys(CURP)
        print(f"[OK] Filled CURP: {CURP}")
        
        print("Filling NSS...")
        nss_input = wait.until(EC.element_to_be_clickable((By.NAME, "nss")))
        nss_input.clear()
        nss_input.click()
        nss_input.send_keys(NSS)
        print(f"[OK] Filled NSS: {NSS}")
        
        print("Checking 'Reporte detallado' checkbox...")
        reporte_detallado_checkbox = wait.until(
            EC.presence_of_element_located((
                By.XPATH, 
                "//label[contains(text(), 'Reporte detallado')]/ancestor::div[contains(@class, 'flex flex-row')]//button[@role='checkbox']"
            ))
        )
        
        checkbox_state = reporte_detallado_checkbox.get_attribute("data-state")
        aria_checked = reporte_detallado_checkbox.get_attribute("aria-checked")
        
        if checkbox_state != "checked" or aria_checked != "true":
            driver.execute_script("arguments[0].scrollIntoView(true);", reporte_detallado_checkbox)
            time.sleep(0.3)
            try:
                reporte_detallado_checkbox.click()
            except:
                driver.execute_script("arguments[0].click();", reporte_detallado_checkbox)
            time.sleep(0.5)
        
        print("[OK] 'Reporte detallado' checkbox verified/checked")
        
        print("\n" + "="*50)
        print("[OK] Form filled successfully!")
        print("="*50)
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        input("\nPress Enter to close browser...")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
