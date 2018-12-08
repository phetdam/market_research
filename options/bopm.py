# contains method for pricing options using the binomial tree approach. note that all
# parameters have to be constant; for stochastic approach, which requires a stochastic
# process for the underlying as well, refer to stochastic_option (doesn't exist yet)
#
# Changelog:
#
# 12-08-2018
#
# initial creation. currently generates european and american options prices. issues:
# prices are usually ~$0.10 cheaper than those in the original cox/ross/rubenstein
# paper. not sure of problem root; dt scaling is appropriate. changed name of method
# to option_price.
#

import math
import numpy as np

# library name
LIB_NAME = "bopm"

# function names
OPTION_PRICE_N = "option_price"

# allowable option types
__option_types = ["call", "put"]

# allowable option flavors
__option_flavors = ["american", "european"]

# implementation of the binomial call option pricing model. uses the original
# cox/ross/rubenstein binomial tree method. time step assumed to be one 1 day.
#
# parameters:
#
# S_        price of underlying at time 0.
# sigma     constant underlying volatility of S
# r         constant risk free rate
# q         constant dividend (or other) yield
# K         strike price of the option
# T_        no. months until expiration; month/year standard is 30/360
# is_type   "call", "put" (default "call")
# flavor    style of option: can be "american", "european" (default "european")
#
# returns the price of the option at time 0 (now)
def option_price(S_, sigma, r, K, T_, q = 0, is_type = "call", flavor = "european"):
    # cannot have negative underlying price
    if (S_ < 0):
        raise ValueError("{0}.{1}: error: initial underlying price cannot be "
                         "negative".format(LIB_NAME, OPTION_PRICE_N))
    # cannot have negative volatility
    if (sigma < 0):
        raise ValueError("{0}.{1}: error: volatility of underlying cannot be "
                         "negative".format(LIB_NAME, OPTION_PRICE_N))
    # warning if negative risk-free rate is passed
    if (r < 0):
        print("{0}.{1}: warning: negative risk-free rate".format(LIB_NAME,
                                                                 OPTION_PRICE_N))
    # cannot have negative strike price
    if (K < 0):
        raise ValueError("{0}.{1}: error: strike price cannot be negative".format(
            LIB_NAME, OPTION_PRICE_N))
    # cannot have negative T_
    if (T_ < 0):
        raise ValueError("{0}.{1}: error: cannot have negative time to expiration".format(
            LIB_NAME, OPTION_PRICE_N))
    # if is_type is not in __option_types
    if (is_type not in __option_types):
        raise ValueError("{0}.{1}: error: option type can only be {2}".format(
            LIB_NAME, OPTION_PRICE_N, __option_types))
    # if flavor is not in __option_flavors
    if (flavor not in __option_flavors):
        raise ValueError("{0}.{1}: error: option flavor can only be {2}".format(
            LIB_NAME, OPTION_PRICE_N, __option_flavors))
    # number of days until option expiration is 30 * T_
    n = 30 * T_
    # if n is fractional, print error and exit
    if (int(n) != float(n)):
        raise ValueError("{0}.{1}: error: cannot have fractional number of days to "
                         "expiration".format(LIB_NAME, OPTION_PRICE_N))
    # size of time step is equal to one day; units must be in years)
    dt = 1 / 360
    # number of final nodes for option values is n + 1
    vals = np.empty(n + 1)
    # up factor; down factor is the inverse of the up factor
    u = math.exp(sigma * math.sqrt(dt))
    # if sigma is 0, no volatility, so p_u == p_d == 0
    if (sigma == 0):
        p_u = p_d = 0
    # else
    else:
        # probability of the underlying moving up
        p_u = (u * math.exp((r - q) * dt) - 1) / (u * u - 1)
        # probability of the underlying moving down
        p_d = 1 - p_u
    # calculate final values for all nodes
    # if the option is a call option
    if (is_type == "call"):
        for i in range(n + 1):
            # intrinsic value of option at time T_
            vals[i] = max(S_ * pow(u, 2 * i - n) - K, 0)
        # work backwards from period n to period 0 (for calls)
        for i in range(n):
            # for each period n - i, combine n - i + 1 nodes into n - i nodes
            for j in range(n - i):
                # value of the option at n - i - 1 is:
                # math.exp(-r * dt) * (p_u * vals[j + 1] + p_d * vals[j])
                # note that this is the same for calls or puts. since for each S[i]
                # where i = 0, 1, ... n S[i + 1] > S[i], call[i + 1] > call[i],
                # while put[i + 1] < put[i]
                vals[j] = math.exp(-r * dt) * (p_u * vals[j + 1] + p_d * vals[j])
                # if the option is american, there each vals[j] has an a value
                # that can be attained during exercise (S[j] at n - i - 1 minus K),
                # so the value of the option would be max(ex_val[j], vals[j])
                if (flavor == "american"):
                    vals[j] = max(vals[j], S_ * pow(u, 2 * j - n + i + 1) - K)
    # else if the option is a put option
    elif (is_type == "put"):
        for i in range(n + 1):
            vals[i] = max(K - S_ * pow(u, 2 * i - n), 0)
        # work backwards from period n to period 0 (for puts)
        for i in range(n):
            # for each period n - i, combine n - i + 1 nodes into n - i nodes
            for j in range(n - i):
                # same rationale as with calls
                vals[j] = math.exp(-r * dt) * (p_u * vals[j + 1] + p_d * vals[j])
                # if the option is american, vals[j] is max(vals[j], ex_val[j])
                if (flavor == "american"):
                    vals[j] = max(vals[j], K - S_ * pow(u, 2 * j - n + i + 1))
    # vals[0] is the expectation options price
    return vals[0]

