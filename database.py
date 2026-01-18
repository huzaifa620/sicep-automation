from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = "Main_User"
MINI_DB_NAME = "Mini_Base_Central"


def get_mongo_client():
    """Get MongoDB client connection."""
    if not MONGO_URI:
        raise ValueError("MONGO_URI not set in environment variables")
    return MongoClient(MONGO_URI)


def update_rw(curp, condition, message, status, queue_document_id=None, extracted_data=None):
    """
    Update Registro_works and optionally update queue document, NBC, imss, and sl_pendidate.
    
    Args:
        curp: CURP value
        condition: RW condition (1=Success, 2=Subdelegación, 4=Error)
        message: Message to store
        status: Status value (usually "Complete")
        queue_document_id: Optional queue document ID to update
        extracted_data: Optional extracted PDF data dictionary (for Condition 1)
    """
    client = None
    try:
        client = get_mongo_client()
        collection = client[DB_NAME]["Registro_works"]
        
        # Find the latest document by 'i_date'
        query = {
            "Curp": curp
        }
        
        latest_doc = collection.find_one(query, sort=[("i_date", -1)])
        if not latest_doc:
            logger.warning(f"No Registro_works document found for CURP: {curp}")
            return
        
        nbc_id = latest_doc.get("NBC_id")
        
        # Handle Condition 2: Subdelegación
        if condition == 2:
            if nbc_id:
                nbc_collection = client[DB_NAME]["Nueva_Base_Central"]
                nbc_collection.update_one(
                    {"_id": nbc_id},
                    {
                        "$set": {
                            "imss": {"status": "subdelegacion", "date": datetime.now()},
                            "searchlook.imss": datetime.now()
                        }
                    }
                )
                logger.info(f"Updated NBC with subdelegación status for CURP: {curp}")
            else:
                logger.warning("NBC_id not found in latest Registro_works document.")
        
        # Handle Condition 1: Success - Update NBC, imss, and sl_pendidate
        if condition == 1:
            if nbc_id:
                try:
                    nbc_collection = client[DB_NAME]["Nueva_Base_Central"]
                    
                    # Update NBC with success status and date
                    nbc_collection.update_one(
                        {"_id": nbc_id},
                        {
                            "$set": {
                                "imss": {"status": "s", "date": datetime.now()},
                                "searchlook.imss": datetime.now()
                            }
                        }
                    )
                    logger.info(f"Updated NBC with success status 's' for CURP: {curp}")
                    
                    # Update imss collection
                    # Note: The imss document _id IS the NBC_id (same ObjectId)
                    imss_collection = client[DB_NAME]["imss"]
                    imss_doc = imss_collection.find_one({"_id": nbc_id})
                    
                    # Prepare update data with extracted PDF data if available
                    imss_update_data = {}
                    
                    # Add extracted PDF data to imss document if available
                    if extracted_data:
                        imss_update_data.update(extracted_data)
                        logger.info(f"Including extracted PDF data in imss update: {list(extracted_data.keys())}")
                    
                    if imss_doc:
                        # Update existing imss document
                        if imss_update_data:
                            imss_collection.update_one(
                                {"_id": nbc_id},
                                {"$set": imss_update_data}
                            )
                            logger.info(f"Updated existing imss document for CURP: {curp}")
                    else:
                        # Create new imss document if it doesn't exist
                        # Note: _id should be the NBC_id, and extracted_data should contain
                        # the fields like Nombre, Nombres, curp_sc, detalle_semanas, job_cotizations, etc.
                        new_imss_doc = {
                            "_id": nbc_id,  # _id is the NBC_id
                            "created_at": datetime.now(),
                            **imss_update_data
                        }
                        imss_collection.insert_one(new_imss_doc)
                        logger.info(f"Created new imss document with NBC_id as _id for CURP: {curp}")
                    
                    # Update sl_pendidate collection
                    sl_pendidate_collection = client[DB_NAME]["sl_pendidate"]
                    # Find document by CURP
                    pendidate_doc = sl_pendidate_collection.find_one({"Curp": curp})
                    
                    if pendidate_doc:
                        # Update existing sl_pendidate document
                        sl_pendidate_collection.update_one(
                            {"_id": pendidate_doc["_id"]},
                            {
                                "$set": {
                                    "imss_status": "processed",
                                    "imss_processed_date": datetime.now(),
                                    "updated_at": datetime.now()
                                }
                            }
                        )
                        logger.info(f"Updated existing sl_pendidate document for CURP: {curp}")
                    else:
                        # Create new sl_pendidate document if it doesn't exist
                        new_pendidate_doc = {
                            "Curp": curp,
                            "NBC_id": nbc_id,
                            "imss_status": "processed",
                            "imss_processed_date": datetime.now(),
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                        sl_pendidate_collection.insert_one(new_pendidate_doc)
                        logger.info(f"Created new sl_pendidate document for CURP: {curp}")
                        
                except Exception as e:
                    logger.error(f"Error updating collections for Condition 1: {e}")
                    # Continue with Registro_works update even if other collections fail
            else:
                logger.warning("NBC_id not found in latest Registro_works document for Condition 1.")
        
        # Handle Condition 4: Error
        if condition == 4:
            if nbc_id:
                nbc_collection = client[DB_NAME]["Nueva_Base_Central"]
                
                # Check for specific retry message
                if message.strip() == "El correo ya fue modificado durante el dia":
                    new_status = "RETRY_AFTER_MIDNIGHT"
                else:
                    new_status = "nf"
                
                nbc_collection.update_one(
                    {"_id": nbc_id},
                    {
                        "$set": {
                            "imss": {"status": new_status, "date": datetime.now()},
                            "searchlook.imss": datetime.now()
                        }
                    }
                )
                logger.info(f"Updated NBC with error status '{new_status}' for CURP: {curp}")
            else:
                logger.warning("NBC_id not found in latest Registro_works document.")
        
        # Update Registro_works
        update_fields = {
            "Condition": condition,
            "Message": message,
            "Status": status,
            "f_date": datetime.now()
        }
        
        result = collection.update_one(
            {"_id": latest_doc["_id"]},
            {"$set": update_fields}
        )
        
        if result.modified_count > 0:
            logger.info(f"Successfully updated Registro_works for CURP: {curp}")
        else:
            logger.info(f"Registro_works found, but nothing modified for CURP: {curp}")
        
        # Update queue document if queue_id exists
        queue_id_to_use = latest_doc.get("queue_id") or queue_document_id
        
        if queue_id_to_use:
            try:
                # Determine success: true for conditions 1, 2, 3 | false for 4
                success = condition in [1, 2, 3]
                
                queue_collection = client[MINI_DB_NAME]['imss_queue_iad']
                
                queue_result = queue_collection.update_one(
                    {"_id": ObjectId(queue_id_to_use)},
                    {
                        "$set": {
                            "Status": "Complete",
                            "success": success,
                            "Message": message,
                            "completed_at": datetime.now()
                        }
                    }
                )
                
                if queue_result.modified_count > 0:
                    logger.info(f"Successfully updated queue document with success={success}")
                else:
                    logger.warning(f"Queue document found but nothing modified")
                    
            except Exception as queue_error:
                logger.error(f"Failed to update queue: {str(queue_error)}")
    
    except PyMongoError as e:
        logger.error(f"MongoDB error in update_rw: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in update_rw: {e}")
        raise
    finally:
        if client:
            client.close()


def mark_device_busy(device_id):
    """Mark device as busy in dev_devices collection using device serial."""
    client = None
    try:
        client = get_mongo_client()
        collection = client[MINI_DB_NAME]["dev_devices"]
        
        result = collection.update_one(
            {"device": device_id},
            {
                "$set": {
                    "available": False,
                    "online": True,
                    "last_updated": datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Marked device {device_id} as busy")
        else:
            logger.warning(f"Device {device_id} not found or already busy")
    
    except PyMongoError as e:
        logger.error(f"MongoDB error marking device busy: {e}")
        raise
    except Exception as e:
        logger.error(f"Error marking device busy: {e}")
        raise
    finally:
        if client:
            client.close()


def mark_device_available(device_id):
    """Mark device as available in dev_devices collection using device serial."""
    client = None
    try:
        client = get_mongo_client()
        collection = client[MINI_DB_NAME]["dev_devices"]
        
        result = collection.update_one(
            {"device": device_id},
            {
                "$set": {
                    "available": True,
                    "online": True,
                    "last_updated": datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Marked device {device_id} as available")
        else:
            logger.warning(f"Device {device_id} not found")
    
    except PyMongoError as e:
        logger.error(f"MongoDB error marking device available: {e}")
        raise
    except Exception as e:
        logger.error(f"Error marking device available: {e}")
        raise
    finally:
        if client:
            client.close()


def register_device(device_name=None, device_info=None):
    """
    Register a new device in dev_devices collection.
    
    Args:
        device_name: Optional device name/identifier
        device_info: Optional additional device information (dict)
    
    Returns:
        device_id: The ObjectId string of the newly registered device
    """
    client = None
    try:
        client = get_mongo_client()
        collection = client[MINI_DB_NAME]["dev_devices"]
        
        # Create device document
        device_doc = {
            "available": True,
            "online": True,
            "last_updated": datetime.now(),
            "created_at": datetime.now()
        }
        
        # Add optional fields
        if device_name:
            device_doc["device_name"] = device_name
        
        if device_info:
            device_doc.update(device_info)
        
        # Insert device
        result = collection.insert_one(device_doc)
        device_id = str(result.inserted_id)
        
        logger.info(f"Registered new device: {device_id} (name: {device_name or 'N/A'})")
        return device_id
    
    except PyMongoError as e:
        logger.error(f"MongoDB error registering device: {e}")
        raise
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        raise
    finally:
        if client:
            client.close()
