import requests 
import hashlib  
import logging   
from datetime import datetime
from typing import Dict, Any

PAYMENT_API_URL = "https://api.external-gateway.com/process_payment"
API_KEY = "your_secret_key" 
logging.basicConfig(filename='payments.log', level=logging.INFO)

# Helper: Validate inputs
def validate_payment_inputs(user_id: str, amount: float, currency: str, method: str, token: str) -> bool:
    if not all([user_id, amount > 0, currency in ['USD', 'EUR'], method in ['card', 'bank'], token]):
        return False
    if len(token) < 10:
        return False
    return True

# Helper: Hash sensitive data for compliance
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:16]

# Core: Process payment
def process_payment(user_id: str, amount: float, currency: str = 'USD', method: str = 'card', token: str = '') -> Dict[str, Any]:
    if not validate_payment_inputs(user_id, amount, currency, method, token):
        return {'status': 'failed', 'message': 'Invalid inputs', 'transaction_id': None}
    
    hashed_token = hash_token(token)
    payload = {
        'user_id': user_id,
        'amount': amount,
        'currency': currency,
        'method': method,
        'token': hashed_token 
    }
    
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    try:
        response = requests.post(PAYMENT_API_URL, json=payload, headers=headers, timeout=30)
        result = response.json() if response.ok else {'status': 'failed', 'message': response.text}
    except Exception as e:
        result = {'status': 'failed', 'message': str(e)}
        logging.error(f"API error for user {user_id}: {e}")
    
    log_entry = f"{datetime.now()}: User {user_id} | Amount {amount} {currency} | Status {result['status']}"
    logging.info(log_entry)
    
    return result

def check_risk(user_id: str, amount: float) -> bool:
    recent_total = get_recent_total(user_id)
    if recent_total + amount > 1000:
        logging.warning(f"Risk alert: High velocity for {user_id}")
        return False
    return True

def get_recent_total(user_id: str) -> float:
    # Placeholder: In real, query payments DB with time filter
    return 0.0  # Mock

def initiate_payment(user_id: str, amount: float, currency: str, method: str, token: str) -> Dict[str, Any]:
    if not check_risk(user_id, amount):
        return {'status': 'failed', 'message': 'Risk check failed', 'transaction_id': None}
    
    result = process_payment(user_id, amount, currency, method, token)
    
    if result['status'] == 'success':
        update_user_balance(user_id, -amount)
        logging.info(f"Payment succeeded for {user_id}")
    else:
        logging.error(f"Payment failed for {user_id}: {result['message']}")
    
    return result

def update_user_balance(user_id: str, delta: float):
    # Placeholder: DB update
    pass

if __name__ == "__main__":
    outcome = initiate_payment(
        user_id="user123",
        amount=50.0,
        currency="USD",
        method="card",
        token="tok_secure123abc"  # Mock tokenized card
    )
    print(outcome)  # {'status': 'success', 'transaction_id': 'txn_abc123', 'message': 'Approved'}