# -*- coding: utf-8 -*-
"""
This script plots files from Iterate Lab's Data Store.

This is called with "dplot":
    >> "dplot <tester> <project> <store plots here>"

This script plots the latest data file uploaded by
"tester" under "project".

@ author Jesper Kristensen
Iterate Labs Inc. Copyright 2018-
"""

__author__ = "Jesper Kristensen"
__copyright__ = "Copyright (C) 2018- Iterate Labs, Inc."
__version__ = "Alpha"

import os
import sys
import matplotlib.pyplot as plt
from ergo_analytics.data_raw import LoadDataStore


if __name__ == '__main__':
    
    # parse command line:
    if not len(sys.argv) == 4:
        raise Exception("Usage: dsplot <tester> <project> <store plots here>")
    
    # parse the user input - selecting which tester and project to use:
    tester = sys.argv[1]
    project = sys.argv[2]
    store_plots_here = sys.argv[3]

    ds = LoadDataStore()
    raw_df = ds.load(tester=tester, project=project)

    # assume in data format 5:
    if not os.path.isdir(store_plots_here):
        os.makedirs(store_plots_here)
    
    raw_df.dropna(how='all', inplace=True)

    # create the various plots:

    # first for Wrist:
    plt.plot(raw_df.iloc[:, 1], 'b-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(f'Yaw[0] wrist\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "wrist_yaw.png"))
    plt.close()

    plt.plot(raw_df.iloc[:, 2], 'b-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Pitch[0] wrist\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "wrist_pitch.png"))
    plt.close()

    plt.plot(raw_df.iloc[:, 3], 'b-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Roll[0] wrist\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "wrist_roll.png"))
    plt.close()

    # then for Hand:
    plt.plot(raw_df.iloc[:, 4], 'g-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Yaw[1] hand\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "hand_yaw.png"))
    plt.close()

    plt.plot(raw_df.iloc[:, 5], 'g-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Pitch[1] hand\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "hand_pitch.png"))
    plt.close()

    plt.plot(raw_df.iloc[:, 6], 'g-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Roll[1] hand\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "hand_roll.png"))
    plt.close()

    # now the Delta's:
    plt.plot(raw_df.iloc[:, 1] - raw_df.iloc[:, 4], 'r-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Delta Yaw\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "delta_yaw.png"))
    plt.close()

    plt.plot(raw_df.iloc[:, 2] - raw_df.iloc[:, 5], 'r-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Delta Pitch\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "delta_pitch.png"))
    plt.close()

    plt.plot(raw_df.iloc[:, 3] - raw_df.iloc[:, 6], 'r-')
    plt.xlabel("Index/Time")
    plt.ylabel("Degrees")
    plt.grid()
    plt.title(
        f'Delta Roll\nfrom ({raw_df.iloc[0][0]}) to ({raw_df.iloc[-1][0]})')
    plt.savefig(os.path.join(store_plots_here, "delta_roll.png"))
    plt.close()
