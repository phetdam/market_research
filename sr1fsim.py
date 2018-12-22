# runs simulations of and plots single-factor short rate models (cir,  vasicek).
# can be specified data to calibrate models with, the type of model to run, and
# the number of processes to generate.
#
# Changelog:
#
# 12-22-2018
#
# made sure all the lines were 80 characters long or less, and reformatted the
# help string to be a multiline string.
#
# 12-09-2018
#
# moved from ./rate_models dir to top level dir. changed imports to reflect new
# file organization
#
# 10-29-2018
#
# removed PL_TITLES; the title of each plot will simply be MTYPE
#
# 10-27-2018
#
# added additional flag to specify the model to run (vasicek or cir). if model
# is not specified, the default process will be a vasicek model. changed several
# variable names and file name (from cir_main.py to sr1fsim.py) to reflect the
# more general nature of the file. added list of acceptable models and some
# other variables.
#
# 10-26-2018
#
# added additional flags and modes. can be calibrated off of a calibration file
# with flag -cf=file_name:data_col, and run k processes with flag -np=k.
# basically added a big chunk of boilerplate code to catch input errors. changed
# parameters from being displayed in the legend for each individual process to
# being displayed in the title; all processed in one graph have the same
# parameters anyways.
#
# 10-24-2018
#
# initial creation; git commit. renamed to cir_main.py, modified usage, cleaned
# a little

# program name
PROGNAME = "sr1fsim"

# help flag
HELP_FLAG = "--help"

# calibration flag
CF_FLAG = "-cf"

# number of processes to run
NP_FLAG = "-np"

# model type flag
MT_FLAG = "-mt"

# csv extension
CSV_EXT = ".csv"

# model names
# cox-ingersoll-ross model
CIR_N = "cir"
# vasicek model
VAS_N = "vas"

# acceptable model types to pass to MT_FLAG
MTYPES = [CIR_N, VAS_N]

# help string
HELP_STR = """Usage: {0} [ [ {1}=csv_file:data_col ] [ {2}=model ] [ {3}=k ] ]
       {0} [ {4} ]
generates stochastic short rate processes, by default 2, which will be started
with default parameters unless a data file (must be {5} file) and a specified
column of numerical data in that file is given, in which case the process will
be calibrated in an attempt to mimic the characteristics of the data. a
different number of processes k will be generated if specified. default model
run will be the vasicek model, unless a specific model is specified at runtime
with the {2} flag.

flags:

{1}\ttakes argument of form csv_file:data_col, where csv_file is the data
\tfile and data_col is the data column in the file to use for calibration.
{2}\ttakes argument model, which is the name of the model to run.
{3}\ttakes argument k, which is the number of processes to generate.
{4}\tprints this usage

acceptable arguments for flag {2}:

{6}\tcox-ingersoll-ross model
{7}\tvasicek model""".format(PROGNAME, CF_FLAG, MT_FLAG, NP_FLAG, HELP_FLAG,
                             CSV_EXT, CIR_N, VAS_N)

# indicates type of model being used; default "vas" (VAS_N)
MTYPE = VAS_N

# indicates how many processes should be generated; default 2
PR_N = 2

# default configurations for models; list [a, mu, dt, sigma, n]
MODEL_PARAM = [0.03, 0.1, 0.001, 0.07, 1000]

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
# import short_rate_1f
import rate_models.short_rate_1f as sr1f

