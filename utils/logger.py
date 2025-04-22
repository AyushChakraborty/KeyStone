#logs the reqs and res

def log(req: str, res: str, req_time: str, res_time: str):
    with open("logs.log", "a") as f:
        f.write(f"[{req_time}] REQUEST: {req}\n")
        f.write(f"[{res_time}] RESPONSE: {res}\n")
        f.write("----------------------------------\n")
    