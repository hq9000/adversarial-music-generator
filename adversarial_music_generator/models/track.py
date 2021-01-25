from typing import List, Dict, Any

from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre import Timbre


class Track:
    def __init__(self, timbre: Timbre):
        self.timbre: Timbre = timbre
        self.notes: List[Note] = []

        """
        a general purpose piece of info to allow generators put something
        for later
        
        It's a dict where tag names are strings to allow tag checking.
        
        if my_tag in track.tags:
            ...
            
        """
        self.tags: Dict[str, Any] = {}
