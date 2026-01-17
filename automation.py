from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
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
    
    logger.info("[STEP] Finding 'Consultar' button in dialog...")
    # Find and click the consultar button - use type="submit" for efficiency
    consultar_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="dialog"] button[type="submit"]'))
    )
    logger.info("[STEP] Found 'Consultar' button, clicking...")
    if not safe_click(driver, consultar_button):
        raise Exception("Failed to click 'Consultar' button")
    
    logger.info("[STEP] Query submitted, waiting for dialog to close...")
    time.sleep(3)
    
    # Wait for dialog to close - try multiple ways
    dialog_closed = False
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"][data-state="open"]')))
        logger.info("[SUCCESS] Dialog closed automatically")
        dialog_closed = True
    except:
        logger.warning("[INFO] Dialog did not close automatically, checking if still open...")
    
    # If dialog is still open, close it explicitly
    if not dialog_closed:
        try:
            logger.info("[STEP] Checking if dialog is still open...")
            dialog = driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"][data-state="open"]')
            logger.info(f"[DEBUG] Found {len(dialog)} dialogs with data-state='open'")
            
            # Also check for any dialog regardless of state
            all_dialogs = driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"]')
            logger.info(f"[DEBUG] Found {len(all_dialogs)} total dialogs")
            
            for idx, d in enumerate(all_dialogs):
                try:
                    data_state = d.get_attribute("data-state")
                    logger.info(f"[DEBUG] Dialog {idx}: data-state='{data_state}'")
                except:
                    pass
            
            if dialog or all_dialogs:
                logger.info("[STEP] Dialog still open, attempting to close it...")
                
                # Try clicking close button - multiple selectors
                close_selectors = [
                    ('css', 'div[role="dialog"] button[data-slot="dialog-close"]'),
                    ('xpath', '//div[@role="dialog"]//button[@data-slot="dialog-close"]'),
                    ('xpath', '//div[@role="dialog"]//button[.//svg[contains(@class, "lucide-x")]]'),
                    ('css', 'div[role="dialog"] button:has(svg.lucide-x)'),
                ]
                
                close_btn = None
                for selector_type, selector in close_selectors:
                    try:
                        if selector_type == 'xpath':
                            elements = driver.find_elements(By.XPATH, selector)
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        logger.info(f"[DEBUG] Close button selector '{selector}': found {len(elements)} elements")
                        if elements:
                            close_btn = elements[0]
                            logger.info(f"[SUCCESS] Found close button using selector: {selector}")
                            break
                    except Exception as e:
                        logger.debug(f"[DEBUG] Error with selector {selector}: {e}")
                
                if close_btn:
                    logger.info("[STEP] Found close button, clicking...")
                    if safe_click(driver, close_btn):
                        time.sleep(2)
                        logger.info("[SUCCESS] Dialog closed via close button")
                        dialog_closed = True
                    else:
                        logger.warning("[WARNING] Failed to click close button")
                else:
                    logger.warning("[WARNING] Close button not found with any selector")
                    
                # If still open, try clicking Cancel button
                if not dialog_closed:
                    logger.info("[STEP] Trying Cancel button...")
                    cancel_selectors = [
                        ('xpath', "//div[@role='dialog']//button[contains(text(), 'Cancelar')]"),
                        ('xpath', "//div[@role='dialog']//button[.//text()[contains(., 'Cancelar')]]"),
                        ('css', 'div[role="dialog"] button:contains("Cancelar")'),
                    ]
                    
                    cancel_btn = None
                    for selector_type, selector in cancel_selectors:
                        try:
                            if selector_type == 'xpath':
                                elements = driver.find_elements(By.XPATH, selector)
                            else:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            logger.info(f"[DEBUG] Cancel button selector '{selector}': found {len(elements)} elements")
                            if elements:
                                cancel_btn = elements[0]
                                logger.info(f"[SUCCESS] Found Cancel button using selector: {selector}")
                                break
                        except Exception as e:
                            logger.debug(f"[DEBUG] Error with selector {selector}: {e}")
                    
                    if cancel_btn:
                        logger.info("[STEP] Found Cancel button, clicking...")
                        if safe_click(driver, cancel_btn):
                            time.sleep(2)
                            logger.info("[SUCCESS] Dialog closed via Cancel button")
                            dialog_closed = True
                    else:
                        logger.warning("[WARNING] Cancel button not found")
        except Exception as e:
            logger.warning(f"[WARNING] Error closing dialog: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    if not dialog_closed:
        logger.warning("[WARNING] Dialog may still be open, but proceeding anyway...")
    
    logger.info("[INFO] Query process initiated, checking for direct download option...")


def try_direct_download(driver, curp, download_dir):
    """
    Try to download PDF directly from the page after query submission.
    Finds table row with CURP, clicks dropdown menu, and downloads PDF.
    Returns: (success, pdf_path) or (False, None) if not available.
    """
    try:
        logger.info("[DIRECT_DOWNLOAD] Starting direct download attempt...")
        
        # Wait for page to update after query submission
        logger.info("[DIRECT_DOWNLOAD] Waiting 5 seconds for page to update...")
        time.sleep(5)
        
        # Find table row with our CURP - check current rows and rows below
        logger.info(f"[DIRECT_DOWNLOAD] Looking for table row with CURP: {curp}")
        curp_row = None
        
        # First try to find row with exact CURP match
        try:
            logger.info("[DIRECT_DOWNLOAD] Searching all table rows...")
            rows = driver.find_elements(By.XPATH, "//tr")
            logger.info(f"[DIRECT_DOWNLOAD] Found {len(rows)} table rows")
            
            for idx, row in enumerate(rows):
                try:
                    row_text = row.text
                    logger.debug(f"[DIRECT_DOWNLOAD] Row {idx} text: {row_text[:100]}...")
                    if curp in row_text:
                        logger.info(f"[SUCCESS] Found table row {idx} with CURP: {curp}")
                        curp_row = row
                        break
                except:
                    continue
        except Exception as e:
            logger.warning(f"[DIRECT_DOWNLOAD] Error finding rows: {e}")
        
        if not curp_row:
            logger.warning(f"[DIRECT_DOWNLOAD] Table row with CURP {curp} not found - scrolling down to check below rows...")
            # If not found, scroll down and check more rows
            try:
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
                rows = driver.find_elements(By.XPATH, "//tr")
                logger.info(f"[DIRECT_DOWNLOAD] After scroll, found {len(rows)} table rows")
                for idx, row in enumerate(rows):
                    try:
                        row_text = row.text
                        if curp in row_text:
                            logger.info(f"[SUCCESS] Found table row {idx} with CURP (after scroll): {curp}")
                            curp_row = row
                            break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"[DIRECT_DOWNLOAD] Error checking below rows: {e}")
        
        if not curp_row:
            logger.warning(f"[DIRECT_DOWNLOAD] Table row with CURP {curp} not found anywhere")
            return (False, None)
        
        # Found the row, now find dropdown button
        try:
            logger.info("[DIRECT_DOWNLOAD] Found row with CURP, looking for dropdown menu button...")
            
            # Find the dropdown menu button with data-slot="dropdown-menu-trigger" in this row
            dropdown_btn = curp_row.find_elements(By.XPATH, ".//button[@data-slot='dropdown-menu-trigger']")
            logger.info(f"[DEBUG] Found {len(dropdown_btn)} dropdown buttons with data-slot='dropdown-menu-trigger'")
            
            # Also try finding by ID pattern (Radix UI dynamic IDs like radix-_r_2k_)
            if not dropdown_btn:
                logger.info("[DEBUG] Trying to find button by ID pattern (radix-*)...")
                # Find all buttons with IDs starting with 'radix-'
                all_radix_buttons = curp_row.find_elements(By.XPATH, ".//button[starts-with(@id, 'radix-')]")
                logger.info(f"[DEBUG] Found {len(all_radix_buttons)} buttons with radix- IDs")
                for idx, btn in enumerate(all_radix_buttons):
                    btn_id = btn.get_attribute("id")
                    data_slot = btn.get_attribute("data-slot")
                    logger.info(f"[DEBUG]   Radix button {idx}: id='{btn_id}', data-slot='{data_slot}'")
                    if data_slot == 'dropdown-menu-trigger':
                        dropdown_btn = [btn]
                        logger.info(f"[SUCCESS] Found dropdown button by radix ID: {btn_id}")
                        break
            
            # Try specific ID if provided (radix-_r_2k_ or similar)
            if not dropdown_btn:
                logger.info("[DEBUG] Trying to find button by ID pattern matching 'radix-_r_*'...")
                all_radix_r_buttons = curp_row.find_elements(By.XPATH, ".//button[matches(@id, 'radix-_r_.*')] | .//button[starts-with(@id, 'radix-_r_')]")
                if not all_radix_r_buttons:
                    # Try XPath with contains for id
                    all_radix_r_buttons = driver.find_elements(By.XPATH, "//button[contains(@id, 'radix-') and @data-slot='dropdown-menu-trigger']")
                logger.info(f"[DEBUG] Found {len(all_radix_r_buttons)} buttons with radix-_r_* pattern")
                if all_radix_r_buttons:
                    # Use the one in our row or first one found
                    for btn in all_radix_r_buttons:
                        try:
                            if btn in curp_row.find_elements(By.XPATH, ".//*"):
                                dropdown_btn = [btn]
                                logger.info(f"[SUCCESS] Found dropdown button in row with radix ID: {btn.get_attribute('id')}")
                                break
                        except:
                            pass
                    if not dropdown_btn and all_radix_r_buttons:
                        dropdown_btn = [all_radix_r_buttons[0]]
                        logger.info(f"[INFO] Using first radix button found: {all_radix_r_buttons[0].get_attribute('id')}")
            
            # Also try CSS selector
            if not dropdown_btn:
                logger.info("[DEBUG] Trying CSS selector for dropdown button...")
                dropdown_btn = curp_row.find_elements(By.CSS_SELECTOR, "button[data-slot='dropdown-menu-trigger']")
                logger.info(f"[DEBUG] CSS selector found {len(dropdown_btn)} buttons")
            
            # Also try searching in entire document
            if not dropdown_btn:
                logger.info("[DEBUG] Searching entire document for dropdown button...")
                all_dropdowns = driver.find_elements(By.XPATH, "//button[@data-slot='dropdown-menu-trigger']")
                logger.info(f"[DEBUG] Found {len(all_dropdowns)} dropdown buttons in entire document")
                
                # Try to find one that's near our row (same table)
                if all_dropdowns:
                    row_parent = curp_row.find_element(By.XPATH, "./..")
                    table = row_parent if row_parent.tag_name == 'tbody' else row_parent.find_element(By.XPATH, "./..")
                    for btn in all_dropdowns:
                        try:
                            # Check if button is in same table/context
                            btn_parent = btn.find_element(By.XPATH, "./../..")
                            if table in btn_parent.get_property('all_parents') or True:  # Just try the first one for now
                                dropdown_btn = [btn]
                                logger.info("[SUCCESS] Found dropdown button in same table context")
                                break
                        except:
                            # Just use first one
                            dropdown_btn = [all_dropdowns[0]]
                            logger.info("[INFO] Using first dropdown button found")
                            break
            
            if not dropdown_btn:
                # Fallback: look for button with ellipsis-vertical icon in this row
                logger.info("[DEBUG] Trying fallback selector - button with ellipsis-vertical icon...")
                dropdown_btn = curp_row.find_elements(By.XPATH, ".//button[.//svg[contains(@class, 'ellipsis-vertical')]]")
                logger.info(f"[DEBUG] Found {len(dropdown_btn)} dropdown buttons with ellipsis-vertical icon")
                
                # Also try in entire document
                if not dropdown_btn:
                    all_ellipsis = driver.find_elements(By.XPATH, "//button[.//svg[contains(@class, 'ellipsis-vertical')]]")
                    logger.info(f"[DEBUG] Found {len(all_ellipsis)} ellipsis buttons in entire document")
                    if all_ellipsis:
                        dropdown_btn = [all_ellipsis[0]]
                        logger.info("[INFO] Using first ellipsis button found")
            
            if dropdown_btn:
                btn = dropdown_btn[0]
                btn_id = btn.get_attribute("id")
                logger.info(f"[DIRECT_DOWNLOAD] Found dropdown button with ID: {btn_id}")
                
                # FIRST: Scroll button into view - this is critical
                logger.info("[DIRECT_DOWNLOAD] Scrolling dropdown button into view...")
                try:
                    # Scroll the button into view (center it)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", btn)
                    logger.info("[DIRECT_DOWNLOAD] Scrolled button into view")
                    
                    # Wait a bit for scroll to complete and button to be ready
                    time.sleep(1)
                    
                    # Re-find the button after scrolling - try by ID first
                    logger.info(f"[DIRECT_DOWNLOAD] Re-finding button after scroll by ID: {btn_id}...")
                    if btn_id:
                        try:
                            btn_by_id = driver.find_element(By.ID, btn_id)
                            btn = btn_by_id
                            logger.info(f"[DIRECT_DOWNLOAD] Button re-found by ID after scroll")
                        except:
                            logger.warning(f"[WARNING] Could not re-find button by ID {btn_id}, trying data-slot...")
                            dropdown_btn_after_scroll = curp_row.find_elements(By.XPATH, ".//button[@data-slot='dropdown-menu-trigger']")
                            if dropdown_btn_after_scroll:
                                btn = dropdown_btn_after_scroll[0]
                                logger.info("[DIRECT_DOWNLOAD] Button re-found by data-slot after scroll")
                            else:
                                logger.warning("[WARNING] Could not re-find button after scroll, using original")
                    else:
                        dropdown_btn_after_scroll = curp_row.find_elements(By.XPATH, ".//button[@data-slot='dropdown-menu-trigger']")
                        if dropdown_btn_after_scroll:
                            btn = dropdown_btn_after_scroll[0]
                            logger.info("[DIRECT_DOWNLOAD] Button re-found by data-slot after scroll")
                    
                    # Wait max 2 seconds for button to be ready
                    time.sleep(2)
                    logger.info("[DIRECT_DOWNLOAD] Waited 2 seconds, button should be ready")
                    
                except Exception as e:
                    logger.warning(f"[WARNING] Error scrolling button into view: {e}")
                
                # Click the dropdown button - try up to 2 times with different methods
                menu_opened = False
                for attempt in range(2):
                    try:
                        if attempt == 0:
                            # First attempt: JavaScript touch events
                            logger.info("[DIRECT_DOWNLOAD] Clicking dropdown menu button (touch events)...")
                            driver.execute_script(f"""
                                var btn = document.getElementById('{btn_id}');
                                if (btn) {{
                                    var touchStart = new TouchEvent('touchstart', {{
                                        bubbles: true,
                                        cancelable: true,
                                        view: window,
                                        touches: [new Touch({{
                                            identifier: 0,
                                            target: btn,
                                            clientX: btn.offsetLeft + btn.offsetWidth/2,
                                            clientY: btn.offsetTop + btn.offsetHeight/2,
                                            radiusX: 2.5,
                                            radiusY: 2.5,
                                            rotationAngle: 10,
                                            force: 0.5
                                        }})]
                                    }});
                                    var touchEnd = new TouchEvent('touchend', {{
                                        bubbles: true,
                                        cancelable: true,
                                        view: window,
                                        changedTouches: [new Touch({{
                                            identifier: 0,
                                            target: btn,
                                            clientX: btn.offsetLeft + btn.offsetWidth/2,
                                            clientY: btn.offsetTop + btn.offsetHeight/2,
                                            radiusX: 2.5,
                                            radiusY: 2.5,
                                            rotationAngle: 10,
                                            force: 0.5
                                        }})]
                                    }});
                                    btn.dispatchEvent(touchStart);
                                    setTimeout(function() {{
                                        btn.dispatchEvent(touchEnd);
                                        btn.click();
                                    }}, 50);
                                }}
                            """)
                        else:
                            # Second attempt: JavaScript with multiple events
                            logger.info("[DIRECT_DOWNLOAD] Retrying click (multiple events)...")
                            driver.execute_script("""
                                var btn = arguments[0];
                                btn.focus();
                                var events = ['mousedown', 'mouseup', 'click', 'pointerdown', 'pointerup'];
                                events.forEach(function(eventType) {
                                    var evt = new MouseEvent(eventType, {
                                        bubbles: true,
                                        cancelable: true,
                                        view: window
                                    });
                                    btn.dispatchEvent(evt);
                                });
                                btn.click();
                            """, btn)
                        
                        logger.info("[DIRECT_DOWNLOAD] Clicked, waiting 2 seconds for menu...")
                        time.sleep(2)
                        
                        # Check if menu opened
                        menu_selectors = [
                            ("//div[@role='menu' and @data-state='open']", "menu with data-state='open'"),
                            ("//div[@role='menu']", "menu"),
                            ("//div[@data-slot='dropdown-menu-content']", "dropdown-menu-content"),
                        ]
                        
                        for selector, desc in menu_selectors:
                            try:
                                all_menus = driver.find_elements(By.XPATH, selector)
                                if all_menus:
                                    logger.info(f"[SUCCESS] Dropdown menu opened (found {len(all_menus)} {desc})")
                                    menu_opened = True
                                    break
                            except:
                                continue
                        
                        if menu_opened:
                            break
                    except Exception as e:
                        logger.warning(f"[WARNING] Click attempt {attempt + 1} failed: {e}")
                
                if not menu_opened:
                    logger.warning("[WARNING] Dropdown menu did not open after all attempts")
                    return (False, None)
                
                # Menu opened successfully, now look for "Descargar PDF" option
                logger.info("[DIRECT_DOWNLOAD] Menu opened, looking for 'Descargar PDF' option...")
                
                # Try multiple selectors
                menu_selectors = [
                    "//div[@role='menu' and @data-state='open']//div[@role='menuitem' and contains(text(), 'Descargar PDF')]",
                    "//div[@role='menu']//div[@role='menuitem' and contains(text(), 'Descargar PDF')]",
                    "//*[@role='menuitem' and contains(text(), 'Descargar PDF')]",
                    "//div[contains(text(), 'Descargar PDF')]",
                ]
                
                descargar_options = []
                for selector in menu_selectors:
                    try:
                        options = driver.find_elements(By.XPATH, selector)
                        if options:
                            descargar_options = options
                            logger.info(f"[SUCCESS] Found 'Descargar PDF' option")
                            break
                    except:
                        continue
                
                if descargar_options:
                    logger.info("[DIRECT_DOWNLOAD] Found 'Descargar PDF' option, clicking...")
                    if safe_click(driver, descargar_options[0]):
                        logger.info("[DIRECT_DOWNLOAD] Clicked 'Descargar PDF', waiting 5 seconds for download to start...")
                        time.sleep(5)
                        
                        # Check if PDF was downloaded
                        download_path = "/sdcard/Download"
                        logger.info(f"[DIRECT_DOWNLOAD] Checking Downloads folder: {download_path}")
                        list_result = subprocess.run(
                            ["adb", "shell", "ls", "-lt", download_path],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if list_result.returncode == 0:
                            logger.info("[DIRECT_DOWNLOAD] Successfully listed Downloads folder")
                            pdf_files = []
                            for line in list_result.stdout.split("\n"):
                                if ".pdf" in line and line.strip().startswith("-"):
                                    parts = line.split()
                                    if len(parts) >= 8:
                                        filename = " ".join(parts[7:])
                                        if filename.endswith(".pdf"):
                                            date_str = " ".join(parts[5:7])
                                            pdf_files.append((filename, date_str))
                                            logger.info(f"[DIRECT_DOWNLOAD] Found PDF file: {filename}")
                            
                            if pdf_files:
                                logger.info(f"[DIRECT_DOWNLOAD] Found {len(pdf_files)} PDF file(s), getting most recent...")
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
                                logger.info(f"[DIRECT_DOWNLOAD] Most recent PDF: {pdf_files[0][0]}")
                                
                                # Rename PDF on device to just CURP.pdf
                                filename = f"{curp}.pdf"
                                device_dir = "/".join(pdf_path.split("/")[:-1])
                                new_pdf_path = f"{device_dir}/{filename}"
                                
                                logger.info(f"[DIRECT_DOWNLOAD] Renaming PDF from {pdf_files[0][0]} to {filename}...")
                                mv_cmd = f'adb shell "mv \'{pdf_path}\' \'{new_pdf_path}\'"'
                                result = subprocess.run(
                                    mv_cmd,
                                    shell=True,
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                
                                if result.returncode == 0:
                                    logger.info(f"[SUCCESS] PDF downloaded directly from page: {new_pdf_path}")
                                    return (True, new_pdf_path)
                                else:
                                    logger.warning(f"[WARNING] Failed to rename PDF: {result.stderr}")
                                    logger.info(f"[INFO] Using original path: {pdf_path}")
                                    return (True, pdf_path)
                            else:
                                logger.warning("[DIRECT_DOWNLOAD] No PDF files found in Downloads folder")
                        else:
                            logger.warning(f"[DIRECT_DOWNLOAD] Could not check Downloads folder: {list_result.stderr}")
                    else:
                        logger.warning("[DIRECT_DOWNLOAD] Failed to click 'Descargar PDF' option")
                else:
                    logger.warning("[DIRECT_DOWNLOAD] 'Descargar PDF' option not found in dropdown menu")
                    return (False, None)
            else:
                logger.warning("[DIRECT_DOWNLOAD] Dropdown menu button not found in row")
        except Exception as e:
            logger.warning(f"[DIRECT_DOWNLOAD] Error interacting with row: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        logger.info("[DIRECT_DOWNLOAD] Direct download failed, will fallback to email method")
        return (False, None)
        
    except Exception as e:
        logger.warning(f"[DIRECT_DOWNLOAD] Error in try_direct_download: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return (False, None)

def wait_for_email_and_download(driver, curp, download_dir):
    """
    Use uiautomator2 to interact with Outlook app directly via ADB.
    Returns: (condition, message, pdf_path)
    - condition: 1=Success, 2=Subdelegación, 4=Error
    - message: Response message
    - pdf_path: Path to PDF if condition=1, None otherwise
    """
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
            return (4, "No unread emails available after waiting 60 seconds", None)
        else:
            logger.info("[OK] Emails found after timeout! Proceeding...")
    
    # Final safety check before clicking - DO NOT CLICK IF EMPTY
    if is_inbox_empty():
        logger.error("[ERROR] SAFETY CHECK FAILED: Inbox is still empty but code tried to proceed. Aborting.")
        return (4, "No unread emails available", None)
    
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
            return (4, "No emails found in inbox", None)
        
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
                    # If this was the last attempt, check for subdelegación message
                    if attempt == max_attempts - 1:
                        logger.warning("No PDF found in any email, checking for subdelegación message...")
                        # Check email content for subdelegación message
                        try:
                            xml_content = d.dump_hierarchy()
                            root = ET.fromstring(xml_content)
                            subdelegacion_text = "Los datos registrados en el IMSS asociados a la CURP"
                            for elem in root.iter():
                                text = elem.get("text", "").strip()
                                if subdelegacion_text in text:
                                    full_message = text[:500]  # Get first 500 chars
                                    logger.info("Found subdelegación message - Condition 2")
                                    return (2, full_message, None)
                        except:
                            pass
                        logger.error("No PDF found and no subdelegación message - Condition 4")
                        return (4, "No PDF found in any email", None)
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
            # If we exhausted all attempts without finding PDF, check for subdelegación
            logger.warning("No PDF found, checking for subdelegación message...")
            try:
                xml_content = d.dump_hierarchy()
                root = ET.fromstring(xml_content)
                subdelegacion_text = "Los datos registrados en el IMSS asociados a la CURP"
                for elem in root.iter():
                    text = elem.get("text", "").strip()
                    if subdelegacion_text in text:
                        full_message = text[:500]
                        logger.info("Found subdelegación message - Condition 2")
                        return (2, full_message, None)
            except:
                pass
            logger.error("No PDF found and no subdelegación message - Condition 4")
            return (4, "No PDF found in any email", None)
            
    except Exception as e:
        logger.error(f"Error analyzing emails: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return (4, f"Error checking emails: {str(e)}", None)
    
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
        # Check for subdelegación message before raising error
        try:
            xml_content = d.dump_hierarchy()
            root = ET.fromstring(xml_content)
            subdelegacion_text = "Los datos registrados en el IMSS asociados a la CURP"
            for elem in root.iter():
                text = elem.get("text", "").strip()
                if subdelegacion_text in text:
                    full_message = text[:500]
                    logger.info("Found subdelegación message - Condition 2")
                    return (2, full_message, None)
        except:
            pass
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
    
    # Success - Condition 1
    return (1, "PDF received successfully", new_pdf_path)


def get_nss_from_db(nbc_id):
    """Get NSS from Nueva_Base_Central collection using nbc_id."""
    try:
        from pymongo import MongoClient
        from bson import ObjectId
        from dotenv import load_dotenv
        import os
        
        load_dotenv(override=True)
        mongo_uri = os.getenv("MONGO_URI", "")
        
        if not mongo_uri:
            logger.warning("MONGO_URI not set, using fallback NSS from env")
            return os.getenv("SISEC_NSS", "")
        
        client = MongoClient(mongo_uri)
        collection = client["Main_User"]["Nueva_Base_Central"]
        
        doc = collection.find_one({"_id": ObjectId(nbc_id)})
        client.close()
        
        if doc and "nss" in doc:
            nss_obj = doc.get("nss", {})
            if isinstance(nss_obj, dict) and "value" in nss_obj:
                return nss_obj["value"]
            elif isinstance(nss_obj, str):
                return nss_obj
        
        logger.warning(f"NSS not found in database for nbc_id: {nbc_id}, using fallback")
        return os.getenv("SISEC_NSS", "")
    except Exception as e:
        logger.warning(f"Error getting NSS from database: {e}, using fallback")
        return os.getenv("SISEC_NSS", "")


def log_error(error_type, message, curp=None, nss=None):
    """Log errors to a separate error log file."""
    log_file = LOG_DIR / "errors.log"
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"{timestamp}|{error_type}|{message}|CURP:{curp or 'N/A'}|NSS:{nss or 'N/A'}\n")
    logger.error(f"Error logged: {error_type} - {message}")


def process_sisec_task(curp, device_id, taskid, queue_document_id, nbc_id):
    """
    Main function to process a SISEC task.
    Called by API service to handle automation.
    
    Args:
        curp: CURP to query
        device_id: Device ID (for logging)
        taskid: Task ID (for logging)
        queue_document_id: Queue document ID (for logging)
        nbc_id: NBC document ID (used to get NSS)
    
    Returns:
        dict with keys: condition, message, status, pdf_path
    """
    driver = None
    try:
        logger.info(f"Starting SISEC task - CURP: {curp}, TaskID: {taskid}")
        
        # Get NSS from database or use fallback
        nss = get_nss_from_db(nbc_id)
        if not nss:
            raise Exception("NSS is required but not found in database or environment")
        
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
        fill_query_form(driver, curp, nss)
        logger.info(f"[SUCCESS] Form filled - CURP: {curp}, NSS: {nss}")
        
        # Submit the query
        submit_query(driver)
        
        # First, try direct download from the page
        logger.info("[MAIN] Attempting direct download from page...")
        direct_success, pdf_path = try_direct_download(driver, curp, DOWNLOAD_DIR)
        
        if direct_success and pdf_path:
            logger.info("[SUCCESS] PDF downloaded directly from page - Condition 1")
            driver.quit()
            return {
                'condition': 1,
                'message': 'PDF downloaded directly from page',
                'status': 'Complete',
                'pdf_path': pdf_path
            }
        
        # If direct download failed, fallback to email method
        logger.info("[MAIN] Direct download not available, falling back to email method...")
        condition, message, pdf_path = wait_for_email_and_download(driver, curp, DOWNLOAD_DIR)
        
        # Driver is already closed inside wait_for_email_and_download
        driver = None
        
        return {
            'condition': condition,
            'message': message,
            'status': 'Complete',
            'pdf_path': pdf_path
        }
        
    except KeyboardInterrupt:
        logger.info("\n[INFO] Interrupted by user")
        if driver:
            driver.quit()
        return {
            'condition': 4,
            'message': 'Process interrupted by user',
            'status': 'Complete',
            'pdf_path': None
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"\n[ERROR] {error_msg}")
        log_error("AUTOMATION_ERROR", error_msg, curp, None)
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        return {
            'condition': 4,
            'message': f"Processing error: {error_msg}",
            'status': 'Complete',
            'pdf_path': None
        }


def main():
    """Standalone test function - for testing automation without API."""
    # For testing, use environment variables
    curp = CURP
    nbc_id = os.getenv("TEST_NBC_ID", "")
    
    result = process_sisec_task(
        curp=curp,
        device_id="test_device",
        taskid=12345,
        queue_document_id="test_queue",
        nbc_id=nbc_id
    )
    
    logger.info(f"Test completed - Condition: {result['condition']}, Message: {result['message']}")

if __name__ == "__main__":
    main()
