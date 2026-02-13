import socket
import time

# Macros

# Sender Locations
SENDER_IP = "127.0.0.1"
SENDER_PORT = 6767

# Receiver location
RECEIVER_IP = "127.0.0.1"
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

BASE = 0
DATA_INDEX = 0
THREE_DUPLICATE_ACKS = False

# State Machine
STATE = "Slow Start"  # Initial state is Slow Start

def SendData(s : socket) -> None:
    payload = bytes(DATA[DATA_INDEX:DATA_INDEX+1])   # .encode()
    packet = FormatPacket(BASE, payload)

    print(f"Sending seq={BASE}, data='{payload[0]}'")
    s.sendto(packet, (RECEIVER_IP, RECEIVER_PORT))
    
    return 

def RecvAck(cwnd : int, in_flight, s : socket):
    ack = s.recv(BUFFER_SIZE)
    ack_seq = int.from_bytes(
        ack[:SEQ_ID_SIZE], byteorder='big', signed=True
    )
    duplicate_acks = 0
    last_recv_ack = -1
    # if ack_seq received
    # Might need to add some logic for cwnd?
    if ack_seq == BASE + 1:     
        # Sequence and Data
        BASE = ack_seq
        DATA_INDEX += 1
        print(f"Recived ACK {ack_seq}")
            
        # cwnd incrementation
        cwnd += 1
        in_flight -= 1

        # count for duplicate acks

        
    else:
        print(f"Expected ACK: {BASE + 1}, Received ACK: {ack_seq}, Resending...")
    
    return [cwnd, in_flight, ack_seq]


def SlowStart(cwnd : int, ssthresh : int, s : socket) -> str:
    # Gradually Increase cwnd until timeout
    in_flight = 0   
    last_ack = -1

    while cwnd < ssthresh:  # Negation of cwnd >= ssthresh cool right
        while in_flight < cwnd and DATA_INDEX != len(DATA):
            SendData(s)
            in_flight += 1
        try: 
            cwnd, in_flight, cur_ack = RecvAck(cwnd, in_flight, s)     
            if cur_ack == last_ack:
                THREE_DUPLICATE_ACKS += 1
            last_ack = cur_ack

            if THREE_DUPLICATE_ACKS == 3:
                ssthresh / 2
                cwnd = ssthresh + 3 # Plus 3 ACKS
                return "Recovery"

        except socket.timeout:
            # FastRetransmit() 
            ssthresh = cwnd / 2
            cwnd = 1
            in_flight = 0
            return "SlowStart()" # FastRetransmit() Can happen here?
        
    # Exit Slow Start and go to AIMD
    return "AIMD" # Can be here too

def AIMD(cwnd : int, ssthresh : int):
    # this is the Congestion Control
    # Increase Constant = 1, Decrease Constant = 2
    
    # On arrival of every ACK, increment the cwnd by (1 / cwnd)
    # and send new segment in the network

    # Increase sending rate by a constant
    # Decrease sending rate by a linear factor


    pass

def FastRetransmit():
    # Get 3 Duplicate ACKs to Indicate Loss
    
    pass

def FastRecovery():
    # If acks coming through no need for slow start
    # Increment cwnd by 1 for each ACK
    pass

def FormatPacket(seq_id, payload: bytes):
    return seq_id.to_bytes(SEQ_ID_SIZE, 'big', signed=True) + payload

def RetrieveData(file : str) -> list:
    with open(file, "rb") as f:
        mp3_bytes = f.read()
    return mp3_bytes

DATA = RetrieveData(FILE_LOC)

def main():
    # Let's get that data
    RetrieveData(FILE_LOC)

    # Reminder: Turn this in TCP!!
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tr_socket:
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
                STATE = SlowStart(int_cwnd, init_ssthresh, tr_socket) 
            elif STATE == "AIMD":
                STATE = AIMD()
            elif STATE == "Recovery":
                STATE = FastRecovery()
            elif STATE == "Retransmit":
                STATE = FastRetransmit()
            else:
                break
        
        tr_socket.sendto(FormatPacket(BASE, '==FINACK=='), (RECEIVER_IP, RECEIVER_PORT))
        tr_socket.close()
            
main()