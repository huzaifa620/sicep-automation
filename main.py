from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import re
import subprocess
import xml.etree.ElementTree as ET
import uiautomator2 as u2
from uiautomator2.exceptions import AccessibilityServiceAlreadyRegisteredError

load_dotenv(override=True)

USERNAME = os.getenv("SISEC_USERNAME")
PASSWORD = os.getenv("SISEC_PASSWORD")
BASE_URL = os.getenv("SISEC_BASE_URL")
CURP = os.getenv("SISEC_CURP")
NSS = os.getenv("SISEC_NSS")

# Timeouts and delays
TIMEOUT = int(os.getenv("SISEC_TIMEOUT"))
DELAY = float(os.getenv("SISEC_DELAY"))
APPIUM_SERVER = os.getenv("APPIUM_SERVER")

OUTLOOK_PACKAGE = "com.microsoft.office.outlook"  # Outlook Android package name

# Download settings
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"automation_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Initialize and return Appium WebDriver for Android Chrome."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android"
    options.browser_name = "Chrome"
    options.no_reset = True
    options.new_command_timeout = 300
    return webdriver.Remote(APPIUM_SERVER, options=options)


def safe_click(driver, element):
    """Click element using JavaScript with fallback to regular click."""
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(DELAY)
        driver.execute_script("arguments[0].click();", element)
        return True
    except:
        try:
            element.click()
            return True
        except:
            return False

def login(driver):
    """Authenticate user on SISEC website."""
    wait = WebDriverWait(driver, TIMEOUT)
    
    email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="email"]')))
    email_input.clear()
    email_input.send_keys(USERNAME)
    
    password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="password"]')))
    password_input.clear()
    password_input.send_keys(PASSWORD)
    
    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
    if not safe_click(driver, login_button):
        raise Exception("Failed to click login button")
    
    time.sleep(3)
    
    if driver.current_url == BASE_URL and driver.find_elements(By.CSS_SELECTOR, 'input[name="email"]'):
        raise Exception("Login failed - still on login page")

def fill_query_form(driver, curp, nss):
    """Fill the query form with CURP, NSS, and ensure 'Reporte detallado' is checked."""
    wait = WebDriverWait(driver, TIMEOUT)
    
    curp_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="curp"]')))
    curp_input.clear()
    curp_input.send_keys(curp)
    
    nss_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="nss"]')))
    nss_input.clear()
    nss_input.send_keys(nss)
    
    checkbox_xpath = "//label[contains(text(), 'Reporte detallado')]/ancestor::div[contains(@class, 'flex flex-row')]//button[@role='checkbox']"
    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, checkbox_xpath)))
    
    if checkbox.get_attribute("aria-checked") != "true":
        safe_click(driver, checkbox)

def submit_query(driver):
    """Click the 'consultar' button and wait for process completion."""
    wait = WebDriverWait(driver, TIMEOUT)
    
    # Find and click the consultar button - use type="submit" for efficiency
    consultar_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="dialog"] button[type="submit"]'))
    )
    if not safe_click(driver, consultar_button):
        raise Exception("Failed to click 'Consultar' button")
    
    logger.info("Query submitted, waiting for process completion...")
    
    time.sleep(2)
    
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"][data-state="open"]')))
        logger.info("Query dialog closed, process initiated")
    except:
        logger.warning("Dialog may have already closed or different structure")
    
    logger.info("Query process initiated. Email will be sent shortly...")

