# Student ID: 002854304
from hashtable import HashTable
from package import Package
from status import Status
import csv
from datetime import datetime

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
            distances.append(row[1:])

    # Dictionary that will store the row / colum index of the address in the 2D array
    index_of_address = {address: i for i, address in enumerate(addresses)}

    # row = index_of_address["6351 South 900 East"]
    # print(row)
    # column = index_of_address["HUB"]
    # print(column)
    # test = distances[row][column]
    # print(test)

    # Counts number of lines in CSV, which equals the number of packages
    with open('PackageFileCleaned.csv', 'r', encoding='utf-8') as f:
        line_count = sum(1 for line in f)
        # Remove 1 from count to disregard headers
        line_count -= 1

    # Hash table to store packages
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

    print(packages.search(9))


if __name__ == '__main__':
    main()