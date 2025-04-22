#a simple lexer to identify plain text vs json vs html

import json

def detect_type(content: str) -> str:
    content = content.strip().lower()  #lower needed as some parts of html code are case insensitive

    if content.startswith("<!doctype html>") or content.startswith("<html") and content.endswith("</html>"):
        return "text/html"
    elif (content.startswith("{") and content.endswith("}")) or (content.startswith("[") and content.endswith("]")):
        try:
            json.loads(content)    #if its able to parse the content fully then its surely json
            return "text/json"
        except:
            return "text/plain"    #else not
    else:
        return "text/plain"