def wait_for_email_and_download(driver, curp, download_dir):
    """Use uiautomator2 to interact with Outlook app directly via ADB."""
    logger.info("Connecting to device using uiautomator2...")
    
    # Connect to device via ADB with retry on service already registered error
    max_retries = 2
    for attempt in range(max_retries):
        try:
            d = u2.connect()
            break
        except AccessibilityServiceAlreadyRegisteredError:
            if attempt < max_retries - 1:
                logger.warning("Accessibility service already registered, stopping uiautomator2 service...")
                # Stop uiautomator2 service via ADB
                subprocess.run(["adb", "shell", "am", "force-stop", "com.github.uiautomator"], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                subprocess.run(["adb", "shell", "pkill", "-f", "uiautomator"], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                time.sleep(2)
            else:
                raise
    
    logger.info("Opening Outlook app...")
    
    # Start Outlook app
    d.app_start(OUTLOOK_PACKAGE)
    d.app_wait(OUTLOOK_PACKAGE, timeout=10)
    time.sleep(5)
    
    # Click filter button
    logger.info("Clicking filter button...")
    try:
        # Try multiple ways to find filter button
        filter_btn = None
        
        # Method 1: By description
        filter_btn = d(description="Filter")
        if not filter_btn.exists:
            filter_btn = d(descriptionContains="Filter")
        
        if filter_btn.exists:
            filter_btn.click()
            logger.info("Clicked filter button")
            time.sleep(2)
        else:
            logger.info("Finding filter button coordinates from UI dump...")
            xml_content = d.dump_hierarchy()
            root = ET.fromstring(xml_content)
            
            for elem in root.iter():
                content_desc = elem.get("content-desc", "").strip()
                bounds = elem.get("bounds", "")
                
                if content_desc == "Filter" and bounds:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        # Check if it's around Y=856
                        if 850 <= y1 <= 870:
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            logger.info(f"Found filter button at ({center_x}, {center_y})")
                            d.click(center_x, center_y)
                            time.sleep(2)
                            break
            else:
                # Last resort: Click at right side, Y=856
                width, height = d.window_size()
                logger.info(f"Filter button not found, clicking at ({width - 50}, 856)")
                d.click(width - 50, 856)
                time.sleep(2)
    except Exception as e:
        logger.warning(f"Failed to click filter: {e}")
    
    # Click "Unread" option
    logger.info("Clicking 'Unread' filter option...")
    try:
        # Try multiple ways to find Unread option
        unread_option = None
        
        # Method 1: By text (with or without clickable)
        unread_option = d(text="Unread")
        if not unread_option.exists:
            unread_option = d(textContains="Unread")
        
        if unread_option.exists:
            unread_option.click()
            logger.info("Clicked 'Unread' filter")
            time.sleep(2)
        else:
            # Fallback: Find Unread by parsing UI dump to get exact coordinates at Y=621
            logger.info("Finding 'Unread' option coordinates from UI dump...")
            xml_content = d.dump_hierarchy()
            root = ET.fromstring(xml_content)
            
            for elem in root.iter():
                text = elem.get("text", "").strip()
                bounds = elem.get("bounds", "")
                class_name = elem.get("class", "")
                
                if text == "Unread" and "TextView" in class_name and bounds:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        # Check if it's around Y=621
                        if 610 <= y1 <= 630:
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            logger.info(f"Found 'Unread' option at ({center_x}, {center_y})")
                            d.click(center_x, center_y)
                            time.sleep(2)
                            break
            else:
                # Last resort: Click filter button again to retry
                logger.warning("'Unread' option not found, clicking filter button again to retry...")
                try:
                    filter_btn = d(description="Filter")
                    if not filter_btn.exists:
                        filter_btn = d(descriptionContains="Filter")
                    
                    if filter_btn.exists:
                        filter_btn.click()
                        logger.info("Clicked filter button again")
                        time.sleep(2)
                        # Try to find Unread again after reopening filter
                        unread_option = d(text="Unread")
                        if not unread_option.exists:
                            unread_option = d(textContains="Unread")
                        if unread_option.exists:
                            unread_option.click()
                            logger.info("Clicked 'Unread' filter after retry")
                            time.sleep(2)
                        else:
                            logger.warning("Still could not find 'Unread' option after filter retry")
                    else:
                        # Fallback: try clicking filter by coordinates
                        width, height = d.window_size()
                        logger.info(f"Filter button not found, clicking at ({width - 50}, 856)")
                        d.click(width - 50, 856)
                        time.sleep(2)
                except Exception as retry_error:
                    logger.error(f"Failed to retry filter click: {retry_error}")
    except Exception as e:
        logger.warning(f"Failed to click Unread: {e}")
    
    # Check if there are any emails (wait up to 1 minute for emails to arrive)
    
    def is_inbox_empty():
        """Check if inbox is empty by looking for empty indicators."""
        try:
            xml_content = d.dump_hierarchy()
            root = ET.fromstring(xml_content)
            
            empty_indicator_texts = ["No unread messages", "You're on top of everything here"]
            
            for elem in root.iter():
                text = elem.get("text", "").strip()
                if text:
                    for indicator in empty_indicator_texts:
                        if indicator.lower() in text.lower():
                            logger.info(f"[EMPTY] FOUND EMPTY INBOX INDICATOR: '{text}' - NO EMAILS AVAILABLE!")
                            return True
            logger.info("[OK] No empty inbox indicators found - emails may be available")
            return False
        except Exception as e:
            logger.error(f"Error checking inbox: {e}")
            return False  # Assume not empty if check fails
    
    # Wait up to 60 seconds for emails to arrive, checking every 5 seconds
    wait_timeout = 60  # 1 minute
    check_interval = 5  # Check every 5 seconds
    elapsed_time = 0
    
    # First check immediately
    if is_inbox_empty():
        logger.info("[EMPTY] INBOX IS EMPTY - 'No unread messages' detected. Waiting up to 60 seconds for emails to arrive...")
    else:
        logger.info("[OK] Emails found! Proceeding to click first email...")
        # Emails are available, skip the wait loop
        elapsed_time = wait_timeout  # Skip the loop
    
    while elapsed_time < wait_timeout:
        if not is_inbox_empty():
            logger.info("[OK] Emails found! Proceeding to click first email...")
            break
        
        # Still empty, wait and check again
        logger.info(f"[WAITING] Still waiting for emails... ({elapsed_time}/{wait_timeout} seconds elapsed)")
        time.sleep(check_interval)
        elapsed_time += check_interval
    else:
        # Timeout reached - check one final time
        if is_inbox_empty():
            logger.info("[TIMEOUT] No unread emails available after waiting 60 seconds. The inbox is still empty. Exiting.")
            return None
        else:
            logger.info("[OK] Emails found after timeout! Proceeding...")
    
    # Final safety check before clicking - DO NOT CLICK IF EMPTY
    if is_inbox_empty():
        logger.error("[ERROR] SAFETY CHECK FAILED: Inbox is still empty but code tried to proceed. Aborting.")
        return None
    
    # Find clickable emails in inbox
    width, height = d.window_size()
    
    try:
        xml_content = d.dump_hierarchy()
        root = ET.fromstring(xml_content)
        
        # Find all clickable email elements in the email list area (typically Y between 400-1200)
        clickable_emails = []
        for elem in root.iter():
            bounds = elem.get("bounds", "")
            clickable = elem.get("clickable", "false")
            if bounds and clickable == "true":
                match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    # Check if it's in the email list area (Y between 400-1200, reasonable width)
                    if 400 <= y1 <= 1200 and x1 >= 0 and x2 <= width and (x2 - x1) > 200:
                        clickable_emails.append({
                            'element': elem,
                            'bounds': (x1, y1, x2, y2),
                            'center_y': (y1 + y2) // 2
                        })
        
        # Sort by Y position (top to bottom)
        clickable_emails.sort(key=lambda x: x['center_y'])
        
        logger.info(f"Found {len(clickable_emails)} unread email(s) in inbox")
        
        if len(clickable_emails) == 0:
            logger.warning("No emails found to click")
            return None
        
        # Function to open email
        def open_email(email_info, email_num):
            x1, y1, x2, y2 = email_info['bounds']
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            logger.info(f"Opening email #{email_num}...")
            
            # Click the email
            d.click(center_x, center_y)
            time.sleep(4)  # Wait for email to open
        
        # Function to try finding PDF in current email
        def try_find_pdf():
            time.sleep(3)  # Wait for email to fully load
            
            pdf_button = None
            
            # Try multiple strategies to find PDF button
            try:
                pdf_button = d(text="Constancia de Semanas Cotizadas del Asegurado.pdf", clickable=True)
                if pdf_button.exists:
                    return pdf_button
            except:
                pass
            
            if not pdf_button or not pdf_button.exists:
                try:
                    pdf_button = d(textContains="Constancia de Semanas Cotizadas del Asegurado.pdf", clickable=True)
                    if pdf_button.exists:
                        return pdf_button
                except:
                    pass
            
            if not pdf_button or not pdf_button.exists:
                try:
                    pdf_button = d(descriptionContains="Constancia de Semanas Cotizadas del Asegurado.pdf", clickable=True)
                    if pdf_button.exists:
                        return pdf_button
                except:
                    pass
            
            if not pdf_button or not pdf_button.exists:
                try:
                    pdf_button = d(descriptionContains="File Type PDF", clickable=True)
                    if pdf_button.exists:
                        return pdf_button
                except:
                    pass
            
            if not pdf_button or not pdf_button.exists:
                try:
                    pdf_button = d(descriptionContains=".pdf", clickable=True)
                    if pdf_button.exists:
                        return pdf_button
                except:
                    pass
            
            if not pdf_button or not pdf_button.exists:
                try:
                    pdf_button = d(textContains=".pdf", clickable=True)
                    if pdf_button.exists:
                        return pdf_button
                except:
                    pass
            
            return None
        
        # Try emails - always click first email after going back (since list shifts)
        max_attempts = len(clickable_emails)
        for attempt in range(max_attempts):
            try:
                # Always get the first email from the list (index 0)
                # After going back, the next email becomes the first one
                
                # Get current UI to find first email
                xml_content = d.dump_hierarchy()
                root = ET.fromstring(xml_content)
                
                # Find first clickable email element in the list
                first_email = None
                first_email_bounds = None
                
                clickable_emails_current = []
                for elem in root.iter():
                    bounds = elem.get("bounds", "")
                    clickable = elem.get("clickable", "false")
                    if bounds and clickable == "true":
                        match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                        if match:
                            x1, y1, x2, y2 = map(int, match.groups())
                            # Check if it's in the email list area (Y between 400-1200, reasonable width)
                            if 400 <= y1 <= 1200 and x1 >= 0 and x2 <= width and (x2 - x1) > 200:
                                clickable_emails_current.append({
                                    'element': elem,
                                    'bounds': (x1, y1, x2, y2),
                                    'center_y': (y1 + y2) // 2
                                })
                
                if not clickable_emails_current:
                    logger.warning("No clickable emails found in current view")
                    break
                
                # Sort by Y position and get the first one
                clickable_emails_current.sort(key=lambda x: x['center_y'])
                first_email = clickable_emails_current[0]
                x1, y1, x2, y2 = first_email['bounds']
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Open email and log contents
                open_email(first_email, attempt + 1)
                
                # Try to find PDF
                pdf_button = try_find_pdf()
                
                if pdf_button and pdf_button.exists:
                    logger.info("PDF found! Clicking PDF attachment...")
                    pdf_button.click()
                    time.sleep(2)
                    # Break out of loop and continue with PDF download
                    break
                else:
                    logger.info(f"No PDF in email #{attempt + 1}, trying next...")
                    # Go back to inbox
                    d.press("back")
                    time.sleep(2)
                    # If this was the last attempt, we're done
                    if attempt == max_attempts - 1:
                        logger.error("No PDF found in any email after checking all")
                        return None
            except Exception as e:
                logger.error(f"Error processing email #{attempt + 1}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Try to go back
                try:
                    d.press("back")
                    time.sleep(2)
                except:
                    pass
                # Continue to next attempt
                continue
        else:
            # If we exhausted all attempts without finding PDF
            logger.error("No PDF found in any email after checking all")
            return None
            
    except Exception as e:
        logger.error(f"Error analyzing emails: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    
    # PDF should already be clicked at this point, continue with save/download
    
    # Click "Save to device" in action sheet
    logger.info("Saving PDF to device...")
    save_button = d(textContains="Save to device", clickable=True)
    if not save_button.exists:
        save_button = d(descriptionContains="Save to device", clickable=True)
    if save_button.exists:
        save_button.click()
        time.sleep(3)
    else:
        logger.warning("Could not find 'Save to device' button")
    
    # Find downloaded PDF in Downloads
    logger.info("Searching for downloaded PDF...")
    time.sleep(3)
    
    download_path = "/sdcard/Download"
    
    list_result = subprocess.run(
        ["adb", "shell", "ls", "-la", download_path],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if list_result.returncode != 0:
        raise Exception(f"Could not access {download_path}")
    
    # Parse PDF files from ls -la output
    pdf_files = []
    for line in list_result.stdout.split("\n"):
        if ".pdf" in line and line.strip().startswith("-"):
            parts = line.split()
            if len(parts) >= 8:
                filename = " ".join(parts[7:])
                if filename.endswith(".pdf"):
                    date_str = " ".join(parts[5:7])
                    pdf_files.append((filename, date_str))
    
    if not pdf_files:
        raise Exception("Could not find downloaded PDF")
    
    # Sort by date (most recent first)
    def parse_date(date_str):
        try:
            if "-" in date_str.split()[0]:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            else:
                current_year = datetime.now().year
                return datetime.strptime(f"{current_year} {date_str}", "%Y %b %d %H:%M")
        except:
            return datetime.now()
    
    pdf_files.sort(key=lambda x: parse_date(x[1]), reverse=True)
    pdf_path = f"{download_path}/{pdf_files[0][0]}"
    
    # Rename PDF on device to just CURP.pdf
    filename = f"{curp}.pdf"
    
    # Get the directory of the original file
    device_dir = "/".join(pdf_path.split("/")[:-1])
    new_pdf_path = f"{device_dir}/{filename}"
    
    # Rename file on device using mv command
    # Use shell=True to properly handle paths with spaces
    mv_cmd = f'adb shell "mv \'{pdf_path}\' \'{new_pdf_path}\'"'
    result = subprocess.run(
        mv_cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        raise Exception(f"Failed to rename PDF on device: {result.stderr}")
    
    # Verify the file was renamed and get its size
    verify_result = subprocess.run(
        ["adb", "shell", "ls", "-l", new_pdf_path],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if verify_result.returncode != 0:
        raise Exception("PDF rename failed - file not found at new location")
    
    # Extract file size from ls output
    size = 0
    if verify_result.stdout:
        parts = verify_result.stdout.split()
        if len(parts) >= 5:
            try:
                size = int(parts[4])
            except:
                pass
    
    logger.info(f"PDF renamed on device: {new_pdf_path} ({size} bytes)")
    
    return new_pdf_path


def log_error(error_type, message, curp=None, nss=None):
    """Log errors to a separate error log file."""
    log_file = LOG_DIR / "errors.log"
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"{timestamp}|{error_type}|{message}|CURP:{curp or 'N/A'}|NSS:{nss or 'N/A'}\n")
    logger.error(f"Error logged: {error_type} - {message}")


def main():
    """Main automation workflow."""
    driver = None
    try:
 
        driver = setup_driver()
        wait = WebDriverWait(driver, TIMEOUT)
        
        logger.info("Navigating to SISEC website...")
        driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]')))
        
        logger.info("Logging in...")
        login(driver)
        
        logger.info("Navigating to semanas-cotizadas...")
        driver.get(f"{BASE_URL}semanas-cotizadas")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        logger.info("Opening query form...")
        nueva_consulta_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Nueva consulta')]"))
        )
        if not safe_click(driver, nueva_consulta_button):
            raise Exception("Failed to click 'Nueva consulta' button")
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"][data-state="open"]')))
        
        logger.info("Filling form...")
        fill_query_form(driver, CURP, NSS)
        logger.info(f"[SUCCESS] Form filled - CURP: {CURP}, NSS: {NSS}")
        
        # Submit the query
        # submit_query(driver)
        
        # Wait for email and download PDF
        logger.info("Waiting for email and downloading PDF...")
        pdf_path = wait_for_email_and_download(driver, CURP, DOWNLOAD_DIR)
        
        # Driver is already closed inside wait_for_email_and_download
        driver = None
        
        if pdf_path is None:
            logger.info("No emails found. Automation completed.")
            return
        
        logger.info(f"[SUCCESS] PDF downloaded and renamed: {pdf_path}")
        logger.info("Automation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n[INFO] Interrupted by user")
        if driver:
            driver.quit()
    except Exception as e:
        error_msg = str(e)
        logger.error(f"\n[ERROR] {error_msg}")
        log_error("AUTOMATION_ERROR", error_msg, CURP, NSS)
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
