# -*- coding: utf-8 -*-
"""This script plots files from Iterate Lab's Data Store.

Typical usage example:
>> dplot --tester <tester> --project <project> --store-here <store plots here>

The script can plot either the latest file only or all files associated with
the particular project.

@ author Jesper Kristensen
Iterate Labs Inc. Copyright 2018-
All rights reserved
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import argparse
import matplotlib.pyplot as plt
import os
import sys

from ergo_analytics.data_raw import LoadDataStore


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=('Welcome to Iterate Lab Inc.\'s '
                     'Data-Store Plotting tool.'),
        epilog="Please contact 'jesper.kristensen@iteratelabs.co' "
               "if any questions.", prog="dplot")

    parser.add_argument('--tester', required=True,
                        help='Project tester - which tester to use?')
    parser.add_argument('--project', required=True,
                        help='Project name - which project name to use?')
    parser.add_argument('--store-here', required=False,
                        help='Path to plots - where to store the plots?')
    # Should all files related to this project ID be plotted?
    parser.add_argument('--all', required=False, action='store_true',
                        help='Plot all files for this tester and project?')

    # start by parsing what the user wants to do:
    try:
        args = parser.parse_args()
    except Exception:
        # print help and exit:
        parser.print_help()
        sys.exit(0)

    # make the names better:
    tester = args.tester
    project = args.project
    plot_all = args.all
    store_plots_here = args.store_here

    if store_plots_here is None:
        store_plots_here = '~/plots'

    store_plots_here = os.path.abspath(os.path.expanduser(store_plots_here))

    if os.path.isdir(store_plots_here) and \
            input("Plots folder '{}' already exists... "
                  "overwrite? ".format(store_plots_here)) in ['n', 'N',
                                                             'no', 'No', 'NO']:
        raise Exception("Plots folder '{}' "
                        "already exists!".format(store_plots_here))

    # we have parsed the input - let's go:
    ds = LoadDataStore()

    num_files = 0
    for ix, (raw_df, s3_filename) in enumerate(ds.load(tester=tester,
                                            project=project, all=plot_all)):

        filename = "{}_{}".format(ix + 1, s3_filename.replace('/', '_'))
        plot_path = os.path.join(store_plots_here, filename)

        print("Plotting file {} in {}...".format(ix + 1, plot_path))

        # assume in data format 5:
        if not os.path.isdir(plot_path):
            os.makedirs(plot_path)

        raw_df.dropna(how='all', inplace=True)

        # create the various plots:

        # first for Wrist:
        plt.plot(raw_df.iloc[:, 1], 'b-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(f'Yaw[0] wrist\nfrom ({raw_df.iloc[0][0]}) to '
                  f'({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "wrist_yaw.png"))
        plt.close()

        plt.plot(raw_df.iloc[:, 2], 'b-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Pitch[0] wrist\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "wrist_pitch.png"))
        plt.close()

        plt.plot(raw_df.iloc[:, 3], 'b-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Roll[0] wrist\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "wrist_roll.png"))
        plt.close()

        # then for Hand:
        plt.plot(raw_df.iloc[:, 4], 'g-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Yaw[1] hand\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "hand_yaw.png"))
        plt.close()

        plt.plot(raw_df.iloc[:, 5], 'g-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Pitch[1] hand\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "hand_pitch.png"))
        plt.close()

        plt.plot(raw_df.iloc[:, 6], 'g-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Roll[1] hand\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "hand_roll.png"))
        plt.close()

        # now the Delta's:
        plt.plot(raw_df.iloc[:, 1] - raw_df.iloc[:, 4], 'r-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Delta Yaw\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "delta_yaw.png"))
        plt.close()

        plt.plot(raw_df.iloc[:, 2] - raw_df.iloc[:, 5], 'r-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Delta Pitch\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "delta_pitch.png"))
        plt.close()

        plt.plot(raw_df.iloc[:, 3] - raw_df.iloc[:, 6], 'r-')
        plt.xlabel("Index/Time")
        plt.ylabel("Degrees")
        plt.grid()
        plt.title(
            f'Delta Roll\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
        plt.savefig(os.path.join(plot_path, "delta_roll.png"))
        plt.close()

        num_files += 1

    print("Plotted {} files.".format(num_files))
    print("All done!")
