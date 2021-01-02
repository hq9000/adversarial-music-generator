from typing import List

from adversarial_music_generator.interfaces import TuneMutatorInterface, TuneGeneratorInterface
from adversarial_music_generator.models.note import Note
from adversarial_music_generator.models.tune import Tune
from adversarial_music_generator.seed import Seed


class NaiveRandomMutator(TuneMutatorInterface):

    def mutate_tune(self, tune: Tune, seed_str: str):
        seed = Seed(seed_str)

        num_notes_to_remove = seed.randint(0, 10, 'num notes to remove')
        num_notes_to_change = seed.randint(0, 10, 'num notes to change')

        total_num_notes = 0
        for track in tune.tracks:
            total_num_notes += len(track.notes)

        removed_notes_ids = set([seed.randint(0, total_num_notes, 'removed note' + str(i)) for i in
                                 range(num_notes_to_remove)])

        changed_notes_ids = set([seed.randint(0, total_num_notes, 'changed note' + str(i)) for i in
                                 range(num_notes_to_change)])

        for i, note in enumerate(tune.all_notes()):
            if i in changed_notes_ids:
                movement = seed.randint(-6, 5, "note movement" + str(i))
                note.note += movement

            if i in removed_notes_ids:
                note.removed = True

        for track in tune.tracks:
            new_notes: List[Note] = []
            for note in track.notes:
                if not note.removed:
                    new_notes.append(note)

            track.notes = new_notes
