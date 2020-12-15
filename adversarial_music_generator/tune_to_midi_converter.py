from midiutil import MIDIFile

from adversarial_music_generator.models.tune import Tune


class TuneToMidiConverter:
    def convert(self, tune: Tune, output_file_path: str):
        midi_file = MIDIFile()

        midi_file.addTempo(0, 0, tune.bpm)
        length_of_quarter_seconds = 60 / tune_bpm

        for idx, track in enumerate(tune.tracks):
            for note in track.notes:
                start_time_in_quarters = note.start_time_seconds / length_of_quarter_seconds
                length_in_quarters = (note.end_time_seconds - note.start_time_seconds) / length_of_quarter_seconds
                midi_file.addNote(idx, idx, note.note, start_time_in_quarters, length_in_quarters, note.velocity)

        with open(output_file_path, "wb") as output_file:
            midi_file.writeFile(output_file)
