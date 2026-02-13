import socket
import time 
import numpy as np

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

WINDOW_SIZE = 100


def format_packet(seq_id, payload: bytes):
    return seq_id.to_bytes(SEQ_ID_SIZE, 'big', signed=True) + payload


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
        sag_socket.settimeout(3.0)

        print("SAG Sending...")

        while base < len(mp3_bytes):
            print("Entering Loop")

            while data_index < len(mp3_bytes) and data_index < base + WINDOW_SIZE:
                # send data in packet to receiver
                payload = bytes(mp3_bytes[data_index:data_index+1])
                packet = format_packet(data_index, payload)

                print(f"Sending seq={base}, data='{payload[0]}'")
                sag_socket.sendto(packet, (UDP_IP, UDP_PORT))

                data_index += 1

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

                print(f"Delay Per Packet Time: {(dpp_timer_end - dpp_timer_start):.7f}")
                dpp_list.append(dpp_timer_end - dpp_timer_start)

                # Move window forward
                if ack_seq > base: # len(payload)
                    base = ack_seq
                    # print(f"Sending Message: {mp3_bytes[data_index]}")
                    print("Window moved forward!")

            except socket.timeout:
                print("Timeout — resending packet")

                # Resent all packets in window
                for i in range(base, data_index):
                    payload = bytes(mp3_bytes[i:i+1])
                    packet = format_packet(i, payload)
                    sag_socket.sendto(packet, (UDP_IP, UDP_PORT))
        
        throughput_timer_end = time.perf_counter()
        sag_socket.sendto(format_packet(base, b'==FINACK=='), (UDP_IP, UDP_PORT))
        print("All data sent. Closing sliding window socket.")
        sag_socket.close()
        print(f"Throughput Time: {(throughput_timer_end - throughput_timer_start):.7f}")
        dpp_avg = np.mean(dpp_list)
        print(f"Average Delay per Packet Time: {dpp_avg:.7f}")

main()