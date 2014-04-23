#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

__author__ = "Marek Rudnicki"

import numpy as np

from mrlib.thorns import spikes
from mrlib.thorns import calc

GOLDEN = 1.6180339887


def plot_neurogram(spike_trains, fs, ax=None, **kwargs):

    neurogram = spikes.trains_to_array(
        spike_trains,
        fs
    )

    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()

    extent = (
        0,                       # left
        neurogram.shape[0] / fs, # right
        0,                       # bottom
        neurogram.shape[1]       # top
    )

    ax.imshow(
        neurogram.T,
        aspect='auto',
        extent=extent,
        **kwargs
    )

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Channel number")

    return ax




def plot_raster(spike_trains, ax=None, style='k.', **kwargs):
    """Plot raster plot."""

    trains = spike_trains['spikes']
    duration = np.max( spike_trains['duration'] )

    # Compute trial number
    L = [ len(train) for train in trains ]
    r = np.arange(len(trains))
    n = np.repeat(r, L)

    # Spike timings
    s = np.concatenate(tuple(trains))


    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()

    ax.plot(s, n, style, **kwargs)
    ax.set_xlabel("Time [s]")
    ax.set_xlim( (0, duration) )
    ax.set_ylabel("Trial Number")
    ax.set_ylim( (-0.5, len(trains)-0.5) )


    return ax





def plot_psth(spike_trains, bin_size, ax=None, **kwargs):
    """Plots PSTH of spike_trains."""


    psth, bin_edges = calc.psth(
        spike_trains,
        bin_size
    )


    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()


    ax.plot(
        bin_edges[:-1],
        psth,
        drawstyle='steps-post',
        **kwargs
    )


    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Spikes per Second")


    return ax


# def isih(spike_trains, bin_size=1e-3, plot=None, **style):
#     """Plot inter-spike interval histogram."""

#     hist = stats.isih(spike_trains, bin_size)

#     c = biggles.Histogram(hist, x0=0, binsize=bin_size)
#     c.style(**style)

#     if plot is None:
#         plot = biggles.FramedPlot()
#     plot.xlabel = "Inter-Spike Interval [ms]"
#     plot.ylabel = "Probability Density Function"
#     plot.add(c)
#     plot.xrange = (0, None)
#     plot.yrange = (0, None)

#     return plot


def plot_period_histogram(
        spike_trains,
        freq,
        nbins=64,
        ax=None,
        style='',
        density=False,
        **kwargs
):
    """Plot period histogram of the given spike trains.

    Parameters
    ----------
    spike_trains : spike_trains
        Spike trains for plotting.
    freq : float
        Stimulus frequency.
    nbins : int
        Number of bins for the histogram.
    ax : plt.Ax, optional
        Matplotlib Ax to plot on.
    style : str, optional
        Plotting style (See matplotlib plotting styles).
    density : bool, optional
        If False, the result will contain the number of samples in
        each bin. If True, the result is the value of the probability
        density function at the bin, normalized such that the integral
        over the range is 1. (See `np.histogram()` for reference)


    Returns
    -------
    plt.Axis
        Matplotlib axis containing the plot.

    """

    hist, bin_edges = calc.period_histogram(
        spike_trains,
        freq=freq,
        nbins=nbins,
        density=density
    )



    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca(polar=True)


    ax.fill(
        bin_edges[:-1],
        hist,
        style,
        **kwargs
    )

    # ax.plot(
    #     bin_edges[:-1],
    #     hist,
    #     style,
    #     **kwargs
    # )


    ax.set_xlabel("Stimulus Phase")
    # ax.set_ylabel("Probability Density Function")

    return ax



def plot_sac(
        spike_trains,
        coincidence_window=50e-6,
        analysis_window=5e-3,
        normalize=True,
        ax=None,
        style='k-',
        **kwargs
):
    """Plot shuffled autocorrelogram (SAC) (Joris 2006)"""

    sac, bin_edges = calc.sac(
        spike_trains,
        coincidence_window=coincidence_window,
        analysis_window=analysis_window,
        normalize=normalize
    )


    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()


    ax.plot(
        bin_edges[:-1],
        sac,
        style,
        drawstyle='steps-post',
        **kwargs
    )


    ax.set_xlabel("Delay [s]")
    ax.set_ylabel("Normalized Number of Coincidences")

    return ax



def plot_signal(signal, fs=None, ax=None):
    """Plot time signal.

    Parameters
    ----------
    signal : array_like
        Time signal.
    fs : float, optional
        Sampling freuency of the signal.


    Returns
    -------
    plt.Axis
       Matplotlib Axis with the plot.

    """

    if ax is None:
        import matplotlib.pyplot as plt
        ax = plt.gca()


    if fs is None:
        fs = 1


    t = np.arange(len(signal)) / fs


    ax.set_xlim((t[0],t[-1]))


    ax.plot(t, signal)

    return ax