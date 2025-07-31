from truck_status import TruckStatus

class Truck:
    def __init__(self, truck_ID, departure_time):
        self.MPH = 18
        self.mileage = 0
        self.assigned_packages = None
        self.delivery_order = []
        self.departure_time = None
        self.status = TruckStatus.AT_HUB
        self.return_time = None
        self.truck_ID = truck_ID
        self.departure_time = departure_time

