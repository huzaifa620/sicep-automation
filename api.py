from flask import Flask, request, jsonify
from threading import Thread
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from automation import process_sisec_task
from database import update_rw, mark_device_busy, mark_device_available, get_mongo_client
from pymongo.errors import PyMongoError
from bson import ObjectId

load_dotenv(override=True)

app = Flask(__name__)


def convert_objectid_to_str(obj):
    """Recursively convert all ObjectId instances to strings."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    else:
        return obj

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


@app.route('/test-db', methods=['GET'])
def test_database():
    """
    Test MongoDB connection and retrieve sample data from collections.
    Returns connection status and sample documents from various collections.
    """
    try:
        # Test MongoDB connection
        client = None
        connection_status = {
            'connected': False,
            'error': None,
            'server_info': None
        }
        
        collections_data = {}
        
        try:
            # Get MongoDB client with timeout
            logger.info("Attempting to connect to MongoDB...")
            # Use MongoClient directly with timeout settings for this test
            from pymongo import MongoClient
            import os
            from dotenv import load_dotenv
            load_dotenv(override=True)
            
            mongo_uri = os.getenv("MONGO_URI", "")
            if not mongo_uri:
                raise ValueError("MONGO_URI not set in environment variables")
            
            # Create client with connection timeout (10 seconds)
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=10000,  # 10 seconds timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=30000  # 30 seconds for queries
            )
            
            # Test connection by getting server info (with timeout protection)
            try:
                logger.info("Getting MongoDB server info...")
                server_info = client.server_info()
                connection_status['connected'] = True
                connection_status['server_info'] = {
                    'version': server_info.get('version'),
                    'host': str(client.address[0]) if hasattr(client, 'address') else 'N/A',
                    'port': client.address[1] if hasattr(client, 'address') and len(client.address) > 1 else 'N/A'
                }
                logger.info("MongoDB connection successful")
            except Exception as e:
                connection_status['error'] = f"Failed to get server info: {str(e)}"
                logger.error(f"Server info error: {e}")
                # If server_info fails, connection might still work, so continue
            
            # Get sample data from dev_devices collection (Mini_Base_Central)
            try:
                logger.info("Querying dev_devices collection...")
                dev_devices_col = client["Mini_Base_Central"]["dev_devices"]
                devices = list(dev_devices_col.find({}).limit(5))
                
                # Convert ObjectId to string for JSON serialization
                for i, device in enumerate(devices):
                    devices[i] = convert_objectid_to_str(device)
                    if '_id' in devices[i]:
                        del devices[i]['_id']
                    if 'last_updated' in devices[i] and devices[i]['last_updated']:
                        if hasattr(devices[i]['last_updated'], 'isoformat'):
                            devices[i]['last_updated'] = devices[i]['last_updated'].isoformat()
                    if 'created_at' in devices[i] and devices[i]['created_at']:
                        if hasattr(devices[i]['created_at'], 'isoformat'):
                            devices[i]['created_at'] = devices[i]['created_at'].isoformat()
                
                collections_data['dev_devices'] = {
                    'database': 'Mini_Base_Central',
                    'collection': 'dev_devices',
                    'sample_documents': devices,
                    'sample_count': len(devices)
                }
            except Exception as e:
                collections_data['dev_devices'] = {
                    'error': str(e),
                    'database': 'Mini_Base_Central',
                    'collection': 'dev_devices'
                }
            
        except PyMongoError as e:
            connection_status['error'] = f"MongoDB error: {str(e)}"
            logger.error(f"MongoDB connection error: {e}")
        except Exception as e:
            connection_status['error'] = f"Connection error: {str(e)}"
            logger.error(f"Database test error: {e}")
        finally:
            if client:
                client.close()
        
        # Build response
        response = {
            'status': 'success' if connection_status['connected'] else 'error',
            'timestamp': datetime.now().isoformat(),
            'connection': connection_status,
            'collections': collections_data
        }
        
        status_code = 200 if connection_status['connected'] else 500
        logger.info(f"Test database completed with status: {status_code}")
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Error in test_database endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f"Unexpected error: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get port from environment or use default
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    # Enable debug mode for auto-reload on code changes
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting SISEC API service on {host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
