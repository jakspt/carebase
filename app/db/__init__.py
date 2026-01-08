from .database_strategy import DatabaseStrategy
from .mongo.base import MongoBase
from .mongo.clerk_mixin import MongoClerkMixin
from .mongo.doctor_mixin import MongoDoctorMixin
from .sql.base import SQLBase
from .sql.clerk_mixin import SQLClerkMixin
from .sql.doctor_mixin import SQLDoctorMixin

"""
Implement everything for the doctor use case in SQLDoctorMixin/MongoDoctorMixin,
everything for the clerk use case in MongoClerkMixin/MongoClerkMixin,
and the base functionality (connecting to the DB) in the SQLBase/MongoBase

MariaDBStrategy and MongoDBStrategy inherit from the necessary classes via multiple inheritance

=> No merge conflicts when working in teams 
"""


class MariaDBStrategy(
    SQLBase,  # Adds _get_conn
    SQLDoctorMixin,  # Adds Doctor methods
    SQLClerkMixin,  # Adds Clerk methods
    DatabaseStrategy,  # Enforces the contract
):
    pass


class MongoDBStrategy(MongoDoctorMixin, MongoClerkMixin, MongoBase, DatabaseStrategy):
    pass


# Strategy Switching:

_current_strategy = MariaDBStrategy()


def get_db() -> DatabaseStrategy:
    return _current_strategy


def switch_to_mongo():
    global _current_strategy
    print("SWITCHING TO MONGO")
    _current_strategy = MongoDBStrategy()


# no switching back since there is no requirement to do so
