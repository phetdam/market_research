# contains basic implementation of a cox-ingersol-ross single-factor short rate model
# https://en.wikipedia.org/wiki/Cox-Ingersoll-Ross_model
#
# Changelog:
#
# 10-24-2018
#
# initial creation; git commit. renamed to cir_main.py, modified usage, cleaned a little

# program name
PROGNAME = "cir_main"

# help flag
HELP_FLAG = "--help"

# help string
HELP_STR = ("Usage: {0}\n       {0} {1}\n"
            "simulates a single run of two CIR processes.".format(PROGNAME, HELP_FLAG)
    )

# default file to save to
DEFAULT_F = "cir.png"

# indicates how many cir processes have been generated
CIR_COUNT = 0

# configurations for cir; list [a, mu, dt, sigma, n]
CIR_PARAM = [0.03, 0.1, 0.001, 0.07, 1000]

# import matplotlib; catch exception
try:
    import matplotlib.pyplot as plt
except:
    print("{}: please install matplotlib.".format(PROGNAME))
    quit()
# import math lib and sys
import math
import sys
# import pandas and numpy
import pandas as pd
import numpy as np
# import cir
import cir

# main
if (__name__ == "__main__"):
    # get length of arguments in the argv vector
    argc = len(sys.argv)
    # if there is only one argument, run with some default values
    if (argc == 1):
        # figure size width 6', height 4.5'
        fg = plt.figure(figsize = (12, 9))
        # get x (t) and y (r) series of cir process; element 0 is time series, 1 is r
        x1, y1 = cir.return_cir(*CIR_PARAM, cc = CIR_COUNT, df = False)
        # plot the two series (x1, y1 and x2, y2)
        # configurations for cir; list [a, mu, dt, sigma, n]
        plt.plot(x1, y1, label = "cir_{0}(a={1}, mu={2}, dt={3}, sigma={4}, n={5})".format(
            CIR_COUNT, *CIR_PARAM))
        # increment CIR_COUNT
        CIR_COUNT += 1
        # get x (t) and y (r) series of cir process; element 0 is time series, 1 is r
        # we do this second one just for comparison reasons; plot
        x2, y2 = cir.return_cir(*CIR_PARAM, cc = CIR_COUNT, df = False)
        plt.plot(x2, y2, label = "cir_{0}(a={1}, mu={2}, dt={3}, sigma={4}, n={5})".format(
            CIR_COUNT, *CIR_PARAM))
        # increment CIR_COUNT
        CIR_COUNT += 1
        # x label, y label (mmake vertical)
        plt.xlabel("t")
        plt.ylabel("r", rotation = 0)
        # graph title
        plt.title("CIR process")
        # show legend
        plt.legend()
        # save to file
        plt.savefig(DEFAULT_F)
    # else if there are two arguments
    elif (argc == 2):
        # if it is the help option
        if (sys.argv[1] == HELP_FLAG):
            print(HELP_STR)
            quit()
    # else too many arguments
    else:
        print("{0}: too many arguments. type '{0} {1}' for usage.".format(PROGNAME, HELP_FLAG))
        quit()
