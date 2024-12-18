from abc import ABC, abstractmethod

class MusicPlayer(ABC):
    @abstractmethod
    def play(self) -> None:
        pass
    
    @abstractmethod
    def pause(self) -> None:
        pass