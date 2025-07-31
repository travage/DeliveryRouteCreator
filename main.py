# Student ID: 002854304
from hashtable import HashTable
from package import Package
from package_status import PackageStatus
import csv
from datetime import datetime, time, timedelta
import sys
import os
from truck import Truck
import math
from truck_status import TruckStatus

def main():
    # Get addresses and distances from DistanceTableCleaned.csv
    addresses = []
    distances = []  # Will become 2D-array
    with open('DistanceTableCleaned.csv', newline='', encoding='utf-8') as distances_file:
        reader = csv.reader(distances_file, skipinitialspace=True)

        # Gets addresses from headers
        first_row = next(reader)
        for i in range(1, len(first_row)):  # Starts at cell 1 since cell 0 does not have an address in the matrix
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
        packages = HashTable(line_count)    # Creates hash table


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
                status = PackageStatus.AT_HUB
            else:
                status = PackageStatus.DELAYED

            # Create package object
            package = Package(package_ID, address, city, zip, deadline, weight, specific_truck,
                              delayed_arrival, correct_address, correct_city, correct_zip,
                              must_be_with, status)

            # Insert into hash table
            packages.insert(package.package_ID, package)

    # Manually set up more here if more trucks are needed
    # Departure times set to align with late arrivals
    truck1 = Truck(1, time(8, 0))
    truck2 = Truck(2, time(9, 5))
    truck3 = Truck(3, time(10, 20))
    trucks = {1: truck1, 2: truck2, 3: truck3} # Dict to retrieve truck object with just the truck ID
    truck_has_driver = {1: True, 2: True, 3: False} # Dict to keep track of which truck has the available driver(s)
    drivers_needed = 1  # Defines how many trucks will need a driver during the day, i.e. # of trucks - # of drivers

    # Assign packages to trucks using their package ID
    truck1.assigned_packages = [1, 4, 13, 14, 15, 16, 19, 20, 21, 22, 29, 30, 34, 37, 39, 40]
    truck2.assigned_packages = [3, 5, 6, 11, 12, 17, 18, 23, 25, 26, 27, 31, 32, 35, 36, 38]
    truck3.assigned_packages = [2, 7, 8, 9, 10, 24, 28, 33]

    # Dict used for quick lookup of what truck a package is assigned to
    assigned_truck_lookup = {}  # Package ID is the key, truck ID is the value
    for truck in trucks.values():
        # Keeps track of which packages are assigned to each truck and vice versa
        for package_ID in truck.assigned_packages:
            packages.search(package_ID).assigned_truck = truck.truck_ID
            assigned_truck_lookup[package_ID] = truck.truck_ID

    # CLI to interact with users
    print('**************************************')
    print('Welcome to the Delivery Route Manager!')
    print('**************************************')
    print()
    # Main menu will repeatedly come back up after completely options,
    # until Exit option is chosen
    while True:
        print('Please select from the options below:')
        print('1. Status of ONE package at entered time')
        print('2. Status of ALL packages at entered time')
        print('3. End of day report')
        print('4. Exit')

        choice = input('Enter an option (1-4): ').strip()
        print()

        # Status of one package at time entered by user
        if choice == '1':
            user_package_id = int(input('Please enter the ID of the package: ').strip())
            user_time = input('Please enter the time (in 24-hour format, e.g. 22:00): ').strip()
            print()
            hour = int(user_time.split(':')[0])
            minute = int(user_time.split(':')[1])

            if user_package_id < 0:
                print('Package ID cannot be negative.')
                print()
                continue
            elif hour < 0 or hour > 23 or minute < 0 or minute > 59:
                print('Invalid time entered.')
                print()
                continue

            # Get assigned truck object
            assigned_truck = trucks.get(assigned_truck_lookup[user_package_id])
            # Run delivery route simulation
            simulate_delivery_route(assigned_truck, time(hour, minute), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)
            # Retrieve package object associated with the ID the user entered
            user_package = packages.search(user_package_id)

            print(f'Time: {user_time}')
            print(f'Package ID: {user_package_id}')
            print(f'\tAssigned truck: {user_package.assigned_truck}')
            print(f'\tStatus: {user_package.status.value}')
            if user_package.delivered_timestamp is not None:    # If package has been delivered, show timestamp
                print(f'\tDelivered at: {user_package.delivered_timestamp}')
            print(f'\tGuaranteed delivery by: {user_package.deadline}')
            print(f'\tDelivery address: {user_package.address}')
            print()
            mileage = round(assigned_truck.mileage, 1)
            print(f'Truck {assigned_truck.truck_ID} mileage: {mileage} miles')
            print(f'Truck {assigned_truck.truck_ID} status: {assigned_truck.status.value}')
            if assigned_truck.return_time is not None:  # If truck has returned to the hub after finishing deliveries
                print(f'Truck {assigned_truck.truck_ID} return time: {assigned_truck.return_time}')
            print(f'Packages delivered: {assigned_truck.delivery_order}')
            print(f'Packages remaining: {assigned_truck.assigned_packages}')
            print()
            # Throws away process and starts new one, essentially restarting the program
            # so that any changes are reverted to run fresh simulations
            os.execv(sys.executable, [sys.executable] + sys.argv)
        # Status of all packages at time entered by user
        elif choice == '2':
            user_time = input('Please enter the time (in 24-hour format, e.g. 22:00): ').strip()
            print()
            print(f'Time: {user_time}')
            print()
            hour = int(user_time.split(':')[0])
            minute = int(user_time.split(':')[1])

            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                print('Invalid time entered.')
                print()
                continue

            # Run simulations on all trucks
            simulate_delivery_route(truck1, time(hour, minute), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)
            simulate_delivery_route(truck2, time(hour, minute), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)
            simulate_delivery_route(truck3, time(hour, minute), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)

            print_all_info(trucks, packages) # Prints out info about trucks and their assigned packages after simulation

            # Throws away process and starts new one, essentially restarting the program
            # so that any changes are reverted to run fresh simulations
            os.execv(sys.executable, [sys.executable] + sys.argv)
        # Run simulation until the end of day, i.e. 17:00
        elif choice == '3':
            print('** END OF DAY REPORT **')
            print()
            # Run simulations on all trucks
            simulate_delivery_route(truck1, time(17, 0), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)
            simulate_delivery_route(truck2, time(17, 0), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)
            simulate_delivery_route(truck3, time(17, 0), index_of_address, distances,
                                    packages, trucks, truck_has_driver, drivers_needed)

            print_all_info(trucks, packages)    # Prints out info about trucks and their assigned packages after simulation

            # Throws away process and starts new one, essentially restarting the program
            # so that any changes are reverted to run fresh simulations
            os.execv(sys.executable, [sys.executable] + sys.argv)
        # Exit out of program
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print('Invalid selection, please enter 1-4.')
            print()

