# script that reads from a configuration file (any *.xyc) that instructs it on what
# xy series of already known options prices vs. x-axis to graph, and the data that
# will be fed to the specified options model(s) to calculate prices that will also
# be graphed. note that fast_plot is a required import for options_grapher.
#
# syntax for configuration files:
#
# any line that starts with '#' will be ignored, and any text after a '#' will be
# ignored as well.
#
# first non-commented line must declare that the file is a config file as follows:
#
# __xyc__
#
# for each file you wish to import and graph, use the following format for each
# file, making sure to put each file on a separate line:
#
# __file__: file_1.csv: xcol_1, ycol_1, series_label_1; \
#                       xcol_2, ycol_2, series_label_2; \
#                       ... xcol_k, ycol_k, series_label_k
# # note that columns can be repeated in any of these pairs, but must exist in the
# # .csv file and must also be of the same length or an error will be thrown. you
# # can break lines with the explicit '\' character. however, if '\' has text
# # following it, you will probably have an error thrown. hehe. note that the
# # final semicolon (omitted here) is optional.
#
# also make sure somewhere in the file after __xyc__ and before __end__ is the
# __params__ tag, which defines parameters for the graph x, y, and title values.
# the format is as follows:
#
# __params__: x_label, y_label, plot_title;
#
# # the final semicolon may also be omitted.
#
# if there is no series label given, the name of the y column will be used instead.
# note that any y-series being plotted should be a PRICE SERIES because the script
# will be graphing calculated options prices.
#
# the config file should be ended with the singular tag "__end__", which should be put
# on its own line. failure to include this tag will result in the parser (hopefully)
# issuing a warning, but should still run fine.
#
# Changelog:
#
# 12-19-2018
#
# completed parser part of the script and the main graphing function. configuration
# file able to specify files, columns, and graph labels for the data and the resulting
# text to put on the graph. currently looking into ways to improve fast_plot to change
# the different kinds of plotting modes. changed name of file and program to xy_grapher,
# as well as updating the different names of the extensions as needed. still need to do
# work on the help string.
#
# 12-10-2018
#
# edited configuration file instructions. this is getting hairy.
#
# 12-09-2018
#
# there was probably an original file before this, but i have no idea where it went.
# so today will mark the date of initial creation.

# access to standard error codes
import errno
# import fast_plot
import lib.fast_plot as fast_plot
import pandas as pd
import sys

# program name
PROGNAME = "xy_grapher"

# config file extension
CONFIG_EXT = ".xyc"

# valid image file extensions
IMG_EXTS = [".jpg", ".png"]

# csv file extension
CSV_EXT = ".csv"

# help flag
HELP_FLAG = "--help"

# help string
HELP_STR = (
    "Usage: {0} config_file{1}\n"
    "reads a configuration file of type {1} (required), and plots the options series as\n"
    "specified by the configuration file. this help is incomplete; please check back\n"
    "at a later date. type '{0} {2}' for usage.".format(PROGNAME, CONFIG_EXT, HELP_FLAG)
    )

# default output file name
DEFAULT_OUT_N = "xy_graph.png"

# function names
_CFPARSER_N = "_cfparser"
_FOPEN__R_N = "_fopen__r"

#===== parser code and variables =====#

# dict of key tokens that the parser watches out for
_TOKENS = {
    # declares the beginning of the config file
    "__HEAD": "__xyc__",
    # declares file data
    "__FILE": "__file__",
    # declares immediate end of configuration file
    "__END": "__end__",
    # declares parameters for the x, y and title of the ouput grapph
    "__PARAMS": "__params__",
    # declares commented block
    "__OMIT": "#",
    # declares line break
    "__LBREAK": "\\",
    # empty line, ignore
    "__EMPTY": "",
    # major token split
    "__MAJTS": ":",
    # minor token split
    "__MINTS": ";",
    # series token split
    "__SERTS": ","
}

# parse error classes

# generic parse error
class ParseError(Exception):
    # constructor; allows one to provide line number if needed
    def __init__(self, _msg = "parse error", _line = "unknown"):
        # if line is not string, convert to string
        if (not isinstance(_line, str)):
            _line = str(_line)
        super(ParseError, self).__init__("line {0}: {1}".format(_line, _msg))
        return None

# raised when empty config file is presented (_cf is config file name)
class EmptyFileError(Exception):
    def __init__(self, _cf = "[no name]"):
        super(EmptyFileError, self).__init__("config file {0} is empty".format(_cf))
        return None

