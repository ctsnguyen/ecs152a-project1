import socket

SENDER_IP = "127.0.0.1"  # Local Host
SENDER_PORT = 6767

UDP_IP = "0.0.0.0"
UDP_PORT = 5001
BUFFER_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = BUFFER_SIZE - SEQ_ID_SIZE
DATA = ["Hello World", "John Pork", "Beyond Ultra Smash this project pls",
        "Government Secrets", "Cyberpunk Edgerunners", "Open the Blackwall"]  # Data Stream



def main():
    expected_seq_id = 0

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as sag_socket:
        
        sag_socket.bind((SENDER_IP, SENDER_PORT))  
        sag_socket.settimeout(1.0) 
        print("SAG Sending...")

        while expected_seq_id < len(DATA):  
            time_out = 0
            try:
                # Create & Enconde Message
                message_sent = DATA[expected_seq_id] # Encoded data-string into bits 
                encoded_message = message_sent.encode()

                # Send Data to Server
                if sag_socket.sendto(encoded_message, (UDP_IP, UDP_PORT)):
                    print(f"Message: {message_sent} sent at {UDP_IP}:{UDP_PORT}")

                # Receive Message
                ack = sag_socket.recv(BUFFER_SIZE)
                seq_id, message_recv = ack[:SEQ_ID_SIZE], ack[SEQ_ID_SIZE:]

                # Decode seq_id
                # if the message id is -1, we have received all the packets
                seq_id = int.from_bytes(seq_id, signed=True, byteorder='big')


                # Check Sequence ID
                # if seq_id_decoded == DATA[expected_seq_id] and len(message_recv[seq_id]) > 0:
                #     while expected_seq_id in DATA:
                #         expected_seq_id += len(DATA[seq_id])

                # Check Sequence ID v2
                if seq_id == expected_seq_id and message_recv:
                    print(f"Acquired Sequence ID: {seq_id}")
                    print(f"Expected Sequence ID: {expected_seq_id}")
                    expected_seq_id += 1
                else:
                    print(f"Ignoring ACK Sequence ID: {seq_id}")
                    print(f"Expected Sequence ID: {expected_seq_id}")
                    print(f"Message Received {message_recv}")

            except socket.timeout:
                time_out += 1
                print(f"Currently in {time_out}")



