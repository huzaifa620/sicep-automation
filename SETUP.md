# SISEC Automation Setup Guide

## Quick Start

1. Install Python 3.8+ (if not already installed)
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with credentials
4. Run: `python main.py`

## Dependencies

- **selenium** - Web automation for browser control
- **Appium-Python-Client** - Mobile device automation
- **python-dotenv** - Environment variable management
- **uiautomator2** - Android UI automation

## Technologies Used

- **Appium** - Mobile automation framework
- **Selenium WebDriver** - Browser automation
- **uiautomator2** - Android UI interaction
- **ADB** - Android Debug Bridge (for device commands)
- **Outlook Android App** - Email client automation

## Environment Variables Needed

Create a `.env` file with:
- `SISEC_USERNAME` - Your SISEC login email
- `SISEC_PASSWORD` - Your SISEC password
- `SISEC_BASE_URL` - SISEC website URL
- `SISEC_CURP` - Test CURP (for standalone runs)
- `SISEC_NSS` - Test NSS (for standalone runs)
- `APPIUM_SERVER` - Appium server URL (usually `http://localhost:4723`)
- `SISEC_TIMEOUT` - Timeout in seconds (default: 30)
- `SISEC_DELAY` - Delay between actions (default: 1.0)

## Prerequisites

- Android device connected via USB with USB debugging enabled
- Appium server running
- Outlook app installed on Android device
- ADB installed and in PATH

That's it! You're ready to go.
