from abc import ABC, abstractmethod

class Base(ABC):
    name:str

    @abstractmethod
    def execute(self, input_data:dict):
        pass