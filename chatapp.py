import os
import smtplib
from email.message import EmailMessage
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# --- Quantum OTP Generation ---
def generate_quantum_otp(length=6):
    # Determine the number of bits needed.
    # Each decimal digit needs about 3.32 bits. We'll get enough bits to be safe.
    num_bits = length * 4

    # 1. Create a Quantum Circuit
    circuit = QuantumCircuit(num_bits, num_bits)

    # 2. Apply Hadamard Gates
    circuit.h(range(num_bits))

    # 3. Measure the Qubits
    circuit.measure(range(num_bits), range(num_bits))

    # 4. Simulate the Circuit
    simulator = AerSimulator()
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts(circuit)

    # 5. Process the Result
    random_bitstring = list(counts.keys())[0]
    random_integer = int(random_bitstring, 2)
    otp_integer = random_integer % (10**length)
    otp_string = format(otp_integer, f'0{length}d')

    return otp_string

# --- Email Sending Functionality ---
def send_otp_by_email(otp_code, recipient_email):
    """
    Sends the generated OTP to a specified email address using Gmail's SMTP server.
    """
    # Securely get credentials from environment variables
    sender_email = os.environ.get('EMAIL_ADDRESS')
    app_password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not app_password:
        raise ValueError("Email credentials (EMAIL_ADDRESS, EMAIL_PASSWORD) are not set.")

    # Construct the email message
    msg = EmailMessage()
    msg['Subject'] = 'Your Quantum-Powered OTP'
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(f"Your secure One-Time Password is: {otp_code}\n\nThis OTP will expire shortly.")

    # Connect to Gmail's SMTP server and send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# --- Example Usage (for testing this file directly) ---
if __name__ == '__main__':
    print("--- Testing Quantum OTP Generation ---")
    quantum_otp = generate_quantum_otp(6)
    print(f"Generated 6-digit secure OTP: {quantum_otp}")

    # --- Email Test ---
    # To test, set your environment variables and uncomment the lines below.
    # print("\n--- Testing Email Functionality ---")
    # try:
    #     recipient = "test_user@example.com" # <-- REPLACE WITH A REAL EMAIL
    #     send_otp_by_email(quantum_otp, recipient)
    #     print(f"Successfully sent OTP to {recipient}")
    # except Exception as e:
    #     print(f"Failed to send email: {e}")