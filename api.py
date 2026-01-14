"""
SISEC Scraper API Service
Main API endpoint for receiving requests from G_IMSS orchestrator
"""

from flask import Flask, request, jsonify
from threading import Thread
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from automation import process_sisec_task
from database import update_rw, mark_device_busy, mark_device_available

load_dotenv(override=True)

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/api_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Track if we're currently processing a task
is_processing = False


def validate_request(data):
    """Validate incoming request data."""
    required_fields = ['curp', 'device_id', 'taskid', 'queue_document_id', 'nbc_id']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Basic CURP validation (18 characters, alphanumeric)
    curp = data.get('curp', '')
    if len(curp) != 18 or not curp.isalnum():
        return False, "Invalid CURP format (must be 18 alphanumeric characters)"
    
    return True, None


@app.route('/process', methods=['POST'])
def process_task():
    """
    Main API endpoint for processing SISEC tasks.
    Returns immediately and processes task in background.
    """
    global is_processing
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Validate request
        is_valid, error_msg = validate_request(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'curp': data.get('curp', ''),
                'taskid': data.get('taskid', ''),
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Check if we're already processing
        if is_processing:
            return jsonify({
                'status': 'busy',
                'message': 'Server at maximum capacity, try again later',
                'curp': data.get('curp', ''),
                'taskid': data.get('taskid', '')
            }), 429
        
        # Extract request data
        curp = data['curp']
        device_id = data['device_id']
        taskid = data['taskid']
        queue_document_id = data['queue_document_id']
        nbc_id = data['nbc_id']
        
        logger.info(f"Received task request - CURP: {curp}, TaskID: {taskid}, Device: {device_id}")
        
        # Mark device as busy
        try:
            mark_device_busy(device_id)
        except Exception as e:
            logger.warning(f"Failed to mark device as busy: {e}")
        
        # Start background task
        is_processing = True
        thread = Thread(
            target=process_task_background,
            args=(curp, device_id, taskid, queue_document_id, nbc_id),
            daemon=True
        )
        thread.start()
        
        # Return success response immediately
        return jsonify({
            'status': 'success',
            'message': 'Task accepted for processing',
            'curp': curp,
            'taskid': taskid,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in process_task endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'curp': data.get('curp', '') if 'data' in locals() else '',
            'taskid': data.get('taskid', '') if 'data' in locals() else '',
            'timestamp': datetime.now().isoformat()
        }), 500


def process_task_background(curp, device_id, taskid, queue_document_id, nbc_id):
    """
    Background task processor.
    Handles the actual SISEC automation and database updates.
    """
    global is_processing
    
    try:
        logger.info(f"Starting background processing for CURP: {curp}, TaskID: {taskid}")
        
        # Process the SISEC task
        result = process_sisec_task(curp, device_id, taskid, queue_document_id, nbc_id)
        
        # result contains: condition, message, status, pdf_path (optional)
        condition = result.get('condition')
        message = result.get('message', '')
        status = result.get('status', 'Complete')
        pdf_path = result.get('pdf_path')
        
        logger.info(f"Task completed - Condition: {condition}, Status: {status}")
        
        # Update database based on result
        update_rw(
            curp=curp,
            condition=condition,
            message=message,
            status=status,
            queue_document_id=queue_document_id
        )
        
        # If we got a PDF (Condition 1), we'd process it here
        # For now, we just log it
        if pdf_path:
            logger.info(f"PDF downloaded at: {pdf_path}")
            # TODO: Extract PDF data and update imss collection
        
    except Exception as e:
        logger.error(f"Error in background processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Update database with error condition
        try:
            update_rw(
                curp=curp,
                condition=4,  # Error condition
                message=f"Processing error: {str(e)}",
                status="Complete",
                queue_document_id=queue_document_id
            )
        except Exception as db_error:
            logger.error(f"Failed to update database with error: {db_error}")
    
    finally:
        # Mark device as available again
        try:
            mark_device_available(device_id)
        except Exception as e:
            logger.warning(f"Failed to mark device as available: {e}")
        
        is_processing = False
        logger.info(f"Background processing completed for CURP: {curp}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'processing': is_processing
    }), 200


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get port from environment or use default
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"Starting SISEC API service on {host}:{port}")
    app.run(host=host, port=port, debug=False)
