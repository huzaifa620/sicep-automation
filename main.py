from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
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

# Email monitoring settings
EMAIL_SENDER = "historia.laboral@imss.gob.mx"
EMAIL_SUBJECT = "Constancia de Semanas Cotizadas del Asegurado"
EMAIL_WAIT_TIMEOUT = int(os.getenv("EMAIL_WAIT_TIMEOUT", "300"))  # 5 minutes default
EMAIL_CHECK_INTERVAL = int(os.getenv("EMAIL_CHECK_INTERVAL", "10"))  # Check every 10 seconds
OUTLOOK_PACKAGE = "com.microsoft.office.outlook"  # Outlook Android package name

# Download settings
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
RECORD_DIR = Path(os.getenv("RECORD_DIR", "recordings"))

# Recording settings
ENABLE_RECORDING = os.getenv("ENABLE_RECORDING", "false").lower() == "true"

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)
RECORD_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"automation_{datetime.now().strftime('%Y%m%d')}.log"),
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

def setup_native_driver():
    """Initialize and return Appium WebDriver for native Android app."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android"
    options.app_package = OUTLOOK_PACKAGE
    options.app_activity = "com.microsoft.office.outlook.ui.activities.MainActivity"
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
    
    # Wait for the dialog to close or for a success message
    # The dialog should close when the process starts
    time.sleep(2)
    
    # Wait for any loading indicators to disappear
    try:
        # Wait for the dialog to close
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"][data-state="open"]')))
        logger.info("Query dialog closed, process initiated")
    except:
        logger.warning("Dialog may have already closed or different structure")
    
    # Additional wait for the process to complete on the server side
    # The actual email will be sent asynchronously
    logger.info("Query process initiated. Email will be sent shortly...")

def get_ui_dump():
    """Get UI hierarchy dump using ADB."""
    # Try method 1: exec-out (direct output)
    try:
        result = subprocess.run(
            ["adb", "exec-out", "uiautomator", "dump", "/dev/tty"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        if result.returncode == 0 and result.stdout:
            # Remove the "UI hierarchy dumped to: /dev/tty" message
            output = result.stdout
            if "UI hierarchy dumped to:" in output:
                xml_start = output.find("<?xml")
                if xml_start != -1:
                    output = output[xml_start:]
            if output.strip().startswith("<?xml"):
                return output.strip()
    except Exception as e:
        logger.debug(f"exec-out method failed: {e}")
    
    # Try method 2: dump to file and read
    dump_path = "/sdcard/window_dump.xml"
    try:
        # Dump UI hierarchy to file
        result = subprocess.run(
            ["adb", "shell", "uiautomator", "dump", dump_path],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        time.sleep(1)  # Wait for file to be written
        
        # Read the dump file
        result = subprocess.run(
            ["adb", "shell", "cat", dump_path],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        if result.returncode == 0 and result.stdout:
            xml_content = result.stdout.strip()
            if xml_content.startswith("<?xml"):
                return xml_content
    except Exception as e:
        logger.debug(f"File dump method failed: {e}")
    
    # Try method 3: pull the file
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.xml', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Dump to device
        subprocess.run(
            ["adb", "shell", "uiautomator", "dump", dump_path],
            timeout=10,
            shell=False
        )
        time.sleep(1)
        
        # Pull file
        result = subprocess.run(
            ["adb", "pull", dump_path, tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )
        
        if result.returncode == 0:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            os.unlink(tmp_path)
            if content.startswith("<?xml"):
                return content
    except Exception as e:
        logger.debug(f"Pull method failed: {e}")
    
    raise Exception("All methods failed to get UI dump")

def find_element_by_text(xml_content, text_keywords, clickable=True):
    """Find element in UI dump by text and return its bounds."""
    try:
        root = ET.fromstring(xml_content)
        for elem in root.iter():
            text = elem.get("text", "").lower()
            content_desc = elem.get("content-desc", "").lower()
            bounds = elem.get("bounds", "")
            clickable_attr = elem.get("clickable", "false")
            
            # Check if text matches keywords
            matches = any(keyword.lower() in text or keyword.lower() in content_desc for keyword in text_keywords)
            
            if matches and bounds and (not clickable or clickable_attr == "true"):
                # Parse bounds: [x1,y1][x2,y2]
                match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    logger.debug(f"Found element: text='{text[:50]}', bounds={bounds}, center=({center_x}, {center_y})")
                    return center_x, center_y
    except ET.ParseError as e:
        logger.error(f"XML parse error: {e}")
        logger.debug(f"XML content (first 500 chars): {xml_content[:500]}")
    except Exception as e:
        logger.error(f"Error parsing UI dump: {e}")
        import traceback
        logger.debug(traceback.format_exc())
    return None, None

def tap_coordinates(x, y):
    """Tap at coordinates using ADB."""
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], timeout=5)
    time.sleep(1)

def swipe_down():
    """Swipe down to scroll."""
    result = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True, timeout=5)
    width, height = 1080, 1920  # defaults
    if result.returncode == 0:
        try:
            size_str = result.stdout.strip().split()[-1]
            width, height = map(int, size_str.split('x'))
        except:
            pass
    
    center_x = width // 2
    start_y = int(height * 0.7)
    end_y = int(height * 0.3)
    subprocess.run(["adb", "shell", "input", "swipe", str(center_x), str(start_y), str(center_x), str(end_y), "500"], timeout=5)
    time.sleep(2)

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
    
    # Click email below the ad (ad ends around y=789, email should be below)
    logger.info("Clicking email below ad...")
    width, height = d.window_size()
    
    # Ad content-desc shows bounds [0,548][1080,789], so email is below y=800
    # Click at middle x, around y=900 (below ad, above bottom nav)
    click_x = width // 2
    click_y = 900  # Below ad area, in email list area
    
    logger.info(f"Clicking at ({click_x}, {click_y}) - below ad area")
    d.click(click_x, click_y)
    time.sleep(4)
    
    # Click PDF attachment button
    logger.info("Clicking PDF attachment...")
    time.sleep(3)  # Wait for email to fully load
    
    pdf_button = None
    
    # Try multiple strategies to find PDF button
    try:
        pdf_button = d(descriptionContains="Constancia de Semanas Cotizadas del Asegurado.pdf", clickable=True)
        if pdf_button.exists:
            logger.info("Found PDF button by full filename")
    except:
        pass
    
    if not pdf_button or not pdf_button.exists:
        try:
            pdf_button = d(descriptionContains="File Type PDF", clickable=True)
            if pdf_button.exists:
                logger.info("Found PDF button by 'File Type PDF'")
        except:
            pass
    
    if not pdf_button or not pdf_button.exists:
        try:
            pdf_button = d(descriptionContains=".pdf", clickable=True)
            if pdf_button.exists:
                logger.info("Found PDF button by '.pdf'")
        except:
            pass
    
    if pdf_button and pdf_button.exists:
        pdf_button.click()
        time.sleep(2)
    else:
        raise Exception("Could not find PDF attachment button")
    
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
    mobile_recording = None
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
        submit_query(driver)
        
        # Wait for email and download PDF
        logger.info("Waiting for email and downloading PDF...")
        pdf_path = wait_for_email_and_download(driver, CURP, DOWNLOAD_DIR)
        
        # Driver is already closed inside wait_for_email_and_download
        driver = None
        
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