# error when file has not been declared (_TOKENS["__HEAD"] not encountered)
class ActivationError(ParseError):
    def __init__(self, _line = "unknown"):
        super(ActivationError, self).__init__(_msg = "missing {0}".format(
            _TOKENS["__HEAD"]), _line = _line)
        return None

# error when an explicitly illegal token has been encountered
class IllegalTokenError(ParseError):
    # _tok is the illegal token encountered
    def __init__(self, _tok, _line = "unknown"):
        super(IllegalTokenError, self).__init__(
            _msg = "encountered illegal token '{}'".format(_tok),
            _line = _line)
        return None

# simple parser that reads line by line and tries to make sense of the tokens given.
# returns a list of file tokens in the following format:
#
# [["file_1", ["x1_1", "y1_1", "name1_1"], ... ["x1_k", "y1_k", "name1_k"]],
#  ["file_2", ["x2_1", "y2_1", "name2_1"], ... ["x2_l", "y2_l", "name2_k"]],
#      ...
#  ["file_n", ["xn_1", "yn_1", "namen_1"], ... ["xn_r", "yn_r", "namen_k"]]]
#
# and a list of graph parameters in the following format:
#
# ["x_axis", "y_axis", "title_text"]
#
# it's not the parser's job to check if the files exist or if any columns in the files
# are valid, but it will enforce whether or not the files end with CSV_EXT or not.
#
# parameters:
#
# fin         input file; must pass a text file object
#
def _cfparser(fin):
    # first check if the input file is None or not
    if (fin == None):
        raise FileNotFoundError("{0}.{1}: file expected, None received".format(
            PROGNAME, _CFPARSER_N))
    # else if file is not None, let's go
    # list of file tokens to return
    ftoks = []
    # graph params
    g_params = None
    # keep track of line number
    lnum = 0
    # default series number: if no name is given for an x-y series, it will be
    # given a default name
    dnum = 0
    # is the file activated? (basically have we read _TOKENS["__HEAD"] yet?)
    is_active = False
    # is the file explicitly terminated? (this is recommended)
    is_exited = False
    # did we already retrieve params for the graph from the file
    has_params = False
    # input loop
    while (True):
        # read the raw line, with trailing spaces and then comments stripped
        raw_line = fin.readline()
        # increment lnum
        lnum += 1
        # if raw_line is empty, we hit an EOF
        if (raw_line == _TOKENS["__EMPTY"]):
            # if len(ftoks) is 0, this is a premature EOF. raise parse error
            if (len(ftoks) == 0):
                raise ParseError(_msg = "premature EOF encountered", _line = lnum)
            # else break
            break
        # modify raw_line by stripping trailing spaces and comments
        raw_line = raw_line.rstrip().split(_TOKENS["__OMIT"])[0]
        # if raw_line ends with _TOKENS["__LBREAK"], split off the line break token
        # and continue appending lines until we hit EOF or the next string does not
        # end with the break token
        if (raw_line.endswith(_TOKENS["__LBREAK"])):
            raw_line = raw_line.split(_TOKENS["__LBREAK"])[0]
            while (True):
                raw_next = fin.readline().rstrip().split(_TOKENS["__OMIT"])[0]
                lnum += 1
                # if we have hit EOF
                if (raw_next == _TOKENS["__EMPTY"]):
                    raise ParseError(_msg = "unexpected EOF while parsing line",
                                     _line = lnum)
                # append stripped raw_next to raw_line
                raw_line += raw_next.split(_TOKENS["__LBREAK"])[0]
                # if we do not have to continue appending and breaking, break
                if (not raw_next.endswith(_TOKENS["__LBREAK"])):
                    break
                # else we continue the loop

        # strip raw_line of all white space, assign to clean_line
        clean_line = "".join(raw_line.split())
        # if clean_line is empty, continue loop
        if (clean_line == _TOKENS["__EMPTY"]):
            continue
        # else if not empty
        # if is_active is False
        if (is_active == False):
            # if clean_line equals _TOKENS["__HEAD"], set is_active to True and
            # skip the rest of the loop
            if (clean_line == _TOKENS["__HEAD"]):
                is_active = True
                continue
            # else break
            else:
                break
        # else the file is already activated; first check to see if there is a
        # duplicate _TOKENS["__HEAD"] in the file
        if (clean_line == _TOKENS["__HEAD"]):
            raise ParseError(_msg = "duplicate occurrence of {0} in file {1}".format(
                _TOKENS["__HEAD"], fin.name), _line = lnum)
        # next check to see if _TOKENS["__END"] has been encountered
        if (clean_line == _TOKENS["__END"]):
            # if len(ftoks) is 0, we have prematurely encountered the end token,
            # so raise a parse error
            if (len(ftoks) == 0):
                raise ParseError(_msg = "premature incidence of {0} before {1}".format(
                    _TOKENS["__END"], _TOKENS["__FILE"]), _line = lnum)
            # if g_params is still None, we have prematurely encountered the end
            # token so raise a parse error
            if (g_params == None):
                raise ParseError(_msg = "premature incidence of {0} before {1}".format(
                    _TOKENS["__END"], _TOKENS["__PARAMS"]), _line = lnum)
            # if len(ftoks) > 0, then set is_exited to True and break the loop
            is_exited = True
            break
        
        # if clean_line is not equal to either of the standalone tokens, we should
        # check to see if we can retrieve the file/params token
            
        # break the line by the token defined by _TOKENS["__MAJTS"], a major split
        maj_s = clean_line.split(_TOKENS["__MAJTS"])
        # check if we recognize the first token
        # if we recognize the token
        if (maj_s[0] in _TOKENS.values()):
            # first check if token is empty (special handling for this one)
            if (maj_s[0] == _TOKENS["__EMPTY"]):
                raise ParseError(_msg = "missing token", _line = lnum)
            # if token is not _TOKENS["__FILE"], or _TOKENS["__PARAMS"] it is out of
            # place. raise parse error
            if (maj_s[0] != _TOKENS["__FILE"] and maj_s[0] != _TOKENS["__PARAMS"]):
                raise ParseError(
                    _msg = "out of place {} encountered".format(maj_s[0]), _line = lnum)
        # else we don't know this token and thus raise illegal token error
        else:
            raise IllegalTokenError(maj_s[0], _line = lnum)
        
        ### if the token is the _TOKENS["__FILE"]
        if (maj_s[0] == _TOKENS["__FILE"]):
            # if the length of maj_s is less or more than 3, parse error
            if (len(maj_s) != 3):
                raise ParseError(_msg = "expected 3 major tokens, {} "
                                 "received".format(len(maj_s)), _line = lnum)

            # it is sure that maj_s[0] is _TOKENS["__FILE"]. we must check if either
            # maj_s[1] or maj_s[2] are empty: if so, raise parse error again
            if (maj_s[1] == _TOKENS["__EMPTY"] or maj_s[2] == _TOKENS["__EMPTY"]):
                raise ParseError(_msg = "expected 3 major tokens, at least one empty",
                                 _line = lnum)
        
            # we know that none of the major tokens are empty. after enforcing input
            # file type, final token of maj_s will undergo a multi-part split fest.

            # enforce input file type (must end in CSV_EXT)
            if (not maj_s[1].endswith(CSV_EXT)):
                raise ParseError(_msg = "input file must be a {} file".format(CSV_EXT),
                                 _line = lnum)
            # create a new entry for this file and append maj_s[1] to it
            f_ent = []
            f_ent.append(maj_s[1])
            # perform a minor split on maj_s[2]
            min_s = maj_s[2].split(_TOKENS["__MINTS"])
            # if the last token of min_s is empty, pop it
            if (min_s[len(min_s) - 1] == _TOKENS["__EMPTY"]):
                min_s.pop()
            # but if any other tokens are empty, raise parse error
            if (_TOKENS["__EMPTY"] in min_s):
                raise ParseError(_msg = "extraneous {}".format(_TOKENS["__MINTS"]),
                                 _line = lnum)
            # if min_s is length 0, raise parse error
            if (len(min_s) == 0):
                raise ParseError(_msg = "no series tokens", _line = lnum)
            # for each token in min_s, perform a series split on each one
            for se in min_s:
                ser_se = se.split(_TOKENS["__SERTS"])
                # if len(ser_se) < 2 or > 3, raise parse error
                if (len(ser_se) < 2 or len(ser_se) > 3):
                    raise ParseError(_msg = "expected 2-3 series tokens, {} "
                                     "received".format(len(ser_se)), _line = lnum)
                # if len(ser_se) == 2, copy ser_se[1] and append it to the list
                if (len(ser_se) == 2):
                    ser_se.append(ser_se[1])
                    dnum += 1
                # append ser_se to f_ent
                f_ent.append(ser_se)
            # final format of the file entry should be as follows:
            # ["file_1", ["x1_1", "y1_1", "name1_1"], ... ["x1_k", "y1_k", "name1_k]]
            # now we append f_ent to ftoks, and proceed with the loop
            ftoks.append(f_ent)

        ### else if the token is the _TOKENS["__PARAMS"]
        elif (maj_s[0] == _TOKENS["__PARAMS"]):
            # if has_params is True, raise parse error
            if (has_params == True):
                raise ParseError(_msg = "duplicate {} token encountered".format(
                    _TOKENS["__PARAMS"]), _line = lnum)
            # if the length of maj_s is less or more than 2, parse error
            if (len(maj_s) != 2):
                raise ParseError(_msg = "expected 2 major tokens, {} "
                                 "received".format(len(maj_s)), _line = lnum)

            # it is sure that maj_s[0] is _TOKENS["__PARAMS"]. we must check if 
            # maj_s[1] is empty: if so, raise parse error
            if (maj_s[1] == _TOKENS["__EMPTY"]):
                raise ParseError(_msg = "expected 2 major tokens, latter empty",
                                 _line = lnum)
        
            # we know that neither of the two major tokens are empty. after we
            # remove the optional _TOKENS["__MINTS"] from maj_s[1], we will
            # perform a series split on maj_s[1]

            # split maj_s[1] by _TOKENS["__MINTS"], a minor split
            prms = maj_s[1].split(_TOKENS["__MINTS"])
            # if the last token of prms is empty, pop it
            if (prms[len(prms) - 1] == _TOKENS["__EMPTY"]):
                prms.pop()
            # if prms is empty, raise parse error
            if (len(prms) == 0):
                raise ParseError(_msg = "missing graph params", _line = lnum)
            # if the length of prms > 1, raise parse error
            if (len(prms) > 1):
                raise ParseError(_msg = "multiple sets of graph params", _line = lnum)
            # set prms to its only element
            prms = prms[0]
            # perform a series split on prms; set g_params
            g_params = prms.split(_TOKENS["__SERTS"])
            # if there len(g_params) != 3, raise parse error
            if (len(g_params) != 3):
                raise ParseError(_msg = "3 graph params expected, {} received".format(
                    len(g_params)), _line = lnum)
            
            # we will allow empty parameters, so no check if parameters are empty
            # addressing the problem of losing whitespace: because we know that the
            # line is of the correct syntax, we can use raw_line to preserve spacing
            # (except for trailing spaces)

            # set g_params to:
            # raw_line.split(_TOKENS["__MAJTS"])[1].split(
            #     _TOKENS["__MINTS"])[0].split(_TOKENS["__SERTS"])
            g_params = raw_line.split(_TOKENS["__MAJTS"])[1].split(
                _TOKENS["__MINTS"])[0].split(_TOKENS["__SERTS"])
            # strip each token in g_params
            for i in range(len(g_params)):
                g_params[i] = g_params[i].strip()
            # set has_params to True
            has_params = True

    ### end of the parsing loop
    # if raw_line is blank but is_active is false, the config file was not
    # yet properly declared.
    if (is_active == False):
        # if lnum == 0, raise EmptyFileError
        if (lnum == 0):
            raise EmptyFileError(_cf = fin.name)
        # else the config file was just not activated before exit
        raise ActivationError(_line = lnum)
    # if the file was not explicitly terminated, print a warning
    if (is_exited == False):
        print("{0}.{1}: {2} not explicitly terminated".format(
            PROGNAME, _CFPARSER_N, fin.name), file = sys.stderr)
    # return the tokens and graph params
    return ftoks, g_params

