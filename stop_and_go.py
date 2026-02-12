import socket
import time 
import pandas as pd

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

# def format_int_packet(seq_id: int, payload: int) -> bytes:
#     seq_bytes = seq_id.to_bytes(SEQ_ID_SIZE, 'big', signed=True)
#     payload_bytes = payload.to_bytes(MESSAGE_SIZE, 'big', signed=False)
#     return seq_bytes + payload_bytes


def main():
    with open("docker/file.mp3", "rb") as f:
        mp3_bytes = f.read()
    
    # limiting the bytes for debugging
    # mp3_bytes = mp3_bytes[:80000]
      
    base = 0          # last acknowledged byte
    data_index = 0
    dpp_list = []
    # initialize sender's socker
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sag_socket:
        # Start Throughput Measurement Here
        throughput_timer_start = time.perf_counter()
        sag_socket.bind((SENDER_IP, SENDER_PORT))
        sag_socket.settimeout(1.0)

        print("SAG Sending...")

        while data_index < len(mp3_bytes):
            print("Entering Loop")
            # send data in packet to receiver
            payload = bytes(mp3_bytes[data_index:data_index+1])   # .encode()
            packet = format_packet(base, payload)

            print(f"Sending seq={base}, data='{payload[0]}'")
            sag_socket.sendto(packet, (UDP_IP, UDP_PORT))
            # Delay Per Packet Timer Starts Here
            dpp_timer_start = time.perf_counter()

            # receive ACK from receiver
            try:
                ack = sag_socket.recv(BUFFER_SIZE)
                ack_seq = int.from_bytes(
                    ack[:SEQ_ID_SIZE], byteorder='big', signed=True
                )
                
                # Received ACK, stop timer
                dpp_timer_end = time.perf_counter()
                print(f"ACK received: {ack_seq}")
                print(f"Delay Per Packet Time: {(dpp_timer_start - dpp_timer_end):.4f}")
                dpp_list.append(dpp_timer_start - dpp_timer_end)

                # Store new last ack
                if ack_seq == base + 1: # len(payload)
                    base = ack_seq
                    data_index += 1
                    # print(f"Sending Message: {mp3_bytes[data_index]}")
                    print("Sent!")
                else:
                    print("Unexpected ACK, resending...")

            except socket.timeout:
                print("Timeout — resending packet")
        
        throughput_timer_end = time.perf_counter()
        sag_socket.sendto(format_packet(base, b'==FINACK=='), (UDP_IP, UDP_PORT))
        print("All data sent. Closing stop and go socket.")
        sag_socket.close()
        print(f"Throughput Time: {(throughput_timer_start - throughput_timer_end):.4f}")
        dpp_avg = pd.mean(dpp_list)
        print(f"Average Delay per Packet Time: {dpp_avg}")
