import socket
import os
import datetime
import threading
from protocol import formatter, constants, parser, mime
from utils import logger

servable_dir = os.path.abspath(os.path.join(".", "servableFiles"))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    #if the server crashes, the next time
#the same port can be used, instead of letting it be unusable due to the socket being in TIME_WAIT
server_socket.bind(("0.0.0.0", 6780)) 

server_socket.listen(5)        #can take up to 5 connection reqs at a time in the queue

#get the actual IP address of the machine
try:
    #this doesn't need to be a real reachable address
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(("8.8.8.8", 80))  #connect to a dummy external IP
    local_ip = temp_sock.getsockname()[0]
    temp_sock.close()
except Exception:
    local_ip = "127.0.0.1"

print(f"SERVER UP: listening on {local_ip}:6780")


def handle_client(client_socket: str, address: str):
    print(f"connection from address: {address}")
    #since the data comes in chuncks, we receieve them in chuncks too
    data = b""   
    
    #the point of this loop is to only get the header info, then with the len of body obtained only 
    #read those many bytes after 
    while True:
        chunk = client_socket.recv(512)
        if not chunk:
            break     
        data += chunk
        if b"\r\n\r\n" in data:  #stops after the headers
            break 
            
    header_data, rest = data.split(b"\r\n\r\n", 1)
    
    header_elements = parser.parse(header_data.decode())     #parsing of the header done
    
    header_ele_len = len(header_elements)
    
    full_req = ""
    req_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if header_ele_len > 2:        #in this case it has a body so its valid case of POST
        print("within post case")
        body_len = header_elements[3][len("Content-Length: ")]
        if body_len != "":
            body_len = int(body_len)
        else:
            body_len = 0
        
        #now read the body
        remaining = body_len - len(rest)
        body_data = rest         #rest being the part of the body partly read
        
        while remaining > 0:
            body_chunk = client_socket.recv(min(512, remaining))
            if not body_chunk:
                break
            body_data += body_chunk
            remaining -= len(body_chunk)
        
        #this approach even works when the req is small enough that even the body fits in it since remaining would be 0

        print(f"\nREQUEST: \n{data.decode()}")
        #print(f"{data.decode()}")  #decode is used to convert from bytes to string here 
        
        full_req = data.decode()   #needed for logging
        req_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        #handling post here
        start_line = header_elements[0]
        method, target, version = start_line.split(" ")
        target_name = target[1:]
        content_type = mime.get_mime(target_name)
        res = ""
        status_code = ""
        status_text = ""

        #in case of post, the target tells where the post req shld go, so we start defining 
        #endpoints here, essentially if the target is a certain name, the server handles
        #it differently, so

        #/save endpoint, to save the contents of the POST body to a file
        if target_name == "save":
            file_path = os.path.join(servable_dir, "posted_info.txt")
            try:
                with open(file_path, "a") as f:
                    f.write(body_data.decode())
                    f.write(f"written at: {str(datetime.datetime.now())}\n")
                    f.write("--------------------------\n")          
                res = "data written successfully to /servableFiles/posted_info.txt"
                status_code = "201"
                status_text = "Created"
            except FileNotFoundError:
                print(f"ERROR: file to be written to not found: {file_path}")
                res = f"File not found"
                status_code = "404"
                status_text = "Not Found"
            except Exception as e:
                print(f"ERROR: {e}")
                res = f"File not found"
                status_code = "404"
                status_text = "Not Found"
            

    else:
        print(f"\nREQUEST: \n{header_data.decode()}")   #get case when no body is present
        start_line = header_elements[0]
        
        full_req = header_data.decode()   #needed for logging
        
        method, target, version = start_line.split(" ")
        #case when the req is GET

        #first functionality, if its /something.txt, search in the local root dir, return its contents
        target_name = target[1:]
        content_type = mime.get_mime(target_name)    #get the mime type of the file to get
        res = ""
        status_code = ""
        status_text = ""

        #handle endpoints
    
        if target_name == "":     #no target endpoint given
            res = "welcome to the server traveller!"
            status_code = "200"
            status_text = "OK"
        else:
            file_path = os.path.join(servable_dir, target_name)
            if content_type == "text/plain" or content_type == "text/json" or content_type == "text/html":
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r") as f:
                            if os.stat(file_path).st_size != 0:
                                res = f.read()
                                status_code = "200"
                                status_text = "OK"
                            else:
                                print(f"ERROR: file is empty {file_path}")
                                res = f"File is empty"
                                status_code = "204"
                                status_text = "No Context"
                    except FileNotFoundError:
                        print(f"ERROR: file to be read not found: {file_path}")
                        res = f"File not found"
                        status_code = "404"
                        status_text = "Not Found"
                    except Exception as e:
                        print(f"ERROR: {e}") 
                        res = f"File not found"
                        status_code = "404"
                        status_text = "Not Found"
                else:
                    print(f"ERROR: file to be read not found: {file_path}")
                    res = f"File not found"
                    status_code = "404"
                    status_text = "Not Found"
            else:                                           #type of the data sent to the client
                res = f"Type cannot be handled"
                status_code = "404"
                status_text = "Not Found"
            
        #/delete endpoint
        if target_name == "delete":
            file_path = os.path.join(servable_dir, "posted_info.txt")
            try:
                with open(file_path, "w") as f:
                    if os.stat(file_path).st_size == 0:
                        print(f"ERROR: file is already empty {file_path}")
                        res = f"File already empty"
                        status_code = "404"
                        status_text = "Not Found"
                    else:
                        f.truncate(0)
                        res = "all records deleted successfully"
                        status_code = "200"
                        status_text = "OK"
            except FileNotFoundError:
                print(f"ERROR: file to be deleted to not found {file_path}")
                res = f"File not found"
                status_code = "404"
                status_text = "Not Found"
            except Exception as e:
                print(f"ERROR: {e}") 
                res = f"File not found"
                status_code = "404"
                status_text = "Not Found"
        
        #/echo endpoint
        elif target_name == "echo":
            file_path = os.path.join(servable_dir, "posted_info.txt")
            try:
                with open(file_path, "r") as f:
                    if os.stat(file_path).st_size == 0:
                        print(f"file is empty: {file_path}")
                        res = f"File is empty"
                        status_code = "204"
                        status_text = "No Context"
                    else:
                        res = f.read()
                        status_code = "200"
                        status_text = "OK"
            except FileNotFoundError:
                print(f"ERROR: file to be deleted to not found {file_path}")
                res = f"File not found"
                status_code = "404"
                status_text = "Not Found"
            except Exception as e:
                print(f"ERROR: {e}") 
                res = f"File not found"
                status_code = "404"
                status_text = "Not Found"

    date = str(datetime.datetime.now())

    headers = {"Server": constants.SERVER_NAME, "Date": date, "Content-Type": content_type}
    
    formatted_res = formatter.format_res(res, method, headers, status_code, status_text)
    
    #not chunkating the response for now
    client_socket.sendall(formatted_res.encode())      #sending a response to the client socket 
    client_socket.close()                              #closing this client socket in the server side 
    
    res_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #logging
    logger.log(full_req, formatted_res, req_time, res_time) 


def main():
    try:
        while True:
            (client_socket, address) = server_socket.accept()
            #address contains clientIP and client port 
            
            threading.Thread(target=handle_client, args=(client_socket, address)).start()
    except KeyboardInterrupt:
        print("\nshutting down the server gracefully...Bye from Keystone!\n")
        server_socket.close()

    

if __name__ == "__main__":
    main()