from abc import ABC
from typing import List

from adversarial_music_generator.interfaces import TuneGeneratorInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.timbre_repository import TimbreRepository
from adversarial_music_generator.models.track import Track
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.seed import Seed


class TuneGenerator(TuneGeneratorInterface):
    def generate_tunes(self, seed: Seed) -> Tune:
        res = Tune()
        res.tracks = [self._generate_one_track(seed, i) for i in range(0, 3)]
        return res

    def _generate_one_track(self, seed: Seed, track_number: int) -> Track:
        notes: List[Note] = []
        for i in range(0, seed.randint(1, 100, f'number of notes for track {track_number}')):
            start_time = seed.randfloat(0, 10.0, f'note start for track {track_number} and note {i}')
            length = seed.randfloat(0.1, 1.0, f'note length for track {track_number} and note {i}')
            pitch = seed.randint(40, 90, f"pitch for track {track_number} and note {i}")
            note = Note(start_time_seconds=start_time, end_time_seconds=start_time + length, note=pitch, velocity=100)
            notes.append(note)

        track = Track(TimbreRepository.lead)
        track.notes = notes
        return track
