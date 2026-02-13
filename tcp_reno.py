import socket
import time

class TCP_Reno:
    BUFFER_SIZE = 1024
    SEQ_ID_SIZE = 4

    def __init__(self, sender_ip="127.0.0.1", sender_port=6767, 
                receiver_ip="127.0.0.1", receiver_port=5001, 
                file_loc="docker/file.mp3", init_cwnd=1,
                init_ssthresh=64, timeout_set=1):
        
        # Networking
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.timeout_set = timeout_set

        # Data
        self.file_loc = file_loc
        self.data = self.RetrieveData(file_loc)

        # Reno state
        self.base = 0
        self.next_seq = 0
        self.data_index = 0
        self.state = "Slow Start"

        self.cwnd = init_cwnd
        self.ssthresh = init_ssthresh

        # Duplicate ACK tracking
        self.last_ack = -1
        self.dup_ack_count = 0

        # Socket 
        self.sock = None

    def FormatPacket(self, seq_id : int, payload: bytes) -> bytes:
        return seq_id.to_bytes(self.SEQ_ID_SIZE, 'big', signed=True) + payload

    def RetrieveData(self, file : str) -> list:
        with open(file, "rb") as f:
            mp3_bytes = f.read()
        return mp3_bytes
    
    def SendData(self) -> None:
        payload = self.data[self.next_seq:self.next_seq+1]   # .encode()
        packet = self.FormatPacket(self.base, payload)
        if not payload:
            return
        print(f"Sending seq={self.base}, data='{payload[0]}'")
        self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))
        self.next_seq += 1

        return 

    def RecvAck(self) -> tuple[int, int]:
        
        ack = self.sock.recv(self.BUFFER_SIZE)
        ack_seq = int.from_bytes(
            ack[:self.SEQ_ID_SIZE], byteorder='big', signed=True
        )
    
        last_recv_ack = -1
        # if ack_seq received
        # Might need to add some logic for cwnd?
        if ack_seq == self.base + 1:     
            # Sequence and Data
            self.base = ack_seq
            self.data_index += 1
            print(f"Recived ACK {ack_seq}")
                
            # cwnd incrementation
            self.cwnd += 1
            in_flight -= 1

            # count for duplicate acks

            
        else:
            print(f"Expected ACK: {self.base + 1}, Received ACK: {ack_seq}, Resending...")
        
        return ack_seq
    
    def SlowStart(self) -> str:
        # Gradually Increase cwnd until timeout
        self.last_ack = -1
        self.duplicate_acks = 0
        while self.cwnd < self.ssthresh:  # Negation of cwnd >= ssthresh cool right
            while (self.next_seq - self.base) < int(self.cwnd) and self.data_index != len(self.data):
                self.SendData()
                
            
            try: 
                cur_ack = self.RecvAck(self.cwnd)     
                
                if cur_ack == self.last_ack:
                    self.duplicate_acks += 1
                self.last_ack = cur_ack

                if self.duplicate_acks == 3:
                    self.ssthresh // 2
                    self.cwnd = self.ssthresh + 3 # Plus 3 ACKS
                    return "Recovery"

            except socket.timeout:
                # FastRetransmit() 
                self.ssthresh = self.cwnd / 2
                self.cwnd = 1
                # in_flight = 0
                return "Slow Start" # FastRetransmit() Can happen here?
            
        # Exit Slow Start and go to AIMD
        return "AIMD" # Can be here too
    
    def AIMD(self) -> str:
        # this is the Congestion Control
        # Increase Constant = 1, Decrease Constant = 2
        # On arrival of every ACK, increment the cwnd by (1 / cwnd)
        # and send new segment in the network

        # We know how much packets are in flight based on:
        # in_flight = self.next_seq - self.base

        while (self.next_seq - self.base) < self.cwnd:            
            # Increase sending rate by a constant
            # Decrease sending rate by a linear factor
            self.SendData()
            self.cwnd += 1

            try: 
                cur_ack, in_flight = self.RecvAck(self.cwnd, in_flight)     
                
                if cur_ack == self.last_ack:
                    self.duplicate_acks += 1
                self.last_ack = cur_ack

                if self.duplicate_acks == 3:
                    self.ssthresh // 2
                    self.cwnd = self.ssthresh + 3 # Plus 3 ACKS
                    return "Recovery"
                 
            except socket.timeout:
                # FastRetransmit() 
                self.ssthresh = self.cwnd / 2
                self.cwnd = 1
                # in_flight = 0
                return "Slow Start"
            
        return ""

    def FastRetransmit(self) -> str:
        # Get 3 Duplicate ACKs to Indicate Loss
        
        pass

    def FastRecovery(self) -> str:
        # If acks coming through no need for slow start
        # Increment cwnd by 1 for each ACK
        pass

    def Run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            self.sock = s
            self.sock.bind((self.sender_ip, self.sender_port))
            self.sock.settimeout(self.timeout_set)

            valid_states = {"Slow Start", "AIMD", "Recovery", "Retransmit"}

            while self.state in valid_states and self.data_index < len(self.data):
                if self.state == "Slow Start":
                    self.state = self.SlowStart()
                elif self.state == "AIMD":
                    self.state = self.AIMD()
                elif self.state == "Recovery":
                    self.state = self.FastRecovery()
                elif self.state == "Retransmit":
                    self.state = self.FastRetransmit()
                else:
                    break

            
            fin_payload = b"==FINACK=="
            self.sock.sendto(self.FormatPacket(self.base, fin_payload), 
                             (self.receiver_ip, self.receiver_port))
            self.sock.close()


if __name__ == "__main__":
    sender = TCP_Reno()
    sender.Run()