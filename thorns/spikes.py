#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

__author__ = "Marek Rudnicki"

import random
import numpy as np

from collections import Iterable

import pandas as pd

from . import calc




def select_trains(spike_trains, **kwargs):

    mask = np.ones(len(spike_trains), dtype=bool)
    for key,val in kwargs.items():
        mask = mask & np.array(spike_trains[key] == val)

    selected = spike_trains[mask]

    return selected


select_spike_trains = select_trains
select = select_trains
sel = select_trains





def make_trains(data, **kwargs):
    if 'fs' in kwargs:
        assert 'duration' not in kwargs


    meta = {}
    for k,v in kwargs.items():
        if k == 'fs':
            continue

        if isinstance(v, Iterable) and not isinstance(v, basestring):
            assert len(v) == len(data)
            meta[k] = v
        else:
            meta[k] = [v] * len(data)



    if isinstance(data, np.ndarray) and (data.ndim == 2) and ('fs' in kwargs):
        trains = _array_to_trains(data, kwargs['fs'], **meta)

    elif isinstance(data[0], Iterable):
        trains = _arrays_to_trains(data, **meta)

    else:
        raise RuntimeError("Spike train format not supported.")


    return trains





def _arrays_to_trains(arrays, **kwargs):


    ### Make sure we have duration
    if 'duration' not in kwargs:
        max_spikes = [np.max(a) for a in arrays if len(a)>0]
        if max_spikes:
            duration = np.max(max_spikes)
        else:
            duration = 0
        kwargs['duration'] = np.repeat(duration, len(arrays))


    trains = {'spikes': arrays}
    trains.update(kwargs)

    trains = pd.DataFrame(trains)


    return trains





def _array_to_trains(array, fs, **kwargs):
    """ Convert time functions to a list of spike trains.

    fs: samping frequency in Hz
    a: input array

    return: spike trains with spike timings

    """
    assert array.ndim == 2

    trains = []
    for a in array.T:
        a = a.astype(int)
        t = np.arange(len(a))
        spikes = np.repeat(t, a) / fs

        trains.append( spikes )


    assert 'duration' not in kwargs

    kwargs['duration'] = len(array) / fs

    spike_trains = _arrays_to_trains(
        trains,
        **kwargs
    )

    return spike_trains








def trains_to_array(spike_trains, fs):
    """Convert spike trains to signals."""

    duration = calc.get_duration(spike_trains)

    nbins = np.ceil(duration * fs)
    tmax = nbins / fs

    signals = []
    for spikes in spike_trains['spikes']:
        signal, bin_edges = np.histogram(
            spikes,
            bins=nbins,
            range=(0, tmax)
        )
        signals.append(
            signal
        )

    signals = np.array(signals).T

    return signals






def accumulate_spike_trains(spike_trains, ignore=None, keep=None):

    """Concatenate spike trains with the same meta data. Trains will
    be sorted by the metadata.

    """

    keys = spike_trains.columns.tolist()
    keys.remove('spikes')

    if ignore is not None:
        assert keep is None
        for k in ignore:
            keys.remove(k)

    if keep is not None:
        assert ignore is None
        keys = keep


    groups = spike_trains.groupby(keys, as_index=False)


    acc = groups.agg({
        'spikes': lambda x: tuple(np.concatenate(tuple(x.values)))
    })

    return acc


accumulate_spikes = accumulate_spike_trains
accumulate_trains = accumulate_spike_trains
accumulate = accumulate_spike_trains




def trim_spike_trains(spike_trains, start, stop):
    """Return spike trains with that are between `start' and
    `stop'.

    """

    if start is not None and stop is not None:
        assert start < stop

    if start is None:
        tmin = 0
    else:
        tmin = start

    if stop is None:
        tmaxs = spike_trains['duration']
    else:
        tmaxs = np.ones(len(spike_trains)) * stop


    assert np.all(tmin < tmaxs)


    trimmed_trains = []
    for key in spike_trains.dtype.names:
        if key == 'spikes':
            trimmed_spikes = []
            for spikes,tmax in zip(spike_trains['spikes'], tmaxs):

                spikes = spikes[ (spikes >= tmin) & (spikes <= tmax)]
                spikes -= tmin

                trimmed_spikes.append(spikes)


            trimmed_trains.append(
                trimmed_spikes
            )


        elif key == 'duration':
            durations = np.array(spike_trains['duration'])

            durations[ durations>tmaxs ] = tmaxs[ durations>tmaxs ]
            durations -= tmin

            trimmed_trains.append(durations)


        else:
            trimmed_trains.append(spike_trains[key])

    trimmed_trains = np.array(
        zip(*trimmed_trains),
        dtype=spike_trains.dtype
    )

    return trimmed_trains




trim = trim_spike_trains
trim_trains = trim_spike_trains


# def remove_empty(spike_trains):
#     new_trains = []
#     for train in spike_trains:
#         if len(train) != 0:
#             new_trains.append(train)
#     return new_trains



def fold_spike_trains(spike_trains, period):
    """ Fold each of the spike trains.

    >>> from thorns import arrays_to_trains
    >>> a = [np.array([1,2,3,4]), np.array([2,3,4,5])]
    >>> spike_trains = arrays_to_trains(a, duration=9)
    >>> fold_spike_trains(spike_trains, 3)
    [array([1, 2]), array([0, 1]), array([2]), array([0, 1, 2])]

    # >>> spike_trains = [np.array([2.]), np.array([])]
    # >>> fold_spike_trains(spike_trains, 2)
    # [array([], dtype=float64), array([ 0.]), array([], dtype=float64), array([], dtype=float64)]

    """
    data = {key:[] for key in spike_trains.dtype.names}

    for train in spike_trains:
        period_num = int( np.ceil(train['duration'] / period) )
        last_period = np.fmod(train['duration'], period)

        spikes = train['spikes']
        for idx in range(period_num):
            lo = idx * period
            hi = (idx+1) * period
            sec = spikes[(spikes>=lo) & (spikes<hi)]
            sec = np.fmod(sec, period)
            data['spikes'].append(sec)

            data['duration'].append(period)

        if last_period > 0:
            data['duration'][-1] = last_period


        for key in spike_trains.dtype.names:
            if key in ('spikes', 'duration'):
                continue

            data[key].extend(
                [train[key]] * period_num
            )


    arrays = (data[key] for key in spike_trains.dtype.names)

    folded_trains = np.array(
        zip(*arrays),
        dtype=spike_trains.dtype
    )


    return folded_trains

fold = fold_spike_trains
fold_trains = fold_spike_trains



# def concatenate_spikes(spike_trains):
#     return [np.concatenate(tuple(spike_trains))]

# concatenate = concatenate_spikes
# concat = concatenate_spikes


# def shift_spikes(spike_trains, shift):
#     shifted = [train+shift for train in spike_trains]

#     return shifted

# shift = shift_spikes


# def split_and_fold_trains(spike_trains,
#                           silence_duration,
#                           tone_duration,
#                           pad_duration,
#                           remove_pads):
#     silence = trim(spike_trains, 0, silence_duration)


#     tones_and_pads = trim(spike_trains, silence_duration)
#     tones_and_pads = fold(tones_and_pads, tone_duration+pad_duration)

#     # import plot
#     # plot.raster(tones_and_pads).show()

#     if remove_pads:
#         tones_and_pads = trim(tones_and_pads, 0, tone_duration)

#     return silence, tones_and_pads

# split_and_fold = split_and_fold_trains