#===== end of parser code and variables =====#

# function to open a file for reading, with builtin file error handling routine.
# remember to close the returned file object after calling!
#
# parameters:
#
# _fname       file name (string)
#
def _fopen__r(_fname):
    # if _fname is None, print error and exit
    if (_fname == None):
        print("{0}.{1}: file name expected, None passed".format(PROGNAME, _FOPEN__R_N))
        quit(1)
    # if file name is not None, but is not a string, print error and exit
    if (not isinstance(_fname, str)):
        print("{0}.{1}: string expected, {2} received".format(PROGNAME, _FOPEN__R_N,
                                                              type(_fname)))
        quit(1)
    # else the file name is a string, so attempt to open it
    try:
        _f = open(_fname, "r")
    # access attributes of caught exception and print correct error message
    except OSError as ose:
        # if file is not found
        if (ose.errno == errno.ENOENT):
            print("{0}: error: file {1} not found".format(PROGNAME, _fname),
                  file = sys.stderr)
        # else if there is an I/O error
        elif (ose.errno == errno.EIO):
            print("{0}: error: error reading file {1}".format(PROGNAME, _fname),
                  file = sys.stderr)
        # else if there is an access issue
        elif (ose.errno == errno.EACCES):
            print("{0}: error: error accessing file {1}".format(PROGNAME, _fname),
                  file = sys.stderr)
        # else print generic OS error message and error code
        else:
            print("{0}: error: OSError {1} ({2}) from file {3}".format(
                PROGNAME, ose.errno, errno.errcode[ose.errno], _fname), file = sys.stderr)
        # quit
        quit(1)
    # return _f
    return _f

