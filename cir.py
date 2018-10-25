# basic implementation of a cox-ingersol-ross single-factor short rate model
# https://en.wikipedia.org/wiki/Cox-Ingersoll-Ross_model
#
# implementation of model (differential changes in r are assumed normal):
#
# dr = a * (mu - r) * dt + sigma * math.sqrt(r) * np.random.normal() * math.sqrt(dt)
# we assume that dW is driven by z * sqrt(dt), where z ~ N(0, 1)
#
# Changelog:
#
# 10-25-2018
#
# added note about normally-distributed nature of model
#
# 10-24-2018
#
# split off from cir_main.py (the original cir.py) into standalone file

# import math, pandas, numpy (assume latter two exist)
import math
import pandas as pd
import numpy as np

# program name
PROGNAME = "cir"

# cir generating function
# driven by sigma, with a to govern speed of mean reversion, while mu establishes the mean
# dt is the differential timestep, and n is the number of times to loop
# by default, returns dataframe, but if df = False, will return tuple of ndarrays (x, y)
# unless specified otherwise, will always assume the cir process it returns is the first
# one being created (can specify number with cc = x)
def return_cir(a, mu, dt, sigma, n, cc = 0, df = True):
    # starting point of r assumed to be mu
    r = mu
    # differential change of r dr starts as 0
    dr = 0
    # np array for the x axis (time)
    x = np.linspace(0, n - 1, n)
    # np array for the y axis (r)
    y = np.empty(n)
    # for n iterations
    for i in range(n):
        # insert r as value in np array
        y[i] = r
        # calculate dr
        dr = a * (mu - r) * dt + sigma * math.sqrt(r) * np.random.normal() * math.sqrt(dt)
        # add change of dr to r
        r += dr
    # if df is True, wrap in dataframe and return (label as cir_(cc))
    if (df == True):
        return pd.DataFrame(index = x, data = y, columns = ["cir_{}".format(cc)])
    # else return ndarrays as a tuple
    return (x, y)

# main
if (__name__ == "__main__"):
    print("{}: do not run in standalone mode.".format(PROGNAME))
    quit(1)
