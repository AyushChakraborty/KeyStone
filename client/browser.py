#a simple browser to send multiple reqs to the server,opens and manages multiple client sockets

from .http_client import client
from protocol import lexer
import re

def browser(sent_option: str):
    valid = 0         #only if valid is 1, will client() be called
    option = ""
    print("WELCOME TO THE KEYSTONE BROWSER")
    print('''
    ___   _  _______  __   __  _______  _______  _______  __    _  _______ 
    |   | | ||       ||  | |  ||       ||       ||       ||  |  | ||       |
    |   |_| ||    ___||  |_|  ||  _____||_     _||   _   ||   |_| ||    ___|
    |      _||   |___ |       || |_____   |   |  |  | |  ||       ||   |___ 
    |     |_ |    ___||_     _||_____  |  |   |  |  |_|  ||  _    ||    ___|
    |    _  ||   |___   |   |   _____| |  |   |  |       || | |   ||   |___ 
    |___| |_||_______|  |___|  |_______|  |___|  |_______||_|  |__||_______|
    ''')
    
    #this block is just for testing, else its not really needed
    if sent_option == "":        #nothing sent as an arg to the func, again its only needed for unit tests
        option = ""
    else:
        option = sent_option
    
    while option != "exit":
        option = input("send a req to our server right here(type help or exit if not): ")
        
        if option == "exit":
            break
        elif option == "help":
            print("-------------------------------------------------------------")
            print()
            print("enter the url this way: <url with port and target> <body in case of post req>")
            print("important note: it can only handle our server reqs for now")
            print()
            print("-------------------------------------------------------------")
        else:
            #parse the input
            num = len(option.split(" ", 1))
            if num == 2:
                url, post_body = option.split(" ", 1)
            else:
                url = option
                post_body = ""
            
            #check if url follows the standard format
            pattern_url = r'^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)/.*$'
            pattern_ip = r'^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$'

            if re.match(pattern_url, url):
                print("valid url")
                valid = 1
            else:
                print("ERROR: invalid url, shld be of format <X.X.X.X/target> where num is any number from 0 to 255 and target is some endpoint")
                valid = 0
            
            num_1 = len(url.split("/"))
            if num_1 == 2:
                ip, target = url.split("/")
            else:
                ip = url
                target = "/"

            if re.match(pattern_ip, ip):
                print("valid ip")
                # if ip == "127.0.0.1":
                #     valid = 1
                # else:
                #     print("for now it only works on our servers!")
                #     valid = 0
                valid = 1
            else:
                print("ERROR: invalid ip, shld be of format <X.X.X.X> where num is any number from 0 to 255")
                valid = 0
                    
            if num == 2:
                #a simple parser to detect for normal text, json, html only
                mime = lexer.detect_type(post_body)
            else:
                #this is the case of a get req, which does not have any body
                mime = "default"                        #will not be used anyways
    
            target = "/" + target
            if valid == 1:
                client(ip.strip(), post_body.strip(), mime, target)
            else:
                print("enter url again")
            print()
            print("-------------------------------------------------------------")
            
if __name__ == "__main__":
    browser("")