# from datetime import datetime
# from pydantic import BaseModel

# class RouteCreate(BaseModel):
#     routeNumber: str
#     creationDate: str
#     creationDate: float
# class TruckUpdate(BaseModel):
#     nombreTruck: str | None = None
#     creationDate: str | None = None
#     creationDate: float | None = None


def route_helper(route) -> dict:
    return {
        "id": str(route["_id"]),
        "routeNumber": route["routeNumber"],
        "creationDate": route["creationDate"]
    }
