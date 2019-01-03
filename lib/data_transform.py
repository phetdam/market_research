"""
the data_transform module is a collection of functions for performing quick data
transformations on columns in a pandas dataframe. intended currently only for
numerical data, but may be extended for manipulation of some categorical data
in the future.
"""
# Changelog:
#
# 01-03-2019
#
# separated module description from change log and made module description a
# docstring instead of a commented block. changed function comment blocks into
# docstrings, and made the library name and all function names private.
#
# 12-31-2018
#
# happy new year's eve! completed the log() function, and wrote an additional
# function _dfvalwarn() to help handle warnings when performing log() on cols
# in a DataFrame. made correction that prevents setting with copy warning.
#
# 12-30-2018
#
# completed work on log() function except for overwrite feature. added option
# for quiet operation, inplace operation, and optional overwrite of input
# DataFrame (enabled by default).
#
# 12-26-2018
#
# initial creation, added header comments. set name to "data_transform", and
# started work on log() function.

import math
import numpy as np
import pandas as pd
import sys

# library  name
_LIBNAME = "data_transform"

# function names
_DFVALWARN_N = "_dfvalwarn"
_LOG_N = "log"


def _dfvalwarn(df, qual = "invalid", lib_n = "anon_lib", func_n = "anon_func",
               df_id = "unknown", id_ismloc = False, col = "??", row = "??"):
    """
    standardized function for issuing warnings when a function operating on a
    DataFrame encounters an illegal value that the user should be warned about,
    but which does not halt the operation of the function. messages will have
    the following format (printed to stderr):

    libname.funcname: DataFrame df, id = id_n: df[col][index] <qualifier>

    note that if id_ismloc is True, then the message format will look like this:

    libname.funcname: DataFrame df at 0x<mem loc>: df[col][index] <qualifier>

    parameters:

    df          required dataframe
    qual        qualifier for warning message, default "invalid"
    lib_n       name of the library the function is in, default "anon_lib"
    func_n      name of the function that encountered the error in the DataFrame
                with default value "anon_func"
    df_id       id of the DataFrame; can be found by passing id(df). default
                "unknown"
    id_ismloc   default False. set to True for different message formatting.
                note that with CPython, formatting id(df) as hex will give the
                memory location of the DataFrame.
    col         label/index of offending column in DataFrame, default "??"
    row         index of offending row in DataFrame, default "??"
    """
    # if df is None
    if (df is None):
        raise ValueError("{0}.{1}: error: DataFrame required, None passed"
                         "".format(_LIBNAME, _DFVALWARN_N))
    # if df is not a DataFrame, raise TypeError
    if (not isinstance(df, pd.DataFrame)):
        raise TypeError("{0}.{1}: error: DataFrame required, {2} passed"
                        "".format(_LIBNAME, _DFVALWARN_N, type(df)))
    # check that qualifier is a string
    if (not isinstance(qual, str)):
        raise TypeError("{0}.{1}: error: qual must be type str".format(
            _LIBNAME, _DFVALWARN_N))
    # check that both lib_n and func_n are both strings
    if (not isinstance(lib_n, str)):
        raise TypeError("{0}.{1}: error: lib_n must be type str".format(
            _LIBNAME, _DFVALWARN_N))
    if (not isinstance(func_n, str)):
        raise TypeError("{0}.{1}: error: func_n must be type str".format(
            _LIBNAME, _DFVALWARN_N))
    # check that if df_id is not "unknown" that df_id is an int
    if (df_id != "unknown" and not isinstance(df_id, int)):
        raise TypeError("{0}.{1}: error: df_id must be int; use function id()"
                        "".format(_LIBNAME, _DFVALWARN_N))
    # check that id_ismloc is boolean
    if (not isinstance(id_ismloc, bool)):
        raise TypeError("{0}.{1}: error: id_ismloc must be bool".format(
            _LIBNAME, _DFVALWARN_N))
    # check that col and row must be string or int
    if ((not isinstance(col, str)) and (not isinstance(col, int))):
        raise TypeError("{0}.{1}: error: col must be str or int".format(
            _LIBNAME, _DFVALWARN_N))
    if ((not isinstance(row, str)) and (not isinstance(row, int))):
        raise TypeError("{0}.{1}: error: row must be str or int".format(
            _LIBNAME, _DFVALWARN_N))
    # set the correct format for reporting the df_id or memory location of df
    # if id_ismloc is True
    if (id_ismloc == True):
        # if df_id is unknown
        if (df_id == "unknown"):
            id_fmt = " at 0x??"
        # else use normal format for id
        else:
            id_fmt = " at 0x{0:x}".format(df_id)
    # else id_ismloc is False
    else:
        # if df_id is unknown, use this format
        if (df_id == "unknown"):
            id_fmt = ", unknown id"
        # else use normal format for id
        else:
            id_fmt = ", id={0}".format(df_id)
    # set the correct format for columns and rows
    if (col != "??" and isinstance(col, str)):
        col = "'{0}'".format(col)
    col_fmt = col
    if (row != "??" and isinstance(row, str)):
        row = "'{0}'".format(row)
    row_fmt = row
    # print warning to stderr
    print("{0}.{1}: DataFrame df{2}: df[{3}][{4}] {5}".format(
        lib_n, func_n, id_fmt, col_fmt, row_fmt, qual), file = sys.stderr)
    return None

