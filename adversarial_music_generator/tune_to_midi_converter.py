from midiutil import MIDIFile
from midiutil.MidiFile import MIDITrack

from adversarial_music_generator.models.timbre import Timbre
from adversarial_music_generator.models.tune import Tune


class TuneToMidiConverter:
    def convert(self, tune: Tune, output_file_path: str):
        midi_file = MIDIFile(
            numTracks=len(tune.tracks)
        )

        midi_file.addTempo(0, 0, tune.bpm)
        length_of_quarter_seconds = 60 / tune.bpm

        for idx, track in enumerate(tune.tracks):
            midi_file.addTrackName(idx, 0.0, 'Track ' + str(idx))
            midi_file.addProgramChange(idx, idx, 0.0, self._generate_program_number(track.timbre))
            for note in track.notes:
                start_time_in_quarters = note.start_time_seconds / length_of_quarter_seconds
                length_in_quarters = (note.end_time_seconds - note.start_time_seconds) / length_of_quarter_seconds
                midi_file.addNote(idx, idx, note.note, start_time_in_quarters, length_in_quarters, round(note.velocity * 127))

        with open(output_file_path, "wb") as output_file:
            midi_file.writeFile(output_file)

    def _generate_program_number(self, timbre: Timbre) -> int:
        return 42  # cello
