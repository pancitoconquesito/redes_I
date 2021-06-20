import socket

HOST ='0.0.0.0'
PORT=2207
IPV=socket.AF_INET
TCP=socket.SOCK_STREAM

with socket.socket(IPV,TCP) as soc:
    soc.bind((HOST,PORT))
    print("Servidor coreindo en ",HOST,PORT)
    while True:
        soc.listen()
        conn,addr = soc.accept()
        with conn:
            rec = conn.recv(1042).decode()
            print(addr," dice: ",rec)
            conn.close()