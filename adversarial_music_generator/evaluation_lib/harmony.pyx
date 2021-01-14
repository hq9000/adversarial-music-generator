from ctypes import Array

def calculate_disharmony(starts_py: Array[float], ends_py: Array[float], pitches_py: Array[int])-> float:
    cdef int i, j, num_notes
    cdef float res = 0.0
    num_notes = len(starts_py)

    cdef float[:] starts = starts_py
    cdef float[:] ends = ends_py
    cdef int[:] pitches = pitches_py

    for i in range(num_notes):
        for j in range(i+1, num_notes):
            res += _calculate_amount_of_disharmony_of_two_notes(i, j, starts, ends, pitches)

    return res

cdef inline float _get_disharmony_map_value(int interval):
    if interval == 0:
        return 0.0
    elif interval == 1:
        return 10.0
    elif interval == 2:
        return 3.0
    elif interval == 3:
        return 3.0
    elif interval == 4:
        return 2.0
    elif interval == 5:
        return 1.0
    elif interval == 6:
        return 10.0
    elif interval == 7:
        return 1.0
    elif interval == 8:
        return 3.0
    elif interval == 9:
        return 6.0
    elif interval == 10:
        return 3.0
    elif interval == 11:
        return 10.0

cdef float _calculate_amount_of_disharmony_of_two_notes(int note_a_idx, int note_b_idx, float[:] starts, float[:] ends, int[:] pitches):

    cdef float start_a = starts[note_a_idx]
    cdef float end_a = ends[note_a_idx]
    cdef int pitch_a = pitches[note_a_idx]

    cdef float start_b = starts[note_b_idx]
    cdef float end_b = ends[note_b_idx]
    cdef int pitch_b = pitches[note_b_idx]


    cdef float overlapping_length = _calculate_perceived_overlapping_length(start_a, end_a, start_b, end_b)

    if overlapping_length == 0.0:
        return 0.0

    cdef int interval = (pitch_a - pitch_b) % 12
    if interval < 0:
        interval = -1 * interval

    cdef float disharmony_map_value = _get_disharmony_map_value(interval)
    return disharmony_map_value * overlapping_length

cdef inline float _max(float a, float b):
    if a > b:
        return a
    else:
        return b

cdef inline float _min(float a, float b):
    if a < b:
        return a
    else:
        return b


cdef inline float _calculate_perceived_overlapping_length(float start_a, float end_a, float start_b, float end_b):
    cdef inline float hearing_inertia = 1.5
    return _max(0.0, _min(end_a + hearing_inertia, end_b + hearing_inertia) - _max(start_a, start_b))
