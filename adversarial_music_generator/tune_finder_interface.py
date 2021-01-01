from abc import abstractmethod, ABC
from typing import Iterable

from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.models.tune import Tune


class TuneFinderInterface(ABC):
    @abstractmethod
    def findTune(self, find_tunes_task: FindTunesTask) -> Iterable[Tune]:
        pass
