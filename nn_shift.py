# reads a csv file, and for a specified column of numerical data, will determine
# the smallest (read: negative) value in the column and add the absolute value
# of the smallest value to each value to make all data values nonnegative. if
# given a positive float as an additional argument, will shift all values by
# that number instead of looking for smallest col val. will write original data
# plus the new column returns back into the original file. must specify file at
# command-line runtime. will print shift factor k to command line, decomposing
# into the automatically identified and manually specified components
#
# Changelog:
#
# 10-25-2018
#
# initial creation; added quiet flag to suppress NaN warnings and allow command
# line specification of manual shift argument (float)

# import necessary stuff
import math
import sys
import numpy as np
import pandas as pd

# program name
PROGNAME = "nn_shift"

# help flag
HELP_FLAG = "--help"

# "quiet" (NaN warning suppressing) flag
QUIET_FLAG = "--quiet"

# true if NaN warnings should be suppressed, false if not
QUIET = False

# csv file extension
CSV_EXT = ".csv"

# help string
HELP_STR = ("Usage: {0} [ file col [ --quiet ] [ k ]]\n"
            "given a {1} file with labeled columns, and a column label that\n"
            "matches a column with numerical data, find the smallest (negative)\n"
            "value in the column and add its absolute value to each value in the\n"
            "column. if specified a value k on the command line, {0} will\n"
            "instead shift all values in the specified column by k. the new numerical\n"
            "series will be added back to the original file under the column header\n"
            "sh_col. note that for any missing value i, the new column of values will\n"
            "still be NaN (np.nan). will print out k to stdout.".format(PROGNAME, CSV_EXT)
)

# main
if (__name__ == "__main__"):
    # get number of arguments
    argc = len(sys.argv)
    # if there are no arguments
    if (argc == 1):
        print("{0}: error: no arguments given. type '{0} {1}' for usage.".format(
            PROGNAME, HELP_FLAG))
        quit(1)
    # else if there are two arguments
    elif (argc == 2):
        # if it is the help flag
        if (sys.argv[1] == HELP_FLAG):
            print(HELP_STR)
            quit()
        # else not enough arguments
        else:
            print("{0}: error: not enough arguments. type '{0} {1}' for usage.".format(
                PROGNAME, HELP_FLAG))
        quit(1)
    # else if there are three to 5 arguments, run appropriately (pass)
    elif (argc >= 3 and argc <= 5):
        pass
    # else too many arguments
    else:
        print("{0}: error: too many arguments. type '{0} {1}' for usage.".format(PROGNAME,
                                                                                 HELP_FLAG))
        quit(1)
        
    # if there are >= 3 arguments, proceed running
    # check if file extension is correct; if not, print error and exit
    if (CSV_EXT not in sys.argv[1]):
        print("{0}: error: input file {1} must be a {2} file.".format(PROGNAME,
                                                                      sys.argv[1], CSV_EXT))
        quit(1)
    # read file into dataframe
    df = pd.read_csv(sys.argv[1])
    # try to locate column in dataframe; if not, print error and exit
    if (sys.argv[2] not in df.columns):
        print("{0}: error: column {1} not in file {2}.".format(PROGNAME, sys.argv[2], sys.argv[1]))
        quit(1)
    # else if it is in column, then we are gucci
    # first assume k is 0
    k = 0
    # if argc >= 4 and <= 5
    if (argc > 3):
        # check if a float value k is in the argument list (not the first three args)
        for i in range(3, argc):
            # try to cast to get k
            try:
                k = float(sys.argv[i])
            # catch exception
            except:
                pass
        # if k is negative, print error
        if (k < 0):
            print("{0}: error: cannot pass a negative integer {1}.".format(k))
            quit(1)
        # look for QUIET_FLAG; ignore k if it exists
        for i in range(3, argc):
            # if we find QUIET_FLAG, set QUIET to true
            if (sys.argv[i] == QUIET_FLAG):
                QUIET = True
            # else if we find k, ignore k
            elif (sys.argv[i] == str(k)):
                pass
            # else print error and exit
            else:
                print("{0}: error: unknown flag '{1}'. type '{0} {2}' for usage.".format(
                    PROGNAME, sys.argv[i], HELP_FLAG))
                quit(1)
    # make reference to the column
    cr = df[sys.argv[2]]
    # forcibly convert to numeric data; anything missing will become NaN
    cr = pd.to_numeric(cr, errors = "coerce")
    # new pandas series (log returns) that is same size as the column (copies old values)
    lr = pd.Series(np.empty(cr.size))
    # only look for negative k if k == 0 (if k > 0, jump straight to shift section)
    if (k == 0):
        # for each element in cr, try to find the minimum (if the element is not NaN)
        for i in range(lr.size):
            if (not math.isnan(cr[i]) and cr[i] < k):
                k = cr[i]
    # record raw value of k
    raw_k = k
    # get absolute value of k
    k = abs(k)
    # after finding abs(k), add k to each element
    # for each element in lr
    for i in range(lr.size):
        # if cr[i] is NaN, set lr[i] to NaN and warn about NaN value is !QUIET
        if (math.isnan(cr[i])):
            if (not QUIET):
                print("warning: at {}: NaN value".format(i))
            lr[i] = np.nan
        # else cr[i] is not np.nan; set lr[i] to cr[i] + k
        else:
            lr[i] = cr[i] + k
    # print k to screen
    print("k = abs({})".format(raw_k))
    # add lr to the dataframe using .assign() method; column label is "sh_{}".format(sys.argv[2])
    # column label interpreted as keyword, so we have to pass through a dictionary
    kw_args = {"sh_{}".format(sys.argv[2]): lr}
    df = df.assign(**kw_args)
    # write back to the same file, no index names
    df.to_csv(sys.argv[1], index = False)