# Simulates the delivery route using nearest neighbor algorithm
# Simulation runs until all packages are delivered or the end_time is reach,
# which is either defined by the user input or set to 17:00 to indicate the end of the day
def simulate_delivery_route(truck, end_time, index_of_address, distances, packages, trucks, truck_has_driver, drivers_needed):

    # Route always begins at the hub and starts when the truck departs
    current_location = 'HUB'
    current_time = truck.departure_time
    # While there are packages that have not been delivered and
    # the end time of the simulation has not been reached
    while len(truck.assigned_packages) > 0 and current_time <= end_time:
        next_package = None
        next_location = None
        shortest_distance = math.inf
        next_deadline = time(23, 59)
        if truck.status == TruckStatus.AT_HUB:
            truck.status = TruckStatus.OUT

        for ID in truck.assigned_packages:
            package = packages.search(ID)

            # Change all package statuses to en route
            if package.status == PackageStatus.AT_HUB or package.status == PackageStatus.DELAYED:
                package.status = PackageStatus.EN_ROUTE

            # Update address if original one is incorrect
            if package.correct_address is not None and package.address != package.correct_address:
                package.address = package.correct_address

            # Lookup distance between current location and package address
            row = index_of_address[current_location]
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

        # Calculate timestamp
        # Need today's date in order to use timedelta
        today = datetime.today()
        starting_datetime = datetime.combine(today, current_time) # Combine current time with today's date to form datetime object
        duration = timedelta(seconds=(shortest_distance / truck.MPH) * 3600)  # Calculates duration in seconds for better precision
        delivered_datetime = starting_datetime + duration  # Time of delivery
        delivered_time = delivered_datetime.time()  # Extract just time

        # If the package is delivered before the end time of the simulation
        if delivered_time <= end_time:
            truck.delivery_order.append(next_package)  # delivery_order stores the order in which the packages are delivered
            current_location = next_location
            truck.assigned_packages.remove(next_package)  # Remove the package as it has been delivered
            packages.search(next_package).delivered_timestamp = delivered_time
            packages.search(next_package).status = PackageStatus.DELIVERED
            truck.mileage += shortest_distance # Add distance to truck mileage counter
        # If the package would be delivered after the end time of the simulation,
        # only calculate the distance covered until reach the end time
        else:
            end_datetime = datetime.combine(today, end_time) # Create datetime object for the end time
            elapsed_time = (end_datetime - starting_datetime).total_seconds()   # Calculate time elapsed from last delivery until end time
            partial_distance = (truck.MPH / 3600) * int(elapsed_time) # Distance covered
            truck.mileage += partial_distance

        # Set current time to when the next package is delivered
        current_time = delivered_time

    # Once packages are all delivered, set status to route completed
    if len(truck.assigned_packages) == 0:
        truck.status = TruckStatus.DONE

    # If the truck is done delivering packages and another truck needs a driver,
    # send the trucks back to the hub so that the driver can move trucks
    if len(truck.assigned_packages) == 0 and drivers_needed > 0:
        row = index_of_address[current_location]
        column = index_of_address['HUB']
        return_distance = distances[row][column]

        # Calculates when truck would return to hub from the last delivery address
        # Today's needed in order to use timedelta
        today = datetime.today()
        last_delivery_time = packages.search(truck.delivery_order[-1]).delivered_timestamp  # Timestamp of last package delivered
        last_delivery_datetime = datetime.combine(today, last_delivery_time)
        return_duration = timedelta(seconds=(return_distance / truck.MPH) * 3600)   # Calculate duration in seconds for better accuracy
        return_datetime = last_delivery_datetime + return_duration
        return_time = return_datetime.time()

        # Loop through all available trucks
        for i in trucks.values():
            # If the truck that is done delivering gets back to the hub before another truck departs
            # AND the departing truck needs a driver
            if return_time <= i.departure_time and truck_has_driver.get(i.truck_ID) == False:
                # If the truck that is done returns before the end time of the simulation,
                # calculate full distance traveled and add that to the total mileage for the truck,
                # plus move driver from finished truck to departing truck
                if return_time <= end_time:
                    truck.mileage += return_distance
                    truck.return_time = return_time
                    truck.status = TruckStatus.FINISHED
                    truck_has_driver[truck.truck_ID] = False   # Set truck that is finished as no longer having a driver
                    truck_has_driver[i.truck_ID] = True   # Set truck that will be departing to having a driver now
                    drivers_needed -= 1   # One less truck now needs a driver
                # If the finished truck will not get back to the depot before the end of the simulation,
                # calculate the distance covered until the end time and add that to the truck's total mileage
                else:
                    end_datetime = datetime.combine(today, end_time)
                    elapsed_time = (end_datetime - last_delivery_datetime).total_seconds()
                    partial_distance = (truck.MPH / 3600) * int(elapsed_time)
                    truck.mileage += partial_distance
                    truck.status = TruckStatus.RETURNING

                # Driver has been moved, no further trucks need to be checked
                break