def log(df, cns, base = "e", inplace = True, overwrite = False, quiet = False):
    """
    function that takes the natural (or base k) log of specified columns from a
    pandas dataframe. can either insert these columns next to the original
    columns in the dataframe, or return a copy of the new dataframe with the
    newly generated log columns. generated columns will be named per the
    following convention: colname_[logk][ln]

    parameters:

    df          required dataframe to operate on
    cns         required parameter; either a single value or a list of values
                that are column names in the dataframe that should have their
                [natural] log or base k log taken.
    base        optional named parameter, default "e". can be set to integers
                for logarithms with different bases.
    inplace     optional named parameter, default True. can be set to False to
                force log() to return a modified copy of the DataFrame df. the
                function will return None is inplace is True, and will return
                the modified copy of the original DataFrame if inplace is False.
    overwrite   optional named parameter, default False. set to True to overwrite
                and rename the original columns in cns with the renamed and
                transformed columns.
    quiet       optional named parameter, default False. set to True to suppress
                warnings about NaN or nonpositive values for all  columns within
                cns.
    """
    # if df is None, raise ValueError
    if (df is None):
        raise ValueError("{0}.{1}: error: DataFrame required, None passed"
                         "".format(_LIBNAME, _LOG_N))
    # if df is not a DataFrame, raise TypeError
    if (not isinstance(df, pd.DataFrame)):
        raise TypeError("{0}.{1}: error: DataFrame required, {2} passed"
                        "".format(_LIBNAME, _LOG_N, type(df)))
    # check if inplace, overwrite, or quiet are boolean
    if (not isinstance(inplace, bool)):
        raise TypeError("{0}.{1}: error: bool required, {2} passed".format(
            _LIBNAME, _LOG_N, type(inplace)))
    if (not isinstance(overwrite, bool)):
        raise TypeError("{0}.{1}: error: bool required, {2} passed".format(
            _LIBNAME, _LOG_N, type(overwrite)))
    if (not isinstance(quiet, bool)):
        raise TypeError("{0}.{1}: error: bool required, {2} passed".format(
            _LIBNAME, _LOG_N, type(quiet)))
    # if inplace is False, set df to a deep copy of df
    if (inplace == False):
        df = df.copy()
    # check if cns is an iterable
    try:
        iter(cns)
        # if cns is a string, set cns to a list wrapping the string
        if (isinstance(cns, str)):
            cns = [cns]
        # else it is an iterable, so do nothing
    # if it's not an iterable, it's most likely a single integer or something
    # also wrap it in a list
    except TypeError:
        cns = [cns]
    # check base: if "e", set base to np.e, else check if the base is valid
    if (base == "e"):
        base = np.e
    # else if base is an int or a float
    elif (isinstance(base, int) or isinstance(base, float)):
        # check if base == 1 or <= 0
        if (base == 1 or base <= 0):
            raise ValueError("{0}.{1}: error: invalid logarithm base ({2})"
                             "".format(_LIBNAME, _LOG_N, base))
    # else raise TypeError
    else:
        raise TypeError("{0}.{1}: error: float base required, {2} passed"
                        "".format(_LIBNAME, _LOG_N, type(base)))
    # check that each column in cns is in df.columns
    # if a single column is not found
    col_err = False
    # list of columns that weren't found
    err_cols = []
    for cn in cns:
        # if not found, set col_err to True and append cn to err_cols
        if (cn not in df.columns):
            col_err = True
            err_cols.append(cn)
    # if col_err is True, raise KeyError and note how many columns are missing
    if (col_err == True):
        raise KeyError("{0}.{1}: error: columns {2} not found".format(
            _LIBNAME, _LOG_N, err_cols))
    # for each column, create a copy, forcibly convert to numeric (replace all
    # non-numeric values with NaN), and then process logarithms as necessary
    # before assigning resulting column to df
    for cn in cns:
        # if overwrite is True, apply to_numeric to df[cn]; any non-numeric
        # or blank values will be replaced with NaN
        if (overwrite == True):
            df.loc[:, cn] = pd.to_numeric(df[cn], errors = "coerce")
            col = df.loc[:, cn]
        # else create copy of series from the DataFrame and coerce to numeric
        else:
            col = pd.to_numeric(df[cn], errors = "coerce")
        # for each element in col
        for i in range(col.size):
            # if the element is NaN
            if (math.isnan(col.iloc[i])):
                # if quiet is False, print warning
                if (quiet == False):
                    _dfvalwarn(df, qual = "is NaN", lib_n = _LIBNAME,
                               func_n = _LOG_N, df_id = id(df), id_ismloc = True,
                               col = cn, row = i)
                # col[i] already NaN so don't do anything
            # else if element is 0
            elif (col.iloc[i] == 0):
                # if quiet is False, print warning
                if (quiet == False):
                    _dfvalwarn(df, qual = "is 0", lib_n = _LIBNAME,
                               func_n = _LOG_N, df_id = id(df), id_ismloc = True,
                               col = cn, row = i)
                # set col[i] to np.NINF
                col.iloc[i] = np.NINF
            # else if element is less than 0
            elif (col.iloc[i] <= 0):
                # if quiet is False, print warning
                if (quiet == False):
                    _dfvalwarn(df, qual = "< 0", lib_n = _LIBNAME,
                               func_n = _LOG_N, df_id = id(df), id_ismloc = True,
                               col = cn, row = i)
                # set col[i] to np.nan
                col.iloc[i] = np.nan
            # else calculate log value normally
            else:
                col.iloc[i] = math.log(col.iloc[i], base)
        # after taking the log of all values in col, assign it back to df
        # with the modified column name (as according to the base used)
        # if overwrite is True, rename inplace
        if (overwrite == True):
            # if natural log was taken
            if (base == np.e):
                df.rename(columns = {cn: "{}_log".format(cn)}, inplace = True)
            # else if base is an int
            elif (isinstance(base, int)):
                df.rename(columns = {cn: "{0}_log{1}".format(cn, base)},
                          inplace = True)
            # else if base is a float
            elif (isinstance(base, float)):
                df.rename(columns = {cn: "{0}_log{1:.2f}".format(cn, base)},
                          inplace = True)
        # else assign as new column
        else:
            # if natural log was taken
            if (base == np.e):
                df["{}_log".format(cn)] = col
            # else if base is an int
            elif (isinstance(base, int)):
                df["{0}_log{1}".format(cn, base)] = col
            # else if base is a float
            elif (isinstance(base, float)):
                df["{0}_log{1:.2f}".format(cn, base)] = col

    # if inplace is True, return None, else return the modified copy of df
    if (inplace == True):
        return None
    return df
