import sys
import subprocess
import os
from database import register_device
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_adb_available():
    """Check if ADB is installed and accessible."""
    try:
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def check_adb_devices_connected():
    """Check if any devices are connected to ADB."""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line for line in lines if line.strip() and 'device' in line]
            return len(devices) > 0
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def get_device_serial_from_adb():
    """Try to extract device serial number from ADB."""
    try:
        result = subprocess.run(
            ["adb", "get-serialno"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            serial = result.stdout.strip()
            if serial != "unknown":
                return serial, None
            else:
                return None, "Device serial is 'unknown' - device may not be properly authorized"
    except FileNotFoundError:
        return None, "ADB not found - is Android SDK Platform Tools installed?"
    except subprocess.TimeoutExpired:
        return None, "ADB command timed out"
    except Exception as e:
        return None, f"ADB error: {str(e)}"
    return None, "No device serial found"


def get_device_model_from_adb():
    """Try to extract device model from ADB."""
    try:
        result = subprocess.run(
            ["adb", "shell", "getprop", "ro.product.model"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            model = result.stdout.strip()
            # Convert to lowercase and replace spaces with underscores
            return model.lower().replace(" ", "_"), None
    except FileNotFoundError:
        return None, "ADB not found - is Android SDK Platform Tools installed?"
    except subprocess.TimeoutExpired:
        return None, "ADB command timed out"
    except Exception as e:
        return None, f"ADB error: {str(e)}"
    return None, "No device model found"


def main():
    """Register a device manually."""
    print("=" * 60)
    print("Device Registration Tool")
    print("=" * 60)
    print()
    
    device_info = {}
    
    # Try to extract device serial from ADB automatically
    print("Attempting to extract device information from ADB...")
    
    # Check if ADB is available
    if not check_adb_available():
        print("⚠ ADB is not installed or not in PATH")
        print("  Tip: Install Android SDK Platform Tools and add it to your PATH")
        print("  Or manually enter device information below\n")
    elif not check_adb_devices_connected():
        print("⚠ No devices connected to ADB")
        print("  Tip: Connect your device via USB and enable USB debugging")
        print("  Run 'adb devices' to verify connection\n")
    else:
        print("✓ ADB is available and device(s) are connected\n")
    
    device_serial, serial_error = get_device_serial_from_adb()
    if device_serial:
        print(f"✓ Found device serial: {device_serial}")
        use_serial = input(f"Use this as 'device' field? (Y/n): ").strip().lower()
        if use_serial in ['', 'y', 'yes']:
            device_info["device"] = device_serial
        else:
            device_serial = None
    else:
        print(f"✗ Could not extract device serial from ADB")
        if serial_error:
            print(f"  Reason: {serial_error}")
    
    # Try to extract device model from ADB automatically
    device_model, model_error = get_device_model_from_adb()
    if device_model:
        print(f"✓ Found device model: {device_model}")
    else:
        print(f"✗ Could not extract device model from ADB")
        if model_error:
            print(f"  Reason: {model_error}")
    
    print("\n" + "-" * 60)
    print("Manual Entry (press Enter to skip optional fields)")
    print("-" * 60)
    
    # Get device field if not auto-extracted
    if "device" not in device_info:
        device_input = input("Device serial/identifier (e.g., '6201RMT14'): ").strip()
        if device_input:
            device_info["device"] = device_input
    
    # Get device_name (optional)
    device_name = None
    if device_model:
        use_model = input(f"Use '{device_model}' as device_name? (Y/n): ").strip().lower()
        if use_model in ['', 'y', 'yes']:
            device_name = device_model
        else:
            device_name_input = input("Enter device name (optional): ").strip()
            if device_name_input:
                device_name = device_name_input
    else:
        device_name_input = input("Enter device name (optional, e.g., 'redmi_note_14'): ").strip()
        if device_name_input:
            device_name = device_name_input
    
    # Get instance (optional)
    instance_input = input("Instance (e.g., 'SISEC-HUZAIFA'): ").strip()
    if instance_input:
        device_info["instance"] = instance_input
    
    # Get process (optional)
    process_input = input("Process (e.g., 'SISEC'): ").strip()
    if process_input:
        device_info["process"] = process_input
    
    # Additional optional fields
    print("\nAdditional optional fields:")
    platform_input = input("Platform (e.g., 'Android'): ").strip()
    if platform_input:
        device_info["platform"] = platform_input
    
    appium_url_input = input("Appium URL: ").strip()
    if appium_url_input:
        device_info["appium_url"] = appium_url_input
    
    # Register device
    try:
        print("\nRegistering device...")
        device_id = register_device(device_name=device_name, device_info=device_info if device_info else None)
        
        print("\n" + "=" * 60)
        print("✓ Device registered successfully!")
        print("=" * 60)
        print(f"Device ID: {device_id}")
        if device_name:
            print(f"Device Name: {device_name}")
        print("\nYou can now use this device_id in API requests.")
        print("=" * 60)
        
        return device_id
        
    except Exception as e:
        print(f"\n✗ Error registering device: {e}")
        logger.error(f"Registration failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nRegistration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
