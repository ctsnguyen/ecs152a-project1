import socket
import time
import numpy as np

class TCP_Reno:
    BUFFER_SIZE = 1024
    SEQ_ID_SIZE = 4

    def __init__(self, sender_ip="127.0.0.1", sender_port=6767, 
                receiver_ip="127.0.0.1", receiver_port=5001, 
                file_loc="docker/file.mp3", init_cwnd=1.0,
                init_ssthresh=64, timeout_set=1.0):
        
        # Metrics
        self.dpp_list = []
        self.throughput_timer_start = None
        
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

        # byte send limit for debugging
        # mp3_bytes = mp3_bytes[:8000]

        return mp3_bytes
    
    def SendData(self) -> None:
        payload = self.data[self.next_seq:self.next_seq+1]   # .encode()
        packet = self.FormatPacket(self.next_seq, payload)
        if not payload:
            return
        print(f"Sending seq={self.next_seq}, data='{payload[0]}'")
        self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))
        self.next_seq += 1

        return 

    def RecvAck(self) -> int:
        # Start Delay Per Packet timer
        dpp_timer_start = time.perf_counter()

        ack = self.sock.recv(self.BUFFER_SIZE)

        # Stop timer after ACK received
        dpp_timer_end = time.perf_counter()
        delay = dpp_timer_end - dpp_timer_start
        self.dpp_list.append(delay)

        ack_seq = int.from_bytes(
            ack[:self.SEQ_ID_SIZE], byteorder='big', signed=True
        )

        return ack_seq
    
    
    def SlowStart(self) -> str:
        # Gradually Increase cwnd until timeout
        # while self.cwnd < self.ssthresh:  # Negation of cwnd >= ssthresh cool right
        while (self.next_seq - self.base) < int(self.cwnd) and self.data_index != len(self.data):
            self.SendData()
                
            
        try: 
            ack_seq = self.RecvAck()

            if ack_seq > self.base:
                self.base = ack_seq
                self.data_index = self.base
                self.dup_ack_count = 0

                # Slow Start growth
                self.cwnd += 1.0

                if self.cwnd >= self.ssthresh:
                    return "AIMD"        
                return "Slow Start" 
                    
            if ack_seq == self.base:
                self.dup_ack_count += 1
                

                if self.dup_ack_count == 3:
                    # self.ssthresh // 2
                    # self.cwnd = self.ssthresh + 3 # Plus 3 ACKS
                    return "Retransmit"
            return "Slow Start"

        except socket.timeout:
            # FastRetransmit() 
            self.ssthresh = max(int(self.cwnd // 2), 2)
            self.cwnd = 1.0
            self.next_seq = self.base
            self.dup_ack_count = 0
            # in_flight = 0
            return "Slow Start" # FastRetransmit() Can happen here?
            
        # Exit Slow Start and go to AIMD
        return "AIMD" # Can be here too
    
    def AIMD(self) -> str:
        # Fill window
        while self.next_seq < self.base + int(self.cwnd) and self.next_seq < len(self.data):
            self.SendData()

        try:
            ack_seq = self.RecvAck()


            if ack_seq > self.base:
                self.base = ack_seq
                # self.data_index = self.base
                self.dup_ack_count = 0

                # AIMD additive increase
                self.cwnd += 1.0 / self.cwnd
                return "AIMD"

            # Duplicate Found
            if ack_seq == self.base:
                self.dup_ack_count += 1
                if self.dup_ack_count == 3:
                    return "Retransmit"
                return "AIMD"

            return "AIMD"

        except socket.timeout:
            self.ssthresh = max(int(self.cwnd // 2), 2)
            self.cwnd = 1.0
            self.next_seq = self.base
            self.dup_ack_count = 0
            return "Slow Start"



    def FastRetransmit(self) -> str:
        self.ssthresh = max(int(self.cwnd // 2), 2)
        self.cwnd = float(self.ssthresh + 3) # Duplicates
        self.dup_ack_count = 0

        payload = self.data[self.base:self.base+1]
        if payload:
            packet = self.FormatPacket(self.base, payload)
            print(f"Fast retransmit seq={self.base}")
            self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))

        return "Recovery"

    def FastRecovery(self) -> str:
        # In Recovery, cwnd is inflated (ssthresh + 3).
        # We stay here until we get a NEW ACK that advances base.

        try:
            ack_seq = self.RecvAck()

            if ack_seq > self.base:
                self.base = ack_seq
                self.data_index = self.base  
                self.dup_ack_count = 0

                self.cwnd = float(self.ssthresh)
                return "AIMD"

            # Duplicate Acts then go into that recovery
            elif ack_seq == self.base:
                self.dup_ack_count += 1
                self.cwnd += 1.0

                while self.next_seq < self.base + int(self.cwnd) and self.next_seq < len(self.data):
                    self.SendData()

                return "Recovery"
            
            return "Recovery"

        except socket.timeout:
            # if Timeout then Slow Start
            self.ssthresh = max(int(self.cwnd // 2), 2)
            self.cwnd = 1.0
            self.next_seq = self.base
            self.dup_ack_count = 0
            return "Slow Start"


    def Run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            self.sock = s
            self.sock.bind((self.sender_ip, self.sender_port))
            self.sock.settimeout(self.timeout_set)

            # Start Throughput Timer
            self.throughput_timer_start = time.perf_counter()

            valid_states = {"Slow Start", "AIMD", "Recovery", "Retransmit"}

            while self.state in valid_states and self.base < len(self.data):
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

            # Stop Throughput Timer
            throughput_timer_end = time.perf_counter()
            
            fin_payload = b"==FINACK=="
            self.sock.sendto(self.FormatPacket(self.base, fin_payload), 
                             (self.receiver_ip, self.receiver_port))

            print("All data sent. Closing TCP Reno socket.")

            total_time = throughput_timer_end - self.throughput_timer_start
            print(f"Throughput Time: {total_time:.7f}")

            if self.dpp_list:
                dpp_avg = np.mean(self.dpp_list)
                print(f"Average Delay per Packet Time: {dpp_avg:.7f}")

            self.sock.close()


if __name__ == "__main__":
    sender = TCP_Reno()
    sender.Run()