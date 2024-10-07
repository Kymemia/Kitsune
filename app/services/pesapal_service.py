#!/usr/bin/env python3

"""
this will be the pesapal servicet hat will handle Mpesa
&& Visa payment integration using the Pesapal API
"""
import os
import requests
import subprocess
import logging


subprocess.run(['bash', '-c', 'source ~/.scripts/bash_scripts/pesapal.sh'], shell=True)

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')

"""
configuring the logging aspect of the integration
    *asctime -> shows the time the message was generated
    *levelname -> shows level of log message.
                    could be error, debug, or info
    *message -> shows the log message
"""
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PesaPalService:
    """
    this is the class definition containing
    all the relevant methods && attributes
    """
    def __init__(self):
        self.access_token = self.get_access_token()

    def get_access_token(self) -> str:
        """
        method definition that fetches
        the OAuth access token from Pesapal
        """
        url = "https://www.pesapal.com/API/OAuth/Token"
        credentials = {
                'consumer_key': CONSUMER_KEY,
                'consumer_secret': CONSUMER_SECRET  
                }

        try:
            response = requests.post(url, data=credentials)
            response.raise_for_status()
            token_data = response.json()
            return token_data['access_token']

        except requests.RequestException as e:
            logging.error(f"Error retrieving access token: {e}")
            raise e

    def initiate_payment(self, order_data: dict) -> dict:
        """
        method definition that initials a payment
        """
        url = "https://www.pesapal.com/API/PostPesapalDirectOrderv4"
        headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
                }

        try:
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Error initiating payment: {e}")
            raise e

    def check_transaction_status(self, transaction_id: str) -> dict:
            """
            method definition to check the status of a transaction
            """
            url = f"https://www.pesapal.com/API/CheckTransactionStatus/{transaction_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
                }

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                logging.error(f"Error checking transaction status: {e}")
                raise e

    def confirm_payment(self, transaction_id) -> str:
        """
        method definition to confirm whether a payment went through
        """
        url = f"https://www.pesapal.com/API/ConfirmPayment/{transaction_id}"
        headers = {
                'Authorization': f'Bearer {self.access_token}'
                }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logging.error(f"Error confirming payment: {e}")
            raise e

    def process_refund(self, payment_id: str, amount: float, reason: str) -> dict:
        """
        method definition to process a refund
        """
        url = "https://www.pesapal.com/API/RefundPayment"
        headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
                }
        data = {
                'payment_id': payment_id,
                'amount': amount,
                'reason': reason
                }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Error processing refund for payment {payment_id}: {e}")
            raise e
