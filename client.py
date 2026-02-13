import stop_and_go
import fixed_slide_win_pro
import tcp_reno
import sys

command = ""
if len(sys.argv) == 2:
    command = sys.argv[1]

STOP_AND_GO = False
FIXED_SLIDE_WIN_PRO = True
TCP_RENO = False

if len(sys.argv) > 2:
    print("Too many arguments")
    print("Please Input: python3 client.py [stop_and_go | fixed_slie_win | tcp_reno]")

if command != "" and len(sys.argv) == 2:
    if command == "stop_and_go":
        STOP_AND_GO = True
        FIXED_SLIDE_WIN_PRO = False
        TCP_RENO = False
    elif command == "fixed_slide_win":
        FIXED_SLIDE_WIN_PRO = True
        STOP_AND_GO = False
        TCP_RENO = False
    elif command == "tcp_reno":
        TCP_RENO = True
        STOP_AND_GO = False
        FIXED_SLIDE_WIN_PRO = False
    else:
        print("Argument Mistake")
        print("Running hard-coded protocol...")
        
if len(sys.argv) < 2:
    print("No Protocol Command Input")
    print("If you want to use command line arguments")
    print("Please Input: python3 client.py [stop_and_go | fixed_slie_win | tcp_reno]")
    
    
def main():
    
    print("Starting Client...")
    if STOP_AND_GO:
        print("Intiating Stop and Go ARQ")
        stop_and_go.main()
    if FIXED_SLIDE_WIN_PRO:
        print("Initiating Fixed Slide Window Protocol...")
        fixed_slide_win_pro.main()
    if TCP_RENO:
        print("TCP RENO not implemented yet :(")
        sender = tcp_reno.TCP_Reno()
        sender.Run()
    if (TCP_RENO == False and STOP_AND_GO == False
        and FIXED_SLIDE_WIN_PRO == False):
        print("No Protocol Boolean Constants Have Been Set to True")

main()