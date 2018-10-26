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
# 10-26-2018
#
# made modification to return_cir(); if r ever drops below 0, r will be forcibly
# corrected back to 0. this is due to r sometimes becoming ever so slightly negative
# with some data such as those of treasury bills, where rates were slightly negative
# for a short file.
#
# 10-25-2018
#
# added note about normally-distributed nature of model; added function calibrate_cir
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
        # if r < 0, set it back to 0; cir processes cannot deal with negative rates
        if (r < 0):
            r = 0
    # if df is True, wrap in dataframe and return (label as cir_(cc))
    if (df == True):
        return pd.DataFrame(index = x, data = y, columns = ["cir_{}".format(cc)])
    # else return ndarrays as a tuple
    return (x, y)

# cir calibrating function
# given a time series (preferred is a pandas series or ndarray), assume process is normal
# and then find the sample mean (mu), sample stddev (sigma), no. elements (n; can be
# scaled with parameter n_scale which is 1 by default), speed of mean reversion (a), and
# default timestep (dt; can be scaled with parameter dt_scale which is 1 by default);
# returns list [a, mu, dt, sigma, n]
def calibrate_cir(ts, dt_scale = 1, n_scale = 1):
    # forcibly convert data to numeric data
    ts = pd.to_numeric(ts, errors = "coerce")
    # total number of indices (also the n we will return)
    n = ts.size
    # get sample mean, ignoring NaN values (note the total values used in this calculation
    # will be certainly <= n)
    mu = np.nanmean(ts)
    # get sample standard deviation
    sigma = np.nanstd(ts)
    # calculate dt; by default dt is 1 / n (can multiply by dt_scale)
    dt = dt_scale / n
    # calcuate a: a = 1 / (sum(i = 0, j - 1: t_i)) * (j - 1), where t_i is the time to
    # mean reversion for each interval of mean reversion
    # number of intervals
    j = 0
    # number of units in interval
    t_i = 0
    # a (speed of mean reversion)
    a = 0
    # current level of rate
    cr = ts[0]
    # previous level of rate
    pr = ts[0]
    # for each element in ts, starting from first
    for i in range(1, n):
        # get current rate; can be np.nan
        cr = ts[i]
        # increment t_i
        t_i += 1
        # if the mean reversion interval has elapsed (cr cannot be NaN)
        if (not math.isnan(cr) and ((cr < mu and pr > mu) or (cr > mu and pr < mu))):
            # increment number of mean reversion intervals
            j += 1
            # add t_i to a
            a += t_i
            # reset t_i to 0
            t_i = 0
            # assign value of cr to pr
            pr = cr
    # calculate a (use sample average to correct for sample, and decrease reversion speed)
    a = (j - 1) / a
    # return [a, mu, dt, sigma, n * n_scale] (n is scaled by n_scale)
    return [a, mu, dt, sigma, n * n_scale]

# main
if (__name__ == "__main__"):
    print("{}: do not run in standalone mode.".format(PROGNAME))
    quit(1)