# main
if (__name__ == "__main__"):
    # get number of arguments
    argc = len(sys.argv)
    # name of output file (initially DEFAULT_OUT_N)
    fout_n = DEFAULT_OUT_N
    # if no arguments are given, print error and exit
    if (argc == 1):
        print("{0}: no arguments. type '{0} {1}' for usage.".format(PROGNAME, HELP_FLAG))
        quit()
    # else if there is one argument
    elif (argc == 2):
        # if it is the help flag
        if (sys.argv[1] == HELP_FLAG):
            print(HELP_STR)
            quit()
        # else just pass
    # else if there is the optional second argument (image file to save graph to)
    elif (argc == 3):
        pass
    # else there are too many arguments
    else:
        print("{0}: error: too many arguments. type '{0} {1}' for usage".format(
            PROGNAME, HELP_FLAG), file = sys.stderr)
        quit(1)

    # if the config file name does not end with CONFIG_EXT, print error and exit
    if (not sys.argv[1].endswith(CONFIG_EXT)):
        print("{0}: error: configuration file must end with {1}".format(
            PROGNAME, CONFIG_EXT), file = sys.stderr)
        quit(1)
    # if the optional output file (image) is given but does not have a valid
    # extension (i.e. the extension it has does not match any one of IMG_EXTS),
    # print error and exit, else set fout_n to sys.argv[2]
    if (argc == 3):
        # split by "."
        out_s = sys.argv[2].split(".")
        # if length of out_s != 2 or "." + out_s[1] not in IMG_EXTS, print
        # error and exit
        if (len(out_s) != 2 or ("." + out_s[1] not in IMG_EXTS)):
            print("{0}: error: output file must be one of the following: {1}".format(
                PROGNAME, IMG_EXTS), file = sys.stderr)
            quit(1)
        # else set fout_n to sys.argv[2]
        fout_n = sys.argv[2]
    # return file object from config file; handle any exceptions
    fin = _fopen__r(sys.argv[1])
    # get proper tokens by reading from fin
    # each element of f_ents is of the following format:
    # ["file_1", ["x1_1", "y1_1", "name1_1"], ... ["x1_k", "y1_k", "name1_k]]
    # the g_params element is of the following format:
    # ["x_name", "y_name", "title_text"]
    f_ents, g_params = _cfparser(fin)
    #print(f_ents)
    #print(g_params)
    # close config file; we don't need it anymore
    fin.close()

    # use retrieved tokens to begin pulling data from the input files and putting
    # it in xy_series, which will contain all the series to be graphed, and
    # labels, a list of all the labels for each series to be graphed. by default,
    # the program will continue running through errors: if the x, y, or both parts
    # of a series are missing, an error will be issued, but the program will proceed
    # and graph only the series that are fully intact and have labels.
    
    # list of xy series to graph; each element is [x_series, y_series]
    xy_series = []
    # list of labels, must be same length as xy_series
    labels = []
    # validate each file entry and graph using fast_plot
    for ent in f_ents:
        # open file; handle any OS errors/exceptions
        fin_ent = _fopen__r(ent[0])
        # read into a dataframe
        df_ent = pd.read_csv(fin_ent.name)
        # close input file; we don't need it anymore
        fin_ent.close()
        # for each of the following x/y/name column entries
        for i in range(1, len(ent)):
            # is the series complete? we assume True to begin
            is_complete = True
            # split into x, y, and label columns
            x_lab, y_lab, lab_lab = ent[i]
            # check if the referenced x/y columns exist; if either do not exist,
            # print a warning to stderr, set is_complete to False, and continue
            if (x_lab not in df_ent.columns):
                print("{0}: error: no x column '{1}' in {2}".format(
                    PROGNAME, x_lab, ent[0]), file = sys.stderr)
                is_complete = False
            if (y_lab not in df_ent.columns):
                print("{0}: error: no y column '{1}' in {2}".format(
                    PROGNAME, x_lab, ent[0]), file = sys.stderr)
                is_complete = False
            # if the series is not complete, continue
            if (is_complete == False):
                continue
            # else if it is complete, retrieve corresponding x/y series from df_ent,
            # append as a two-element list to xy_series, and append corresponding
            # label to labels
            xy_series.append([df_ent[x_lab], df_ent[y_lab]])
            labels.append(lab_lab)
    # use fast_plot to write the series to a graph
    fast_plot.xy_plot(xy_series, ll__ = labels, fout = fout_n, title = g_params[2],
                      xlab = g_params[0], ylab = g_params[1])
