from typing import List, Optional

from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre import Timbre


class Track:
    def __init__(self, timbre: Timbre):
        self.timbre: Timbre = timbre
        self.notes: List[Note] = []
        self.tag: Optional = None
