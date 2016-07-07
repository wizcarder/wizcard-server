from gcm import GCM
import logging

logger = logging.getLogger(__name__)



def send_gcm_message(key, reg_token, data):
    gcm = GCM(key)



    response = gcm.json_request(registration_ids=reg_token, data=data, delay_while_idle=False)

    # Successfully handled registration_ids
    if response and 'success' in response:
        for reg_id, success_id in response['success'].items():
            logger.debug("Successfully sent notification for %s",reg_id)

            # Handling errors
            if 'errors' in response:
                for error, reg_ids in response['errors'].items():
                    # Check for errors and act accordingly
                    if error in ['NotRegistered', 'InvalidRegistration']:
                                                                # Remove reg_ids from database
                        for reg_id in reg_ids:
                            logger.debug("Removing reg_id: %s from db",reg_id)
