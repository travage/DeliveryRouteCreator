# Student ID: 002854304
from hashtable import HashTable
from package import Package
from status import Status
import csv
from datetime import datetime, time, timedelta
import sys
from truck import Truck
import math

def main():
    # Get addresses and distances from DistanceTableCleaned.csv
    addresses = []
    distances = []  # Will become 2D-array
    with open('DistanceTableCleaned.csv', newline='', encoding='utf-8') as distances_file:
        reader = csv.reader(distances_file, skipinitialspace=True)

        # Gets addresses from headers
        first_row = next(reader)
        for i in range(1, len(first_row)):
            addresses.append(first_row[i])

        # Create 2D-array with distances
        for row in reader:
            distances.append([float(x) for x in row[1:]])

    # Dictionary that will store the row / colum index of the address in the 2D array
    index_of_address = {address: i for i, address in enumerate(addresses)}

    # Counts number of lines in CSV, which equals the number of packages
    with open('PackageFileCleaned.csv', 'r', encoding='utf-8') as f:
        line_count = sum(1 for line in f)
        # Remove 1 from count to disregard headers
        line_count -= 1

    # Hash table to store packages
    # If number of packages is above 1.1 million, hash table will run inefficiently,
    # therefore number of packages needs to be lowered
    if line_count >= 1100000:
        print('Maximum number of packages is 1.1 million, please reduce the number of packages in the CSV file and try again')
        sys.exit(1)
    else:
        packages = HashTable(line_count)


    # Read package data CSV, create package object, and add to hash table
    with open('PackageFileCleaned.csv', newline='', encoding='utf-8') as package_file:
        reader = csv.reader(package_file, skipinitialspace=True)

        # Skip headers
        next(reader)

        for row in reader:
            #Required fields
            package_ID = int(row[0])
            address = row[1]
            city = row[2]
            zip = row[3]
            deadline = datetime.strptime(row[4], '%H:%M').time()
            weight = int(row[5])

            # Optional fields
            specific_truck = row[6]
            if specific_truck.strip() != '':
                specific_truck = int(specific_truck)
            else:
                specific_truck = None

            delayed_arrival = row[7]
            if delayed_arrival.strip() != '':
                delayed_arrival = datetime.strptime(row[7], '%H:%M').time()
            else:
                delayed_arrival = None

            correct_address = row[8]
            if correct_address.strip() == '':
                correct_address = None

            correct_city = row[9]
            if correct_city.strip() == '':
                correct_city = None

            correct_zip = row[10]
            if correct_zip.strip() == '':
                correct_zip = None

            must_be_with = row[11]
            if must_be_with.strip() != '':
                must_be_with = [int(x) for x in row[11].split(';')]
            else:
                must_be_with = None

            if delayed_arrival is None:
                status = Status.AT_HUB
            else:
                status = Status.DELAYED

            package = Package(package_ID, address, city, zip, deadline, weight, specific_truck,
                              delayed_arrival, correct_address, correct_city, correct_zip,
                              must_be_with, status)

            packages.insert(package.package_ID, package)

    # Manually set up more here if more trucks are needed
    # Departure times set to align with late arrivals
    truck1 = Truck(1, time(8, 0))
    truck2 = Truck(2, time(9, 5))
    truck3 = Truck(3, time(10, 20))

    # Assign packages to trucks using their package ID
    truck1.assigned_packages = [1, 4, 13, 14, 15, 16, 19, 20, 21, 22, 29, 30, 34, 37, 39, 40]
    truck2.assigned_packages = [3, 5, 6, 11, 12, 17, 18, 23, 25, 26, 27, 31, 32, 35, 36, 38]
    truck3.assigned_packages = [2, 7, 8, 9, 10, 24, 28, 33]

    create_route(truck1, index_of_address, distances, packages)
    create_route(truck2, index_of_address, distances, packages)
    create_route(truck3, index_of_address, distances, packages)

# Creates delivery route using nearest neighbor algorithm
def create_route(truck, index_of_address, distances, packages):

    # Route always begins at the hub and starts when the truck departs
    current_location = "HUB"
    current_time = truck.departure_time
    while len(truck.assigned_packages) > 0: # While there are packages remaining to be delivered
        next_package = None
        next_location = None
        shortest_distance = math.inf
        next_deadline = time(23, 59)

        for ID in truck.assigned_packages:
            package = packages.search(ID)
            # Lookup distance between current location and package address
            row = index_of_address[current_location]
            if package.correct_address is not None: # Check is package has been assigned wrong address
                column = index_of_address[package.correct_address]
            else:
                column = index_of_address[package.address]
            distance = distances[row][column]

            # Distance of 0 means that the package is being delivered to the same address and should
            # obviously be delivered next (i.e. at the same time)
            if distance == 0.0:
                next_location = package.address
                shortest_distance = distance
                next_package = ID
                break
            # Priority given to packages with earlier deadlines, unless the deadline is the same,
            # then shortest distance is given priority
            elif package.deadline < next_deadline or (package.deadline == next_deadline and distance < shortest_distance):
                next_location = package.address
                shortest_distance = distance
                next_package = ID
                next_deadline = package.deadline

        truck.delivery_order.append(next_package)   # delivery_order stores the order in which the packages are delivered
        current_location = next_location
        truck.assigned_packages.remove(next_package)    # Remove the package as it has been delivered
        truck.mileage += shortest_distance

        # Assign timestamp
        # Need today's date in order to use timedelta
        today = datetime.today()
        starting_time = datetime.combine(today, current_time)

        duration = timedelta(hours=shortest_distance / truck.MPH)   # Calculates time it takes for truck to travel to next location
        delivered_datetime = starting_time + duration   # Time of delivery
        delivered_time = delivered_datetime.time()  # Extract just time

        packages.search(next_package).delivered_timestamp = delivered_time

        current_time = delivered_time

        print(next_package, delivered_time, packages.search(next_package).deadline)


    print(truck.delivery_order)
    print(truck.mileage)
    print()

if __name__ == '__main__':
    main()