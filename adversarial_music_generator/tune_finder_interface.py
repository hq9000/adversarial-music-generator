from abc import abstractmethod, ABC
from typing import List

from adversarial_music_generator.find_tunes_task import FindTunesTask
from adversarial_music_generator.models.tune import Tune


class TuneFinderInterface(ABC):
    @abstractmethod
    def find_tunes(self, find_tunes_task: FindTunesTask) -> List[Tune]:
        pass
