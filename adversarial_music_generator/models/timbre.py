class Timbre:
    FREQUENCY_CHARACTER_SOFT = "fc_soft"
    FREQUENCY_CHARACTER_BRIGHT = "fc_bright"

    DYNAMICS_SOFT = "dyn_soft"
    DYNAMICS_SHARP = "dyn_sharp"

    VALID_FREQUENCY_CHARACTERS = [
        FREQUENCY_CHARACTER_SOFT,
        FREQUENCY_CHARACTER_BRIGHT
    ]

    VALID_DYNAMICS = [
        DYNAMICS_SOFT,
        DYNAMICS_SHARP
    ]

    def __init__(self, frequency_character: str, dynamics: str):
        assert (frequency_character in self.VALID_FREQUENCY_CHARACTERS)
        assert (dynamics in self.VALID_DYNAMICS)

        self.frequency_character: str = frequency_character
        self.dynamics: str = dynamics
