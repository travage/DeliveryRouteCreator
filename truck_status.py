from enum import Enum

class TruckStatus(Enum):
    AT_HUB = 'Not departed yet'
    OUT = 'Out on route'
    DONE = 'Route completed'
    RETURNING = 'Returning to Hub'
    FINISHED = 'Back at Hub; route completed'
