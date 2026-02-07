import stop_and_go
import fixed_slide_win_pro
import tcp_reno

STOP_AND_GO = True
FIXED_SLIDE_WIN_PRO = False
TCP_RENO = False

def main():
    
    print("Client is running")
    if STOP_AND_GO:
        stop_and_go.main()
    if FIXED_SLIDE_WIN_PRO:
        pass
    if TCP_RENO:
        pass

main()