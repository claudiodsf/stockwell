#!/usr/bin/env python
"""
Time-frequency plot of seismic traces.

:copyright:
    2011-2021 Maria Lancieri <maria.lancieri@irsn.fr>,
              Claudio Satriano <satriano@ipgp.fr>
:license:
    CeCILL Free Software License Agreement, Version 2.1
    (http://www.cecill.info/index.en.html)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import os
try:
    from obspy import read, Trace
except Exception:
    sys.stderr.write(
        'ObsPy is required to run this script. Please install it and retry.\n'
        'Installation instructions on https://obspy.org.\n')
    sys.exit(1)
from optparse import OptionParser
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
try:
    from stockwell.lib import st
except Exception:
    from lib import st

# define ipshell(), if possible
if sys.stdout.isatty():
    try:
        import IPython
        IP_VERSION = tuple(map(int, IPython.__version__.split('.')[:3]))
        len(IP_VERSION) > 2 or IP_VERSION.append(0)
        if IP_VERSION < (0, 11, 0):
            from IPython.Shell import IPShellEmbed
            ipshell = IPShellEmbed()
        if (0, 11, 0) <= IP_VERSION < (1, 0, 0):
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            ipshell = InteractiveShellEmbed()
        elif IP_VERSION >= (1, 0, 0):
            from IPython.terminal.embed import InteractiveShellEmbed
            ipshell = InteractiveShellEmbed()
    except ImportError:
        ipshell = None
else:
    ipshell = None

save_stockwell = False


def main():
    usage = 'usage: %prog [options] sac_file(s)'

    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--maxfreq', dest='maxfreq', action='store',
                      type='float', default=None,
                      help='Maximum frequency (hz) to calculate the '
                           'S-transform. If not specified, Nyquist '
                           'frequence is used')
    parser.add_option('-d', '--downsample', dest='downsample',
                      action='store_true', default=False,
                      help='Downsample data if the Nyquist is higher than '
                           'the max frequency')
    parser.add_option('-r', '--reffiled', dest='reffield', action='store',
                      default=None,
                      help='Reference (zero) field for plotting and/or '
                           'cutting traces')
    parser.add_option('-s', '--startcut', dest='startcut', action='store',
                      type='float', default=None,
                      help='Cut start time (in sec) respect to '
                           'reference field')
    parser.add_option('-e', '--endcut', dest='endcut', action='store',
                      type='float', default=None,
                      help='Cut end time (in sec) respect to reference field')
    parser.add_option('-f', '--factor', dest='decimation_factor',
                      action='store', type='int', default=1,
                      help='Factor for decimating the S-transform graph. '
                           '(Useful to speed-up plotting)')
    parser.add_option('-a', '--ascii', dest='ascii', action='store_true',
                      default=False,
                      help='Data file is in ascii format (two columns, '
                           'time/amplitude)')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_usage(file=sys.stderr)
        sys.stderr.write("\tUse '-h' for help\n\n")
        sys.exit(1)

    for sacfile in args:
        print(sacfile)

        if options.ascii:
            data = np.loadtxt(sacfile)
            time = data[:, 0]
            amplitude = data[:, 1]
            tr = Trace(amplitude)
            tr.stats.delta = time[1] - time[0]
        else:
            try:
                tr, = read(sacfile, format='SAC')
            except Exception as message:
                print(message)
                next

        # Calculate nyquist and do downsampling, if required
        stats = tr.stats
        delta = stats.delta
        fny = 1. / (2*delta)
        if options.maxfreq:
            if fny > options.maxfreq:
                if options.downsample:
                    newdelta = fny/options.maxfreq * delta
                    dsample = int(np.floor(newdelta/delta))
                    delta = delta * dsample
                    fny = 1./(2*delta)
                    tr.decimate(factor=dsample)
                else:
                    fny = options.maxfreq

        # Cut data, if required
        if options.startcut:
            if not options.reffield:
                sys.stderr.write('Error: you must specify a reference field '
                                 '(option -r)\n')
                sys.exit(1)
            if not options.endcut:
                sys.stderr.write('Error: you must specify a end cut time '
                                 '(option -e)\n')
                sys.exit(1)

            tstart = stats.starttime + stats.sac[options.reffield] -\
                stats.sac.b + options.startcut
            tend = tstart + options.endcut
            print(tstart, tend, stats.sac.b, stats.sac.a)
            tr.trim(tstart, tend)
            #stats.sac[options.reffield] = stats.sac.b - options.startcut
            #stats.sac.b = 0

        data = tr.data

        # remove mean
        data -= data.mean()
        # normalize trace
        norm = np.max((data.max(), -data.min()))
        data /= norm

        df = 1/(delta*len(data))  # frequency step
        low = 0  # lowest frequency for the S-Transform
        nfreq = int(np.ceil(fny/df))  # number of discrete frequencies

        # Stockwell file name
        basename = os.path.basename(sacfile)
        stock_file_name = basename + '.stock.npy'

        # If we have a transform saved to disk, we don't recalculate it
        try:
            stock = np.load(stock_file_name)
            print('File %s loaded' % stock_file_name)
        except Exception:
            #Stockwell transform
            stock = st.st(data, low, nfreq)
            stock = np.flipud(stock)
            #Save transform to disk
            if save_stockwell:
                np.save(stock_file_name, stock)

        #if stockwell_stack == None:
        #    stockwell_stack = stock
        #else:
        #    stockwell_stack += stock

        reftime = 0
        if options.reffield:
            try:
                reftime = stats.sac[options.reffield] - stats.sac.b
            except Exception as message:
                sys.stderr.write(message)

        plot_stockwell(data, delta, reftime, stock, df, sacfile,
                       options.decimation_factor)


def plot_stockwell(data, delta, reftime, stock, df, sacfile, decimate=1):
    #Get dir names
    basename = os.path.basename(sacfile)
    dirname = os.path.basename(os.path.dirname(os.path.abspath(sacfile)))

    time = np.arange(len(data)) * delta
    time -= reftime

    stock_dec = stock[0::decimate, 0::decimate]
    #data_dec = data[0::decimate]
    nfreqs, ntimes = np.shape(stock_dec)
    delta *= decimate
    df *= decimate

    time_dec = np.arange(ntimes) * delta
    time_dec -= reftime

    freq = []
    for i_freq in range(nfreqs):
        freq.append(i_freq*df)

    fig = plt.figure(figsize=(20, 13))
    ax0 = fig.add_subplot(211)
    ax0.plot(time, data, 'k')
    ax0.axis('tight')
    ax0.set_xlim(min(time), max(time))
    ax0.set_xlabel('Time (s)')
    ax0.set_ylabel('Amplitude')
    ax0.set_title('%s\n%s' % (dirname, basename))

    ax1 = fig.add_subplot(212)

    # center bin
    halfbin_time = delta/2.
    halfbin_freq = df/2.

    # pcolor expects one bin more at the right end
    #freq = np.concatenate((freq, [freq[-1] + 2 * halfbin_freq]))
    #time = np.concatenate((time, [time[-1] + 2 * halfbin_time]))
    # center bin
    #time -= halfbin_time
    #freq -= halfbin_freq
    #X, Y = np.meshgrid(time, freq)
    #ax1.pcolor(X, Y, np.abs(stock), cmap=cm.jet)
    #ax1.pcolorfast(X, Y, np.abs(stock), cmap=cm.jet)
    #ax1.semilogy()

    cmap = plt.cm.jet
    #cmap = cm.Spectral
    cmap = plt.cm.Paired

    extent = (time_dec[0] - halfbin_time, time_dec[-1] + halfbin_time,
              freq[0] - halfbin_freq, freq[-1] + halfbin_freq)
    colorplot = ax1.imshow(np.abs(stock_dec), interpolation='nearest',
                           extent=extent, cmap=cmap)

    ax1.axis('tight')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Frequency (Hz)')
    ax1.grid(False)

    # fig.colorbar(colorplot)

    outfile = '%s.pdf' % basename
    print(outfile)

    fig.savefig(outfile, format='pdf')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
