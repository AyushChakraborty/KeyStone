import socket
from protocol import formatter, constants

def client(host: str, req_body: str, req_type: str, target: str):   
    server_down = 0 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #make the raw TCP socket, uses IPv4 and TCP
    try:
        s.connect((host, 6780))                                #connect to the server at 127.0.0.1:6780
    except ConnectionRefusedError:
        print("\n---------SERVER DOWN---------\n")
        server_down = 1
    #when .connect() is called the OS picks an available port from the epehemeral port range, uses that for the client socket
    
    body_len = str(len(req_body))
    headers = {}
    
    if req_body != "":
        headers = {"Host": host, "Content-Type": req_type, "Content-Length": body_len}
    else:
        #in case of get
        headers = {"Host": host}
    
    formatted_req = formatter.format_req(req_body, "GET", headers, target)
    formatted_req_bytes = formatted_req.encode()
    
    #sending 512B long chunks 
    for byte in range(0, len(formatted_req_bytes), constants.CHUNK_SIZE):
        if not server_down:
            s.send(formatted_req_bytes[byte: byte+constants.CHUNK_SIZE])
    
    data = s.recv(constants.CLIENT_SOCKET_BUFFER_SIZE)  #blocks and waits until it gets all the data or the server closes the connection
    #the buffer can be adjusted as needed
    print(f"\nRESPONSE: \n{data.decode()}")
    s.close()                                           #closing the client socket in client side after one exhange is done

if __name__ == "__main__":
    client("192.168.x.x", "", "default", "/")     ###### was 127.0.0.1