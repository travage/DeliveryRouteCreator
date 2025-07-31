from enum import Enum

class PackageStatus(Enum):
    AT_HUB = 'At Hub'
    EN_ROUTE = 'En route'
    DELIVERED = 'Delivered'
    DELAYED = 'Delayed'