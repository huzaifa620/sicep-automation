# SICEP Automation

A Python automation project using Selenium to interact with the SISEC website.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows (PowerShell):
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - On Windows (CMD):
     ```bash
     venv\Scripts\activate.bat
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python main.py
```

## Requirements

- Python 3.7+
- Chrome browser installed
- ChromeDriver (Selenium will handle this automatically with newer versions)
