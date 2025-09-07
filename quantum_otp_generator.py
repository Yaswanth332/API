import os
import smtplib
from email.message import EmailMessage
from adaptive_qrng import adaptive_rotation_qrng  # import the advanced QRNG

# --- Quantum OTP Generation using adaptive QRNG ---
def generate_quantum_otp(length=6):
    """
    Generates a quantum-based OTP using adaptive-rotation QRNG.
    Returns a numeric OTP of specified length.
    """
    # Generate enough random bits to cover the OTP
    seq_length = length * 4  # 4 bits per decimal digit is safe
    history, sequences, probs = adaptive_rotation_qrng(
        n_qubits=5,        # number of qubits
        shots=2048,
        iterations=8,
        warmup=2,
        init_theta=3.1415/2,
        lr=0.5,
        seq_length=seq_length,
        num_seqs=1,        # only need 1 sequence
        tolerance=0.01
    )

    # Convert the first sequence of bits into an integer OTP
    bitstring = sequences[0]
    otp_integer = int(bitstring, 2) % (10 ** length)
    otp_string = f"{otp_integer:0{length}d}"

    return otp_string


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
    print("--- Testing Adaptive Quantum OTP ---")
    otp = generate_quantum_otp(6)
    print(f"Generated 6-digit quantum OTP: {otp}")

    # To send email:
    # recipient = "test_user@example.com"
    # send_otp_by_email(otp, recipient)