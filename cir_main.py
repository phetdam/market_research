# contains basic implementation of a cox-ingersol-ross single-factor short rate model
# https://en.wikipedia.org/wiki/Cox-Ingersoll-Ross_model
#
# Changelog:
#
# 10-26-2018
#
# added additional flags and modes. can be calibrated off of a calibration file with
# flag -cf=file_name:data_col, and run k processes with flag -np=k. basically added a
# big chunk of boilerplate code to catch input errors.
#
# 10-24-2018
#
# initial creation; git commit. renamed to cir_main.py, modified usage, cleaned a little

# program name
PROGNAME = "cir_main"

# help flag
HELP_FLAG = "--help"

# calibration flag
CF_FLAG = "-cf"

# number of processes to run
NP_FLAG = "-np"

# csv extension
CSV_EXT = ".csv"

# help string
HELP_STR = ("Usage: {0} [ {1}=csv_file:data_col ] [ {2}=k ]\n"
            "       {0} [ {3} ]\n"
            "generates cir processes, by default 2, which will be started with default\n"
            "parameters unless a data file (must be {4} file) and a specified column\n."
            "of numerical data in that file is given, in which case the process will\n"
            "be calibrated in an attempt to mimic the characteristics of the data.\n"
            "a different number of processes k will be generated if specified.\n\n"
            "flags:\n\n"
            "{1}\ttakes argument of form csv_file:data_col, where csv_file is the data\n"
            "\tfile and data_col is the data column in the file to use for calibration.\n"
            "{2}\ttakes argument k, which is the number of processes to generate.\n"
            "{3}\tprints this usage".format(PROGNAME, CF_FLAG, NP_FLAG, HELP_FLAG, CSV_EXT)
    )

# default file to save to
DEFAULT_F = "cir.png"

# indicates how many cir processes have been generated
CIR_COUNT = 0

# indicates how many cir processes should be generated; default 2
CIR_N = 2

# default configurations for cir; list [a, mu, dt, sigma, n]
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
    # if there are no arguments
    if (argc == 1):
        pass
    # else if there is one argument
    elif (argc == 2):
        # if it is the help option
        if (sys.argv[1] == HELP_FLAG):
            print(HELP_STR)
            quit()
    # else if there are two arguments (just pass)
    elif (argc == 3):
        pass
    # else too many arguments
    else:
        print("{0}: too many arguments. type '{0} {1}' for usage.".format(PROGNAME, HELP_FLAG))
        quit()

    # will be a dataframe, if CF_FLAG is passed with the correct argument
    df = None
    # boolean for if a calibration file and data column have been provided, and calibration
    # should be performed
    c_cir = False
    # boolean for unknown flag error
    uf_error = False
    # if there are one or two arguments
    if (argc == 2 or argc == 3):
        # for each argument except the program name
        for i in range(1, argc):
            # reference to sys.argv[i]
            arg = sys.argv[i]
            # if the argument contains CF_FLAG or NP_FLAGS
            if (CF_FLAG in arg or NP_FLAG in arg):
                # attempt to split arg by "="
                s_arg = arg.split("=")
                # if s_arg size is not 2, set uf_error to True and break
                if (len(s_arg) != 2):
                    uf_error = True
                    break
                # if s_arg[0] == CF_FLAG
                if (s_arg[0] == CF_FLAG):
                    # split argument into file name and data column [file, col]
                    fnd = s_arg[1].split(":")
                    # if size of fnd != 2, print error and exit
                    if (len(fnd) != 2):
                        print("{0}: error: argument to {1} must be of form file:col.".format(
                            PROGNAME, CF_FLAG))
                        quit(1)
                    # unpack into file name, column name
                    fn, cn = fnd
                    # check file extension of file; must be CSV_EXT (.csv)
                    # if not, print error and exit
                    if (CSV_EXT not in fn):
                        print("{0}: error: calibration file must be a {1} file.".format(
                            PROGNAME, CSV_EXT))
                        quit(1)
                    # else it is, so read into dataframe (let python handle errors)
                    df = pd.read_csv(fn)
                    # try to locate column in dataframe; if not, print error and exit
                    if (cn not in df.columns):
                        print("{0}: error: column {1} not in file {2}.".format(PROGNAME, cn, fn))
                        quit(1)
                    # set c_cir to True so that calibration will take place
                    c_cir = True
                # else if s_arg[0] == NP_FLAG
                elif (s_arg[0] == NP_FLAG):
                    # attempt to cast argument to int and assign to CIR_N
                    try:
                        CIR_N = int(s_arg[1])
                    # print error and exit
                    except:
                        print("{0}: error: argument to {1} expected to be positive int.".format(
                            PROGNAME, NP_FLAG))
                        quit(1)
                    # if CIR_N has been set to less than 1, print error and exit
                    if (CIR_N < 1):
                        print("{0}: error: argument to {1} must be positive.".format(
                            PROGNAME, NP_FLAG))
                        quit(1)
                # else set uf_error to True and break
                else:
                    uf_error = True
                    break
                
            # else it's some random argument; set uf_error to True and break
            else:
                uf_error = True
                break

    # if there is an uf_error (unknown flag error), print error and exit
    if (uf_error):
        print("{0}: error: unknown flag '{1}'. type '{0} {2}' for usage.".format(
            PROGNAME, arg, HELP_FLAG))
        quit(1)
    # if c_cir is True, calibrate CIR process
    if (c_cir):
        # return calibration to CIR_PARAM, using column cn in dataframe df
        # do not change dt or n scale
        CIR_PARAM = cir.calibrate_cir(df[cn])
    # print params
    print(CIR_PARAM)
        
    # create figure and plot processes
    # figure size width 12', height 9'
    fg = plt.figure(figsize = (12, 9))
    # for CIR_N iterations
    for i in range(CIR_N):
        # get x (t) and y (r) series of cir process; element 0 is time series, 1 is r
        x, y = cir.return_cir(*CIR_PARAM, cc = i, df = False)
        # plot the series; label each as cir_i
        plt.plot(x, y, label = "cir_{0}".format(i))
    # format after plotting
    # x label, y label (make vertical)
    plt.xlabel("t")
    plt.ylabel("r", rotation = 0)
    # graph title; put parameters there so you don't clutter the graph
    plt.title("CIR process (a={0}, mu={1}, dt={2}, sigma={3}, n={4})".format(
        *[round(e, 7)for e in CIR_PARAM]))
    # show legend
    plt.legend()
    # save to file
    plt.savefig(DEFAULT_F)
