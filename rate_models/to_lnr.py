# reads a csv file, transforms a numerical column into a series of log returns,
# with the first element in the column starting at 0. will write the original
# data plus the new column of log returns back into the original file. must
# specify file at command-line runtime.
#
# Changelog:
#
# 10-25-2018
#
# changed program name to to_lnr, file name to to_lnr.py. instead of assuming
# missing log returns are 0, they are filled with np.nan. writes new data to
# original file, instead of a different file
#
# 10-24-2018
#
# initial creation; added quiet flag to suppress NaN warnings

# import necessary stuff
import math
import sys
import numpy as np
import pandas as pd

# program name
PROGNAME = "to_lnr"

# help flag
HELP_FLAG = "--help"

# "quiet" (NaN warning suppressing) flag
QUIET_FLAG = "--quiet"

# true if NaN warnings should be suppressed, false if not
QUIET = False

# csv file extension
CSV_EXT = ".csv"

# help string
HELP_STR = ("Usage: {0} [ file col [ --quiet ] ]\n"
            "given a {1} file with labeled columns, and a column label that\n"
            "matches a column with numerical data, transform the column into\n"
            "a series of log returns and add the new numerical series to the\n"
            "original {1} file with the column header lnr_col\n\n"
            "note that for any missing value i, log returns i and i + 1 will\n"
            "be set to NaN (np.nan). for interest rates, negative rates are\n"
            "treated as if they are 0, and thus log returns for negative rates\n"
            "will also be set to NaN.".format(PROGNAME, CSV_EXT)
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
    # else if there are three or four arguments, run appropriately (pass)
    elif (argc == 3 or argc == 4):
        pass
    # else too many arguments
    else:
        print("{0}: error: too many arguments. type '{0} {1}' for usage.".format(PROGNAME,
                                                                                 HELP_FLAG))
        quit(1)
        
    # if there are three arguments, proceed running
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
    # if argc == 4
    if (argc == 4):
        # if the last argument is QUIET_FLAG, set QUIET to True
        if (sys.argv[3] == QUIET_FLAG):
            QUIET = True
        # else print error and exit
        else:
            print("{0}: error: unknown flag '{1}'. type '{0} {2}' for usage.".format(PROGNAME,
                                                                                     sys.argv[3],
                                                                                     HELP_FLAG))
            quit(1)
    # make reference to the column
    cr = df[sys.argv[2]]
    # forcibly convert to numeric data; anything missing will become NaN
    cr = pd.to_numeric(cr, errors = "coerce")
    # new pandas series (log returns) that is same size as the column (copies old values)
    lr = pd.Series(np.empty(cr.size))
    # set initial element to 0
    lr[0] = 0
    # for each element in lf, except for the first
    for i in range(1, lr.size):
        # if the prev element is NaN, we already checked for that last index i, so
        # simply set lr[i] to np.nan and continue
        if (math.isnan(cr[i - 1])):
            lr[i] = np.nan
            continue
        # if the current element is NaN, indicate NaN at i if QUIET is False; set lr[i] to np.nan
        # and continue
        if (math.isnan(cr[i])):
            if (not QUIET):
                print("warning: at {}: NaN value".format(i))
            lr[i] = np.nan
            continue
        # if either cr[i - 1] or cr[i] are <= 0, set lr[i] to np.nan and continue
        if (cr[i - 1] <= 0 or cr[i] <= 0):
            lr[i] = np.nan
            continue
        # else calculate log return
        #lr[i] = math.log(f_ce / f_pe)
        lr[i] = math.log(cr[i] / cr[i - 1])
    # add lr to the dataframe using .assign() method; column label is "lnr_{}".format(sys.argv[2])
    # column label interpreted as keyword, so we have to pass through a dictionary
    kw_args = {"lnr_{}".format(sys.argv[2]): lr}
    df = df.assign(**kw_args)
    # write back to the same file, no index names
    df.to_csv(sys.argv[1], index = False)

