from adversarial_music_generator.models.timbre import Timbre


class TimbreRepository:
    bass_drum: Timbre = Timbre(Timbre.FREQUENCY_CHARACTER_SOFT, Timbre.DYNAMICS_SHARP)
    bass: Timbre = Timbre(Timbre.FREQUENCY_CHARACTER_SOFT, Timbre.DYNAMICS_SOFT)
    pad: Timbre = Timbre(Timbre.FREQUENCY_CHARACTER_SOFT, Timbre.DYNAMICS_SOFT)
    lead: Timbre = Timbre(Timbre.FREQUENCY_CHARACTER_BRIGHT, Timbre.DYNAMICS_SHARP)
