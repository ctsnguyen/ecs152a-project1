import socket
from pydub import AudioSegment 

SENDER_IP = "127.0.0.1"
SENDER_PORT = 6767

UDP_IP = "127.0.0.1"
UDP_PORT = 5001

BUFFER_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = BUFFER_SIZE - SEQ_ID_SIZE

TEST_DATA = [
    "Hello World",
    "John Pork",
    "Beyond Ultra Smash this project pls",
    "Government Secrets",
    "Cyberpunk Edgerunners",
    "Open the Blackwall",
    "john",
    "==FINACK=="
]


DATA = []

def format_packet(seq_id, payload: bytes):
    return seq_id.to_bytes(SEQ_ID_SIZE, 'big', signed=True) + payload

def format_int_packet(seq_id, payload: bytes)

def main():
    with open("docker/file.mp3", "rb") as f:
        mp3_bytes = f.read()
        mp3_size = len(mp3_bytes)\
        
    for i in range(mp3_size):
        DATA.append(mp3_bytes[i])
    
    

    
    base = 0          # last acknowledged byte
    data_index = 0

    # initialize sender's socker
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sag_socket:
        sag_socket.bind((SENDER_IP, SENDER_PORT))
        sag_socket.settimeout(1.0)

        print("SAG Sending...")

        while data_index < len(DATA):
            # send data in packet to receiver
            payload = DATA[data_index].encode()
            packet = format_packet(base, payload)

            print(f"Sending seq={base}, data='{DATA[data_index]}'")
            sag_socket.sendto(packet, (UDP_IP, UDP_PORT))

            # receive ACK from receiver
            try:
                ack = sag_socket.recv(BUFFER_SIZE)
                ack_seq = int.from_bytes(
                    ack[:SEQ_ID_SIZE], byteorder='big', signed=True
                )

                print(f"ACK received: {ack_seq}")

                # Store new last ack
                if ack_seq == base + len(payload):
                    base = ack_seq
                    data_index += 1
                else:
                    print("Unexpected ACK, resending...")

            except socket.timeout:
                print("Timeout — resending packet")

        print("All data sent. Closing stop and go socket.")
        sag_socket.close()
