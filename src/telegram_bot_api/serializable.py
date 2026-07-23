import json
from abc import ABC, abstractmethod


class Serializable(ABC):
    @abstractmethod
    def serialize(self, name: str, params: dict, files: dict):
        ...


class SerializableJSON[T](Serializable):
    def __init__(self, value: T):
        self.value = value

    def serialize(self, name: str, params: dict, files: dict):
        params[name] = json.dumps(self.value)


class SerializableInputFile(Serializable):
    def __init__(self, path: str):
        self.path = path

    def serialize(self, name: str, params: dict, files: dict):
        with open(self.path, "rb") as f:
            files[name] = f.read()
