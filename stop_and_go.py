import socket

RECEIVER_PORT = 67
SENDER_PORT = 6767
UDP_IP = "0.0.0.0"
UDP_PORT = 5001

def WaitForAck():
    pass

def SendData():
    pass

def SetTimer(timeout : int) -> None :
    """
    Set a Integer Timer and wait for an incoming acknowledgement (ACK)
    
    :param timeout: Timeout in seconds
    :type timeout: int
    
    """
    while (timeout != 0):
        WaitForAck()

def main():

    ID = 0 # Integer Iterable
    data = ["Hello World", "John Pork", "Beyond Ultra Smash this project pls"] # Data Stream
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as sag_socket:
        sag_socket.bind(address=("0.0.0.0", SENDER_PORT))        

        print("SAG Sending...")

       
        while ID < len(data):
            # Create & Enconde Message
            message = data[ID] # Encoded data-string into bits 
            encoded_message = message.encode()

            # Send to Server
            sag_socket.sendto(encoded_message, (UDP_IP, UDP_PORT))
            print(f"Message: {message} sent at {UDP_IP}:{UDP_PORT}")


