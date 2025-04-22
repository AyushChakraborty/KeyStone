#function to get the extension

def get_mime(target: str) -> str:
    if ".txt" in target:
        return "text/plain"
    elif ".json" in target:
        return "text/json"
    elif ".html" in target:
        return "text/html"
    return "default"