#functions to parse the req and res

def parse(req: str):
    elements = req.split("\r\n")
    
    return elements