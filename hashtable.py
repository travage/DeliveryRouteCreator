import math

class HashTable:
    def __init__(self, num_of_packages):
        # Prime bucket sizes to help more evenly distribute keys
        # If there are more than ~1.1 million packages, additional prime bucket sizes are needed
        # TODO: Add check to warn of this ^
        self.prime_sizes = [
            7, 17, 37, 53, 97, 193, 389,
            769, 1543, 3079, 6151, 12289,
            24593, 49157, 98317, 196613,
            393241, 786433, 1572869
        ]

        # Calculate an initial list size for a load factor of 0.7
        init_size = num_of_packages + math.ceil((num_of_packages / 7) * 3)
        # Find next largest prime and make it the number of buckets
        starting_size = 0
        for prime in self.prime_sizes:
            if prime >= init_size:
                starting_size = prime
                break

        # Underlying list where values will be stored
        # Each bucket is a list to implement chaining
        self.table = [[] for x in range(starting_size)]

        # Tracks number of key-value pairs
        self.size = 0

    def insert(self, key, value):
        index = key % len(self.table)
        bucket = self.table[index]

        # Check if bucket already contains key; if so, update it with new value
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # If bucket doesn't contain key, add key-value pair as a tuple
        bucket.append((key, value))
        self.size += 1

        # Check load factor and resize if above 0.7
        if (self.size / len(self.table)) > 0.7:
            self.resize()

    # Prevents endless recursion loop when resize() needs to rehash the values
    def insert_without_resize(self, key, value):
        index = key % len(self.table)
        bucket = self.table[index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.size += 1

    def search(self, key):
        index = key % len(self.table)
        bucket = self.table[index]

        # Iterate through key-value pairs
        for (k, v) in bucket:
            if k == key:
                return v

        # Key not found
        return None

    def delete(self, key):
        index = key % len(self.table)
        bucket = self.table[index]

        # Check bucket for key and delete tuple if so
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True

        return False

    def resize(self):
        # Duplicate old table
        old_table = self.table

        # Find next largest prime and make it the next size
        next_size = 0
        for prime in self.prime_sizes:
            if prime > len(self.table):
                next_size = prime
                break

        # Reset table to new size
        self.table = [[] for x in range(next_size)]

        # Reset size to 0 since insert() will increment size
        self.size = 0

        # Rehash key-values into new table
        for bucket in old_table:
            for key, value in bucket:
                self.insert_without_resize(key, value)

    def __str__(self):
        return str(self.table)