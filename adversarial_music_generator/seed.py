from random import Random
from typing import Dict, TypeVar

T = TypeVar('T')
RandomChoiceOptions = Dict[T, int]


class Seed:
    """
    A controllable random tune_seed for all kinds of repeatable random uses

    This one is actually copy-pasted from py-headless-daw repo
    Requirements:
      - similar tune_seeds should produce similar outputs
      - ...
    """

    def __init__(self, seed: str = None):
        self._seed: str = 'default tune_seed'
        if seed is not None:
            self._seed = seed
        self._generator: Random = Random(seed)

    def randint(self, min_val: int, max_val: int, sub_seed: str):
        local_generator = Random(self._seed + sub_seed)
        return local_generator.randint(min_val, max_val)

    def randfloat(self, min_val: float, max_val: float, sub_seed: str) -> float:
        local_generator = Random(self._seed + sub_seed)
        rnd = local_generator.random()
        return min_val + rnd * (max_val - min_val)

    def choose_one(self, probabilities: RandomChoiceOptions[T], sub_seed: str) -> T:
        sum_of_probabilities: int = 0

        # probabilities do not have to sum up to 100 or anything,
        # it's enough if they are positive integers
        for option, add_probability in probabilities.items():
            sum_of_probabilities += add_probability

        dice_value = self.randint(0, sum_of_probabilities - 1, sub_seed)

        sum_of_probabilities = 0
        for option, add_probability in probabilities.items():
            if sum_of_probabilities <= dice_value < sum_of_probabilities + add_probability:
                return option
            sum_of_probabilities += add_probability

        raise ValueError('unable to generate a random choice (error: 8256cd68)')

    def create_subseed(self, subseed_str):  # type: (str)->Seed
        return Seed(self._seed + "/" + subseed_str)