# Prints out info regarding the trucks and their assigned packages after the simulation has ended
def print_all_info(trucks, packages):
    total_mileage = 0  # Keeps tracks of mileage on ALL trucks
    # Loop through each truck and print info
    for truck in trucks.values():
        print('**********************************')
        print(f'Truck #: {truck.truck_ID}')
        print(f'Truck status: {truck.status.value}')
        mileage = round(truck.mileage, 1)
        total_mileage += mileage
        print(f'Total mileage: {mileage} miles')
        print()
        print('-----------------')
        print('Assigned Packages')
        # Loop through all delivered packages and print info
        for pack_id in truck.delivery_order:
            print('-----------------')
            pack = packages.search(pack_id)
            print(f'\tPackage ID: {pack_id}')
            print(f'\tStatus: {pack.status.value}')
            print(f'\tDelivered at: {pack.delivered_timestamp}')
            print(f'\tGuaranteed delivery by: {pack.deadline}')
            print(f'\tDelivery address: {pack.address}')
        # Loop through all packages that have not been delivered and print info
        for pack_id in truck.assigned_packages:
            print('-----------------')
            pack = packages.search(pack_id)
            print(f'\tPackage ID: {pack_id}')
            print(f'\tStatus: {pack.status.value}')
            print(f'\tGuaranteed delivery by: {pack.deadline}')
            print(f'\tDelivery address: {pack.address}')
        print('-----------------')
        print()
    round_total_mileage = round(total_mileage, 1)
    print(f'Total mileage for all trucks: {round_total_mileage} miles')
    print()

if __name__ == '__main__':
    main()