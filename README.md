# Adversarial Music Generator
_...exploring the randomness in music_

## Overview

This library implements a framework for automated multitrack music composition based on guided random search.

The library strives to be generic and for that provides interfaces to be implemented by the users. 

Additionally, a reference implementation of componenets is provided (called "NaiveRandom").

### Examples

[These examples](https://github.com/hq9000/adversarial-music-generator/tree/amg-8-tune-post-processor/adversarial_music_generator/demo/naive_random/mp3_examples) are generated using the reference implementation (see the code in `demo/naive_random`)



### Inspired by...
The approach implemented in the library largely borrows  inspiration from evolutionary approaches such as genetic algorithms.


## How the search is performed

There are 4 core procedures involved in the process:

* generation
* evaluation
* reduction  
* mutation

The four procedures above are used in the high-level search process of finding the tunes.

### Description of the high-level search process

for the details of implementation see `adversarial_music_generator.tune_finder.TuneFinder`

The process works, roughly, as follows:

1. `Generate` initial population of random tunes
2. `Evaluate` them
3. `Reduce` the evaluations
4. Sort all of the tunes and keep only the predefined number of the "best" ones, discard all the others
5. execute the following  iterative epoch-by-epoch process for the required number of epochs:
   1. apply random `Mutations` to the generation
   2. rank and sort all the tunes in this generation (using `Evaluation` and `Reduction`)
   3. keep the best Tunes only
   4. repeat 
6. in the end we are left with the last "mutation" generation and we can simply take the best tunes from that one.

### Description of the core procedures

Below goes the description of each of the core procedures used in the high-level search process.

#### Generation

Generation is a purely random and independent generation of so called `Tunes` (you can think of a Tune as a multitrack midi stripped of non-essential features. See `adversarial_music_generator.models.tune.Tune`).

The framework does not impose any particular way of generation, instead, it provides an interface to be implemented by the users of the library (see `adversarial_music_generator.interfaces.TuneGeneratorInterface`). There is an exemplary "naive" implementation of generator interface used in the demo (see `adversarial_music_generator.demo.naive_random.naive_random_generator.NaiveRandomGenerator`). This reference implementation basically throws a bunch of random notes into the tracks.

#### Evaluation

Evaluation is a procedure of getting one `Tune` and assigning it a multi-dimensional score (`adversarial_music_generator.models.tune_evaluation_result.TuneEvaluationResult`). Each dimension of the evaluation is called an `aspect`.

Again, the framework is generic, and only requires that evaluator classes implement `TuneEvaluatorInterface`.

The reference "naive" implementation of evaluator can be seen in `NaiveRandomEvaluator`. This implementation takes a tune and assigns it scores for such aspects as:

- "RHYTHMICALITY"
  - punishing the tunes that have a lot of out-of-beat notes
- "HARMONY"
  - punishing the tunes that have a lot of dissonant intervals
- "CONTENT"
  - punishing the tunes having too much or too few notes

#### Reduction

Reduction is a process of "reducing" the multi-dimensional evaluation into a single float number. 

The reference `NaiveRandomReducer` does so by simply calculating a weighted sum of different components.

#### Mutation

Mutation is a process of randomly applying certain small changes to a Tune. 

Examples:

- remove a note
- add a note
- change the note's pitch 

reference implementation: `adversarial_music_generator.demo.naive_random.naive_random_mutator.NaiveRandomMutator`

## How to compile cython parts

not needed as it's done automatically with 
```
pyximport.install()
from adversarial_music_generator.evaluation_lib.harmony import calculate_disharmony
```