# main
if (__name__ == "__main__"):
    # get length of arguments in the argv vector
    argc = len(sys.argv)
    # if there are no arguments
    if (argc == 1):
        pass
    # else if there is one argument
    elif (argc == 2):
        # if it is the help option, print usage and exit
        if (sys.argv[1] == HELP_FLAG):
            print(HELP_STR)
            quit()
        # else pass
        pass
    # else if there are two or three arguments (just pass)
    elif (argc == 3 or argc == 4):
        pass
    # else too many arguments
    else:
        print("{0}: too many arguments. type '{0} {1}' for usage.".format(
            PROGNAME, HELP_FLAG))
        quit()

    # will be a dataframe, if CF_FLAG is passed with the correct argument
    df = None
    # boolean for if a calibration file and data column have been provided, and
    # calibration should be performed
    c_model = False
    # boolean for unknown flag error
    uf_error = False
    # if there are one to three arguments
    if (argc >=2 and argc <= 4):
        # for each argument except the program name
        for i in range(1, argc):
            # reference to sys.argv[i]
            arg = sys.argv[i]
            # if the argument contains CF_FLAG, NP_FLAGS, or MT_FLAG
            if (CF_FLAG in arg or NP_FLAG in arg or MT_FLAG in arg):
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
                        print("{0}: error: argument to {1} must be of form "
                              "file:col.".format(PROGNAME, CF_FLAG))
                        quit(1)
                    # unpack into file name, column name
                    fn, cn = fnd
                    # check file extension of file; must be CSV_EXT (.csv)
                    # if not, print error and exit
                    if (CSV_EXT not in fn):
                        print("{0}: error: calibration file must be a {1} "
                              "file.".format(PROGNAME, CSV_EXT))
                        quit(1)
                    # else it is, so read into dataframe (let python handle
                    # any errors that occur)
                    df = pd.read_csv(fn)
                    # try to locate column in df; if not, print error and exit
                    if (cn not in df.columns):
                        print("{0}: error: column {1} not in file {2}.".format(
                            PROGNAME, cn, fn))
                        quit(1)
                    # set c_model to True so that calibration will take place
                    c_model = True
                # else if s_arg[0] == NP_FLAG
                elif (s_arg[0] == NP_FLAG):
                    # attempt to cast argument to int and assign to PR_N
                    try:
                        PR_N = int(s_arg[1])
                    # print error and exit
                    except:
                        print("{0}: error: argument to {1} expected to be "
                              "positive int.".format(PROGNAME, NP_FLAG))
                        quit(1)
                    # if PR_N has been set to less than 1, print error and exit
                    if (PR_N < 1):
                        print("{0}: error: argument to {1} must be "
                              "positive.".format(PROGNAME, NP_FLAG))
                        quit(1)
                # else if s_arg[0] == MT_FLAG
                elif (s_arg[0] == MT_FLAG):
                    # if the arg is not in MTYPES (invalid), print error + exit
                    if (s_arg[1] not in MTYPES):
                        print("{0}: error: invalid argument to {1}. acceptable "
                              "args: {2}".format(PROGNAME, MT_FLAG, MTYPES))
                        quit(1)
                    # else we have a valid model, so set MTYPE to the argument
                    MTYPE = s_arg[1]
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
    # if c_model is True, calibrate model
    if (c_model):
        # return calibration to MODEL_PARAM, using column cn in dataframe df
        # do not change dt or n scale
        MODEL_PARAM = sr1f.calibrate_model(df[cn])
    # print model type and params
    print(MTYPE, MODEL_PARAM)

    # determine which model to use; bind  appropriate function name to return_pr
    # if we have specified cir process
    if (MTYPE == CIR_N):
        return_pr = sr1f.return_cir
    # else if we have specified vasicek model
    elif (MTYPE == VAS_N):
        return_pr = sr1f.return_vas

    # create figure and plot processes
    # figure size width 12", height 9"
    fg = plt.figure(figsize = (12, 9))
    # for PR_N iterations
    for i in range(PR_N):
        # get x (t) and y (r) series of generated process; element 0 is time
        # series, 1 is r
        x, y = return_pr(*MODEL_PARAM, cc = i, df = False)
        # plot the series; label each as MTYPE + "_i"
        plt.plot(x, y, label = "{0}_{1}".format(MTYPE, i))
    # format after plotting
    # x label, y label (make vertical)
    plt.xlabel("t")
    plt.ylabel("r", rotation = 0)
    # graph title; put parameters there so you don't clutter the graph
    plt.title("{0} (a={1}, mu={2}, dt={3}, sigma={4}, n={5})".format(
        MTYPE, *[round(e, 7)for e in MODEL_PARAM]))
    # show legend
    plt.legend()
    # save to file MTYPE + ".png"
    plt.savefig(MTYPE + ".png")
