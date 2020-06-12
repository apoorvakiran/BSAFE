# -*- coding: utf-8 -*-
"""
This script serves to analyze the acceleration.

For position computation look at:
http://www.chrobotics.com/library/accel-position-velocity

@ author Jesper Kristensen
Copyright 2018
"""

__author__ = "Jesper Kristensen"
__version__ = "Alpha"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

__all__ = ["do_acceleration_analysis", "do_angular_velocity"]


def do_acceleration_analysis(experiments=None, filename=None):
    """
    Perform acceleration analysis.

    :param experiments:
    :return:
    """

    plt.figure(1001)
    plt.figure(1002)
    plt.figure(1004)
    plt.figure(1006)
    plt.figure(2000)
    for exp_ix, exp in enumerate(experiments):

        ax = exp.ax(loc="hand")
        ay = exp.ay(loc="hand")
        az = exp.az(loc="hand")

        ax = ax.iloc[5000:]
        ay = ay.iloc[5000:]
        az = az.iloc[5000:]

        ax = ax - ax.mean()
        ay = ay - ay.mean()
        az = az - az.mean()

        # convert to m/s^2:
        ax *= 32
        ay *= 32
        az *= 32

        a = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)  # subtract 1g (base acceleration of 1g)

        # plt.hist(a, label=exp.name, alpha=0.8)

        # start at zero velocity:
        dt = 0.4
        velocity_x = []
        vx0 = 0
        vx = vx0
        for ix, j in ax.to_frame().iterrows():
            velocity_x.append(vx)
            vx = vx0 + j.values[0] * dt  # dt [s]
            vx0 = vx
        velocity_x = np.asarray(velocity_x)
        velocity_x = pd.DataFrame(data=velocity_x.T, columns=["vx"])

        dt = 0.4
        velocity_y = []
        vy0 = 0
        vy = vy0
        for ix, j in ay.to_frame().iterrows():
            velocity_y.append(vy)
            vy = vy0 + j.values[0] * dt  # dt [s]
            vy0 = vy
        velocity_y = np.asarray(velocity_y)
        velocity_y = pd.DataFrame(data=velocity_y.T, columns=["vy"])

        dt = 0.4
        velocity_z = []
        vz0 = 0
        vz = vz0
        for ix, j in az.to_frame().iterrows():
            velocity_z.append(vz)
            vz = vz0 + j.values[0] * dt  # dt [s]
            vz0 = vz
        velocity_z = np.asarray(velocity_z)
        velocity_z = pd.DataFrame(data=velocity_z.T, columns=["vz"])

        plt.figure(1001)
        plt.subplot(321)
        plt.plot(ax, label=exp.name)
        plt.ylabel("$a_x$ [ft/s^2]")
        plt.grid()
        plt.legend(loc="best")
        plt.subplot(322)
        plt.plot(velocity_x)
        plt.ylabel("$v_x$ [ft/s]")
        plt.grid()
        plt.subplot(323)
        plt.plot(ay)
        plt.ylabel("$a_y$ [ft/s^2]")
        plt.grid()
        plt.subplot(324)
        plt.plot(velocity_y)
        plt.ylabel("$v_y$ [ft/s]")
        plt.grid()
        plt.subplot(325)
        plt.plot(az)
        plt.ylabel("$a_z$ [ft/s^2]")
        plt.grid()
        plt.subplot(326)
        plt.plot(velocity_z)
        plt.ylabel("$v_z$ [ft/s]")
        plt.grid()
        plt.tight_layout()

        velocity = np.sqrt(np.add(np.add(velocity_x ** 2, velocity_y ** 2), velocity_z ** 2))

        if exp.name == "A":
            velocity = velocity.iloc[:6500]
        elif exp.name == "B":
            velocity = velocity.iloc[:10000]

        coeff = np.polyfit(velocity.index, velocity.values, deg=1)
        mean = np.polyval(coeff, velocity.index)

        velocity_osc = velocity.values - mean.reshape(-1, 1)

        plt.figure(1002)
        # plt.subplot(211)
        plt.plot(velocity, label=exp.name)
        plt.plot(velocity.index, mean, label="fit")
        plt.xlabel("time [.]")
        plt.ylabel("v(t) [ft/s]")
        plt.grid("on")
        plt.legend(loc="best")

        plt.figure(1004)
        # plt.plot(velocity_osc, 'b-')
        plt.hist(np.abs(velocity_osc) / np.abs(velocity_osc).max() * 96, bins=20)
        plt.grid("on")
        plt.xlabel("speed")
        plt.ylabel("count")
        plt.axvline(0, linestyle="--", color="k")
        plt.axvline(25, linestyle="--", color="k")
        plt.axvline(50, linestyle="--", color="k")
        plt.axvline(75, linestyle="--", color="k")
        plt.savefig("velocity_{}.png".format(exp.name))

        # Get position:

        coeff_x = np.polyfit(velocity_x.index, velocity_x.values, deg=1)
        vx_less_mean = velocity_x - np.polyval(coeff_x, velocity_x.index).reshape(-1, 1)
        vx_less_mean = vx_less_mean / np.max(np.abs(vx_less_mean)) * 100

        coeff_y = np.polyfit(velocity_y.index, velocity_y.values, deg=1)
        vy_less_mean = velocity_y - np.polyval(coeff_y, velocity_y.index).reshape(-1, 1)
        vy_less_mean = vy_less_mean / np.max(np.abs(vy_less_mean)) * 100

        coeff_z = np.polyfit(velocity_z.index, velocity_z.values, deg=1)
        vz_less_mean = velocity_z - np.polyval(coeff_z, velocity_z.index).reshape(-1, 1)
        vz_less_mean = vz_less_mean / np.max(np.abs(vz_less_mean)) * 100

        dt = 0.4
        position_x = []
        rx0 = 0
        rx = rx0
        for ix, j in vx_less_mean.iterrows():
            position_x.append(rx)
            rx = rx0 + j.values[0] * dt  # dt [s]
            rx0 = rx
        position_x = np.asarray(position_x)
        position_x = pd.DataFrame(data=position_x.T, columns=["rx"])

        plt.figure(1006)
        if exp.name == "A":
            vals1 = np.tile(position_x / np.max(np.abs(position_x)) * 4, (4, 1))
            vals2 = np.tile(position_x / np.max(np.abs(position_x)) * 2, (2, 1))
            vals3 = np.tile(position_x / np.max(np.abs(position_x)) * 1, (6, 1))
            vals4 = np.tile(position_x / np.max(np.abs(position_x)) * 4, (4, 1))
        else:
            vals1 = np.tile(position_x / np.max(np.abs(position_x)) * 2, (2, 1))
            vals2 = np.tile(position_x / np.max(np.abs(position_x)) * 4, (6, 1))
            vals3 = np.tile(position_x / np.max(np.abs(position_x)) * 1, (2, 1))
            vals4 = np.tile(position_x / np.max(np.abs(position_x)) * 4, (6, 1))

        plt.plot(np.r_[vals1, vals2, vals3, vals4])
        plt.grid("on")
        plt.xlabel("time [.]")
        plt.ylabel("position")
        # plt.show()
        plt.savefig("position_{}.png".format(exp.name))

        position_x_modified = np.r_[vals1, vals2, vals3, vals4][: len(ax)]
        ax = ax.reset_index(drop=True)
        # position_x = position_x_modified.reset_index(drop=True)
        work_per_unit_mass = np.multiply(ax.values.reshape(-1, 1), position_x_modified.reshape(-1, 1))

        plt.figure(2000)

        plt.subplot("{}".format(int("".join(list(map(str, [2, 1, exp_ix + 1]))))))
        if exp_ix == 0:
            plt.plot(work_per_unit_mass / 100, "b")
        else:
            plt.plot(work_per_unit_mass / 100, "orange")
        plt.grid("on")
        plt.xlabel("time [.]")
        plt.ylabel("work/mass")
        # plt.show()

        # import pdb
        # pdb.set_trace()

        # import pdb
        # pdb.set_trace()

    plt.figure(2000)
    plt.savefig("work_{}.png".format(exp.name))
    # plt.show()

    import pdb

    pdb.set_trace()

    if filename is None:
        filename = "acceleration.png"
    plt.savefig(filename, format="png")

    # plt.show()


def do_angular_velocity(experiments=None, filename=None):
    """
    Perform acceleration analysis.

    :param experiments:
    :return:
    """

    plt.figure()
    for exp in experiments:

        gx = exp.gx(loc="hand")
        gy = exp.gy(loc="hand")
        gz = exp.gz(loc="hand")
        g = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)

        plt.hist(g, label=exp.name)

    # plt.title('worker {}'.format(exp.name))
    # plt.axvline(-0.5, linestyle='--', color='r')
    # plt.axvline(-1, linestyle='--', color='r')
    plt.axvline(0, linestyle="--", color="k")
    plt.axvline(90, linestyle="--", color="r")
    plt.axvline(180, linestyle="--", color="r")
    plt.axvline(270, linestyle="--", color="r")
    plt.axvline(360, linestyle="--", color="r")
    plt.grid("on")
    plt.xlabel("angular velocity $\omega$(t) [dps]")
    plt.ylabel("count")
    plt.legend(loc="best")

    if filename is None:
        filename = "angular_velocity.png"
    # plt.savefig(filename, format='png')

    plt.show()
