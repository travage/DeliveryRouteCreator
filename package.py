from status import Status


class Package:
    def __init__(self, packageID, address, city, zip, deadline, weight):
        self.packageID = packageID
        self.address = address
        self.city = city
        self.zip = zip
        self.deadline = deadline
        self.weight = weight
        self.status = Status.AT_HUB


