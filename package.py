from status import Status


class Package:
    def __init__(self, package_ID, address, city, zip, deadline, weight, specific_truck, delayed_arrival,
                 correct_address, correct_city, correct_zip, must_be_with, status):
        self.package_ID = package_ID
        self.address = address
        self.city = city
        self.zip = zip
        self.deadline = deadline
        self.weight = weight
        self.specific_truck = specific_truck
        self.delayed_arrival = delayed_arrival
        self.correct_address = correct_address
        self.correct_city = correct_city
        self.correct_zip = correct_zip
        self.must_be_with = must_be_with
        self.status = status

    def __str__(self):
        return str(vars(self))


