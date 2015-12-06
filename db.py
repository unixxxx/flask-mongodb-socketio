import json
from datetime import datetime, timedelta
from dateutil.parser import parse
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DATABASE = "Gavichede"
MONGO_CLIENT = client = MongoClient(MONGO_HOST, MONGO_PORT)


def get_database() -> 'pymongo.database.Database':
    return MONGO_CLIENT.get_database(MONGO_DATABASE)  # type :pymongo.database.Database


class Location:
    def __init__(self, data: dict):
        self.data_dict = data  # type:dict
        self.errors = []  # type : [str]
        self.is_valid = True
        self.__type = 'Point'  # type:str
        self.__coordinates = None  # type:[float]
        self.coordinates = self.data_dict.get("coordinates")

    @property
    def type(self) -> str:
        return self.__type

    @property
    def coordinates(self) -> [float]:
        return self.__coordinates

    @coordinates.setter
    def coordinates(self, value: [float]) -> None:
        if value is None or type(value) is not list or len(value) != 2:
            self.is_valid = False
            self.errors.append("coordinates is required and it must be list of two floats \n you passed %s" % (
                str(self.coordinates),))
            self.__coordinates = None
        else:
            self.__coordinates = value

    def to_json(self) -> str:
        return '{"type":"%s","coordinates":%s}' % (self.type, self.coordinates)

    def to_dict(self) -> dict:
        return dict(type=self.type, coordinates=self.coordinates)


class _Entities:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["entities"]

    def find_one(self, query: dict) -> 'Entity':
        item = self.collection.find_one(query)
        return None if item is None else Entity(item)

    def find(self, query: dict) -> 'list(Entities)':
        return (Entity(item) for item in self.collection.find(query))

    def insert_one(self, entity: 'Entity') -> 'bson.ObjectId':
        obj_id = self.collection.insert_one(entity.to_dict())
        entity.id = obj_id.inserted_id
        return entity

    def remove(self, query):
        return self.collection.remove(query)

    def get_last_20_minutes(self):
        return self.find(query={"start_time": {"$gt": datetime.now() - timedelta(minutes=20)}})


class Entity:
    def __init__(self, data: str) -> None:
        self.data_dict = data if type(data) is dict else json.loads(data)  # type: dict
        self.id = self.data_dict.get("_id")  # type : bson.ObjectId
        self.__errors = []  # type :[str]
        self.__is_valid = True  # type: bool
        self.__device_id = None  # type : str
        self.device_id = self.data_dict.get("device_id")
        self.__start_time = None  # type : datetime
        self.start_time = self.data_dict.get("start_time")
        self.__location = None  # type : Location
        self.location = Location(self.data_dict.get("location", dict()))  # type: Location

    @property
    def errors(self) -> [str]:
        return self.__errors + self.location.errors

    @property
    def is_valid(self) -> bool:
        if not self.location.is_valid:
            return False
        return self.__is_valid

    @is_valid.setter
    def is_valid(self, value: bool) -> None:
        self.__is_valid = value

    @property
    def device_id(self) -> str:
        return self.__device_id

    @device_id.setter
    def device_id(self, value: str) -> None:
        if value is not None and type(value) is not str:
            self.is_valid = False
            self.__errors.append('wrong type "device_id" is str')
            self.__device_id = None
            return

        elif value is None or len(value) < 1:
            self.is_valid = False
            self.__errors.append('"device_id" is required')
            self.__device_id = None
        else:
            self.__device_id = value

    @property
    def start_time(self) -> datetime:
        return self.__start_time

    @start_time.setter
    def start_time(self, value: 'Union(str, datetime)') -> None:
        if value is None:
            self.is_valid = False
            self.__errors.append("start_time is required")
            self.__start_time = None
        elif type(value) is datetime:
            self.__start_time = value
        elif type(value) is int:
            self.__start_time = datetime.fromtimestamp(value / 1000)
        else:
            # noinspection PyBroadException
            try:
                self.__start_time = parse(value)
            except:
                self.is_valid = False
                self.__errors.append("start_time wrong datetime format")
                self.__start_time = None

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, value: 'Location'):
        if not value.is_valid:
            self.is_valid = False
        self.__location = value

    def to_json(self) -> str:
        return '{"device_id":"%s","start_time":"%s","location":%s,%s}' % (
            self.device_id, self.start_time, self.location.to_json(),
            "" if self.id is None else '"_id":%s' % (self.id,)
        )

    def to_dict(self) -> dict:
        _return = dict(device_id=self.device_id, start_time=self.start_time, location=self.location.to_dict())
        return _return if self.id is None else _return.update({"_id": self.id})


Entities = _Entities()

if __name__ == '__main__':
    e = Entity(
        data='{"device_id":"id2","start_time":"2015-12-05 20:19:44","location":{"type":"point","coordinates":[45.5,46]}}')
    items = list(Entities.get_last_20_minutes())
    print(items)
