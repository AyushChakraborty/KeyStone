#format the reqs and res according to the http format

def format_req(req_body: str, method: str, headers: dict, target: str = "/") -> str:
    """
    explaination:
        a http req is formatted as 
            <req-method> <target> <req-protocol>\r\n 
            <headers separated by \r\n>\r\n
            \r\n
            <body>\r\n
            \r\n
            
        within the body, the fields present are
            Host: IP of the server
            Content-Type: type of content sent in the body
            Content-Length: length of content in the body
    
    parameters:
        req_body: the body of the req
        method: the req method 
        target: the url-path being requested
        headers: dictionary of header fields, generally with keys Host, Content-Type, Content-Length
    
    returns: 
        http formatted req
    """
    formatted_req = f"{method} {target} HTTP/1.1\r\n"
    
    for key, val in headers.items():
        formatted_req += f"{key}: {val}\r\n"
    
    formatted_req += f"\r\n{req_body}\r\n\r\n"
    
    return formatted_req
    
    
def format_res(res_body: str, method: str, headers: dict, status_code: str, status_text: str) -> str:
    """
    explaination:
        a http res formatted as
            <res-protocol> <status-code> <status-text>\r\n
            <headers separated by \r\n>\r\n
            \r\n
            <body>\r\n
            \r\n
        
        here too, headers are comprised of response and representational headers where response headers relate to
        response's metadata and representational data relate to the reponse body's metadata
        
        parameters: 
            res_body: the response body sent by the server
            method: the reqs method in response to which this res is sent
            headers: additional information about the response
            status_code: res status code
            status_text: res status text
        
        returns:
            http formatted res
    """
    formatted_res = f"HTTP/1.1 {status_code} {status_text}\r\n"
    
    for key, val in headers.items():
            formatted_res += f"{key}: {val}\r\n"
        
    formatted_res += f"\r\n{res_body}\r\n\r\n"
        
    return formatted_res
    
    
    