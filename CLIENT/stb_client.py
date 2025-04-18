import socket
import struct
import sys
import pyaes
import base64
import time
import logging
import pyarmor
import os
# Define the multicast group and port

#multicast_group = os.getenv("MULTICAST", "224.1.1.1").strip()
#port = int(os.getenv("PORT", 5000))

multicast_group = "0.0.0.0"
port = 5050
key = 'qwertyuioplkjhgd'
start_time = time.time()
total_bytes = 0


logging.basicConfig(
    level=logging.DEBUG,  # Set log level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

logger.info(f"Listening on {multicast_group} and Port {port}")
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific interface and port
sock.bind((multicast_group, port))
#logger.info("Bind succesfull")


# Create an AES cipher object with the provided key and CTR mode
def decrypt_string(key, encrypted_data):
    block_size = 16

    # Generate the same initialization vector (IV) used during encryption
    iv = pyaes.Counter(initial_value=0)

    # Create an AES cipher object with the provided key and CTR mode
    cipher = pyaes.AESModeOfOperationCTR(key.encode('utf-8'), counter=iv)

    # Decode the base64-encoded ciphertext
    ciphertext = base64.b64decode(encrypted_data)

    # Decrypt the ciphertext
    padded_plaintext = cipher.decrypt(ciphertext).decode('utf-8')

    # Remove the padding from the plaintext
    padding_length = ord(padded_plaintext[-1])
    plaintext = padded_plaintext[:-padding_length]
    #logger.info(f"Data received: {plaintext}")
    return plaintext

try:
    while True:
        # Receive and process data from the multicast stream
        data, address = sock.recvfrom(1024)
        plaintext = decrypt_string(key, data)
        if plaintext.startswith("982334"):
            logger.info(f"Received encryoted data: {data} from {address}")
            logger.info(f"Received data: {plaintext}")
            total_bytes += len(data)
            logger.info(f"Total Bytes:, {total_bytes}")
            elapsed_time = time.time() - start_time
            logger.info(f"Elapsed Time:, {elapsed_time}")
            if elapsed_time >= 30:
                # Calculate bytes per second
                bytes_per_sec = total_bytes / elapsed_time
                # Print the result
                logger.info(f"BW in Kb:, {bytes_per_sec}/1024")
                #print("BW in Kb:", bytes_per_sec/1024)
                # Reset counters and start time
                total_bytes = 0
                start_time = time.time()
            
except KeyboardInterrupt:
    # Handle Ctrl+C interruption
    end_time = time.time()
    elapsed_time = end_time - start_time
    # Calculate bytes per second
    bytes_per_sec = total_bytes / elapsed_time
    # Print the final result
    logger.info(f"BW in Kb: {bytes_per_sec}/1024")
    #print("BW in Kb:", bytes_per_sec/1024)
    #print("KeyboardInterrupt: Closing socket.")
    sock.close()
    sys.exit(0)
