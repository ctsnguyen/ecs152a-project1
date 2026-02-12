import socket
import time

# Macros

# Sender Locations
SENDER_IP = "127.0.0.1"
SENDER_PORT = 6767

# Receiver location
RECEIVER_IP = "0.0.0.0"
RECEIVER_PORT = 5001

# Packets Information
BUFFER_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = BUFFER_SIZE - SEQ_ID_SIZE

# Test Strings
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

FILE_LOC = "docker/file.mp3"

# Empty List
DATA = {}
BASE = 0
DATA_INDEX = 0

# State Machine
STATE = "Slow Start"  # Initial state is Slow Start

def SendData(s : socket) -> None:
    payload = bytes(DATA[DATA_INDEX:DATA_INDEX+1])   # .encode()
    packet = FormatPacket(BASE, payload)

    print(f"Sending seq={BASE}, data='{payload[0]}'")
    s.sendto(packet, (RECEIVER_IP, RECEIVER_PORT))
    
    return 
    
def SlowStart(cwnd : int, ssthresh : int, s : socket) -> None:
    # Gradually Increase cwnd until timeout
    in_flight = 0   
    while cwnd < ssthresh:  # Negation of cwnd >= ssthresh cool right

        while in_flight < cwnd and idx != len(DATA):
            SendData(s)
            in_flight += 1

        try: 
            ack = s.recv(BUFFER_SIZE)
            ack_seq = int.from_bytes(
                ack[:SEQ_ID_SIZE], byteorder='big', signed=True
            )
            
            # if ack_seq received
            if ack_seq == BASE + 1:     
                # Sequence and Data
                BASE = ack_seq
                idx += 1
                print(f"Recived ACK {ack_seq}")
                
                # cwnd incrementation
                cwnd += 1
                in_flight -= 1
            else:
                print(f"Expected ACK: {BASE + 1}, Received ACK: {ack_seq}, Resending...")
                            
        except s.timeout:
            ssthresh = cwnd / 2
            cwnd = 1
            in_flight = 0
            STATE == "Slow Start"
            
    # Exit Slow Start and go to AIMD
    STATE == "AIMD"
    return 

def AIMD(cwnd : int, ssthresh : int):
    # this is the Congestion Control
    pass

def FastRetransmit():
    pass

def FastRecovery():
    pass

def FormatPacket(seq_id, payload: bytes):
    return seq_id.to_bytes(SEQ_ID_SIZE, 'big', signed=True) + payload

def RetrieveData(file : str) -> list:
    with open(file, "rb") as f:
        mp3_bytes = f.read()
    return mp3_bytes

def main():
    # Let's get that data
    DATA = RetrieveData(FILE_LOC)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as tr_socket:
        # For TCP Reno, set the initial window size = 1 packet 
        # and the initial slow start threshold to 64 packets.
        int_cwnd = 1
        init_ssthresh = 64
        tr_socket.bind((SENDER_IP, SENDER_PORT))
        tr_socket.settimeout(1.0)
        # print(type(tr_socket))

        # State Machine
        list_of_states = ["Slow Start", "AIMD", "Recovery", "Retransmit"]
        while STATE in list_of_states:
            # TCP Reno = Slow Start + AIMD + Fast Retransmit + Fast Recovery
            if STATE == "Slow Start":
                # Enter Slow Start
                SlowStart(int_cwnd, init_ssthresh, tr_socket) 
            if STATE == "AIMD":
                AIMD()
            if STATE == "Recovery":
                FastRecovery()
            if STATE == "Retransmit":
                FastRetransmit()
            else:
                break
        
        tr_socket.sendto(FormatPacket(BASE, '==FINACK=='), (RECEIVER_IP, RECEIVER_PORT))
        tr_socket.close()
            



main()