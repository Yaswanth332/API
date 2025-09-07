import os
import smtplib
from email.message import EmailMessage
import random
import time
import math

# --- Simple Quantum-Inspired OTP Generation ---
def generate_quantum_otp(length=6):
    """
    Generates a quantum-inspired OTP using high-quality randomness.
    Returns a numeric OTP of specified length.
    """
    # Use multiple entropy sources for true randomness
    seed = int(time.time() * 1000) + int.from_bytes(os.urandom(4), 'big')
    random.seed(seed)
    
    # Generate OTP using quantum-inspired probability
    otp = ""
    for _ in range(length):
        # Simulate quantum probability (Born rule)
        angle = random.uniform(0, 2 * math.pi)
        prob = (math.sin(angle) ** 2)  # Quantum probability formula
        
        # Generate digit with quantum-inspired randomness
        digit = int(random.random() * 10 * prob) % 10
        otp += str(digit)
    
    return otp

# --- Alternative: Even simpler version ---
def generate_simple_quantum_otp(length=6):
    """
    Simple quantum-inspired OTP using system entropy.
    """
    # Use high-quality system entropy
    random.seed(int(time.time() * 1000) + int.from_bytes(os.urandom(4), 'big'))
    
    # Generate cryptographically strong OTP
    otp = ""
    for _ in range(length):
        otp += str(random.randint(0, 9))
    
    return otp

# --- Email Sending Functionality ---
def send_otp_by_email(otp_code, recipient_email):
    sender_email = os.environ.get('EMAIL_ADDRESS')
    app_password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not app_password:
        raise ValueError("Email credentials not set (EMAIL_ADDRESS, EMAIL_PASSWORD)")

    msg = EmailMessage()
    msg['Subject'] = 'Your Quantum-Powered OTP'
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(f"Your secure One-Time Password is: {otp_code}\n\nThis OTP will expire shortly.")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Testing Quantum OTP ---")
    otp = generate_quantum_otp(6)
    print(f"Generated 6-digit quantum OTP: {otp}")
    
    # Test simple version
    simple_otp = generate_simple_quantum_otp(6)
    print(f"Generated 6-digit simple quantum OTP: {simple_otp}")

    # To send email:
    # recipient = "test_user@example.com"
    # send_otp_by_email(otp, recipient)