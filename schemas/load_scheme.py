
def load_helper(load) -> dict:
    return {
        "id": str(load["_id"]),
        "firstStopTime": load["firstStopTime"],
        "route": load["route"],
        "lastStopTime": load["lastStopTime"],
        "landFillTimeIn": load["landFillTimeIn"],
        "landFillTimeOut": load["landFillTimeOut"],
        "grossWeight": load["grossWeight"],
        "tareWeight": load["tareWeight"],
        "tons": load["tons"],
        "landFill": load["landFill"],
        "ticketNumber": load["ticketNumber"],
        "note": load["note"],
        "image": load["image"]  
    }