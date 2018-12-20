# module for fast graphing of multiple series generically. makes matplotlib a little
# more tractable and removes the need for multiple lines or a deep understanding
# of the object hierarchy in matplotlib.
#
# Changelog:
#
# 12-20-2018
#
# added error checking to make sure that appropriate exceptions are raised when there
# the given formats are zero characters in length
#
# 12-19-2018
#
# changed XY_PLOT_N to "xy_plot" to reflect function name change. added capability to
# specify either a broad type of plot format with a single string, or a list to
# specify individual formats for each single xy-series. changed __IMG__EXTS to
# _IMG_EXTS; did not know about the name mangling before. updated silly sample usage.
#
# 12-09-2018
#
# initial creation. method allows for plotting multiple pairs of series, setting the
# x, y, title, and legend labels, tilting the y axis an arbitrary number of degrees,
# changing the font size of x, y, and title, saving to file, and changing the width
# and height of the plot. not comprehensive, but has enough features for basic needs.
#
# silly sample usage:
#
# import fast_plot
# a = [[x for x in range(10)], [x for x in range(10)]]
# b = ([x for x in range(15)], [x ** 1.4 for x in range(15)])
# c = [[x for x in range(15)], [-x ** 1.5 for x in range(15)]]
# fmt = ["m.", "g-", "c^"]
# fast_plot.xy_plot((a, b, c), ll__ = ["cheese", "bacon", "germs"], fmt_ = fmt,
#                   fout = "xy_plot.png", title = "silly graph",
#                   xlab = "axis of folly", ylab = ":)", tilt_y = 0)

import matplotlib.pyplot as plt

# library name
LIB_NAME = "fast_plot"

# function names
XY_PLOT_N = "xy_plot"

# list of acceptable picture formats to save to
_IMG_EXTS = [".jpg", ".png"]

# flag indicating that graph colors/formats should be automatically selected
AUTO_FORMAT = "AUTO_FORMAT"

# graphing function; creates a plot and saves it to specified .png file. dimensions,
# x and y labels, and title may be specified. formatting cannot be controlled except
# for whether or not the y axis label is vertical or horizontal, which can be made 
# vertical with the option tilt_y (by default 90, so the y axis will be vertical)
# legend is automatically determined, but it is optional to pass manual specifications
# for each xy-series or for all the series as a whole.
#
# list of plot format specifiers:
# https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
#
# parameters:
#
# gs__        list of series pairs to graph; each pair must be in the form of (x_series,
#             y_series) or [x_series, y_series]; both x_series and y_series in one
#             tuple/list. full list would be [[x_1, y_1], [x_2, y_2] ...]
#             each tuple's x and y series must have matching lengths.
# w, h        width and height of image (default w = 8, h = 4.5)
# fout        output file, default None; if None, the figure will not be saved to file.
# ll__        list of legend labels; default ll__ = None. if None, will label each line
#             in the legend as "plot_k" where k is the position of the tuple in qs__
# fmt_        format for either each individual xy-series or for all the series. the
#             default value for fmt_ is specified by AUTO_FORMAT
#             starting from 0. len(ll__) must equal len(gs__).
# xlab        x label, default xlab = "default_xlab"; can make empty by passing None
# ylab        y label, default ylab = "default_ylab"; can make empty by passing None
# title       title, default title = "default_title"; can make empty by passing None
# fontsize_x  size of x label font; default None
# fontsize_y  size of y label font; default None
# fontsize_t  size of title label font; default None
# tilt_y      default 90 (vertical y axis), set to 0 for horizontal y axis
# hide_x      hide x axis but not x label (default False)
# hide_y      hide y axis but not y label (default False)
#
# returns the saved figure
def xy_plot(gs__, w = 8, h = 4.5, fout = None, ll__ = None, fmt_ = AUTO_FORMAT,
            xlab = "default_xlab", ylab = "default_ylab", title = "default_title",
            fontsize_x = None, fontsize_y = None, fontsize_t = None, tilt_y = 90,
            hide_x = False, hide_y = False):
    # if fout is not None
    if (fout != None):
        # if fout does not have an extension in _IMG_EXTS, raise error
        # split fout
        fout_s = fout.split(".")
        # if len(fout_s) is not 2 or invalid file extension, raise error
        if (len(fout_s) != 2 or
            (len(fout_s) == 2 and ("." + fout_s[1] not in _IMG_EXTS))):
            raise TypeError("{0}.{1}: error: file type restricted to {2}".format(
                LIB_NAME, XY_PLOT_N, _IMG_EXTS))
    # first check if gs__ is iterable, but not a string
    try:
        iter(gs__)
        if (isinstance(gs__, str)):
            raise TypeError("{0}.{1}: error: required argument must be non-string "
                            "iterable".format(LIB_NAME, XY_PLOT_N))
    except TypeError:
        raise TypeError("{0}.{1}: error: required argument must be iterable".format(
            LIB_NAME, XY_PLOT_N))
    # parse each series in gs__
    for e in gs__:
        # if e is not iterable, raise TypeError
        try:
            iter(e)
            # check that e is not a string
            if (isinstance(e, str)):
                raise TypeError("{0}.{1}: error: element must be non-string "
                                "iterable".format(LIB_NAME, XY_PLOT_N))
        except TypeError:
            raise TypeError("{0}.{1}: error: element must be iterable".format(
                LIB_NAME, XY_PLOT_N))
        # check if each element of e is iterable
        for ee in e:
            try:
                iter(ee)
                # check that ee is not a string
                if (isinstance(e, str)):
                    raise TypeError("{0}.{1}: error: non-string iterable expected "
                                    "in element".format(LIB_NAME, XY_PLOT_N))
            except TypeError:
                raise TypeError("{0}.{1}: error: iterable expected in element".format(
                    LIB_NAME, XY_PLOT_N))
        # if e is not length 2, we got a problem
        if (len(e) != 2):
            raise IndexError("{0}.{1}: error: iterable element must have length 2".format(
                LIB_NAME, XY_PLOT_N))
        # if it is length 2 but the series not of the same length, raise error
        if (len(e[0]) != len(e[1])):
            raise IndexError("{0}.{1}: error: x and y series of element must have same "
                             "length".format(LIB_NAME, XY_PLOT_N))
    # if ll__ is not None and gs__ and ll__ are not the same length, raise error
    if ((ll__ != None) and (len(gs__) != len(ll__))):
        raise IndexError("{0}.{1}: error: number of labels must equal number of plotted "
                         "series".format(LIB_NAME, XY_PLOT_N))
    # boolean True if fmt_ is iterable but NOT a string, False if not
    is_fmt_iterable = None
    # if fmt_ is not AUTO_FORMAT
    if (fmt_ != AUTO_FORMAT):
        # check if fmt_ is an iterable
        # if fmt_ is iterable
        try:
            iter(fmt_)
            # if fmt_ is a string
            if (isinstance(fmt_, str)):
                # if fmt_ (str) is less than 1 character, raise error
                if (len(fmt_) < 1):
                    raise IndexError("{0}.{1}: error: length of non-iterable fmt_ must "
                                     "be positive".format(LIB_NAME, XY_PLOT_N))
                # if fmt_ (str) is more than 2 characters, raise error
                if (len(fmt_) > 2):
                    raise IndexError("{0}.{1}: error: length of non-iterable fmt_ must "
                                 "be two characters or less".format(LIB_NAME, XY_PLOT_N))
                # if all tests pass, set is_fmt_iterable to False
                is_fmt_iterable = False
            # else fmt_ is a non-string iterable
            else:
                # for each element, make sure it is a string of length 2 max (defer
                # checking if the formats are correct to the actual library)
                for e in fmt_:
                    # if e is not a string
                    if (not isinstance(e, str)):
                        raise TypeError("{0}.{1}: error: elements of iterable fmt_ must "
                                        "be of type str".format(LIB_NAME, XY_PLOT_N))
                    # if length of e < 1
                    if (len(e) < 1):
                        raise IndexError("{0}.{1}: error: elements of iterable fmt_ must "
                                         "be at least one character".format(
                                             LIB_NAME, XY_PLOT_Nx))
                    # if length of e > 2
                    if (len(e) > 2):
                        raise IndexError("{0}.{1}: error: elements of iterable fmt_ must "
                                         "be two characters or less".format(
                                             LIB_NAME, XY_PLOT_N))
                    # if fmt_ is iterable but not of the same length as gs__, raise error
                    if (len(fmt_) != len(gs__)):
                        raise IndexError("{0}.{1}: error: number of format specifiers "
                                         "must equal number of plotted series".format(
                                             LIB_NAME, XY_PLOT_N))
                # if all tests pass, set is_fmt_iterable to True
                is_fmt_iterable = True
                
        # else fmt_ is not iterable; raise type error
        except TypeError:
            raise TypeError("{0}.{1}: error: non-iterable fmt_ must be type of "
                            "str".format(LIB_NAME, XY_PLOT_N))
    # if height and width are nonpositive, print error and exit
    if (w < 1 or h < 1):
        raise ValueError("{0}.{1}: error: cannot have nonpositive dimension".format(
            LIB_NAME, XY_PLOT_N))
    # if xlab, ylab, or title are None, make them "" instead
    if (xlab == None):
        xlab = ""
    if (ylab == None):
        ylab = ""
    if (title == None):
        title = ""
    # check that fontsizes are above 0 if any of them are not None
    if ((fontsize_x != None and fontsize_x < 1) or
        (fontsize_y != None and fontsize_y < 1) or
        (fontsize_t != None and fontsize_t < 1)):
        raise ValueError("{0}.{1}: error: cannot have nonpositive font size".format(
            LIB_NAME, XY_PLOT_N))
    # make new figure w by h
    fg = plt.figure(figsize = (w, h))
    # if ll__ is None, set it to the default labels
    if (ll__ == None):
        ll__ = ["plot_{}".format(i) for i in range(len(gs__))]
    # plot all xy series in gs__
    # if fmt_ is an iterable
    if (is_fmt_iterable == True):
        # plot all xy series, using fmt_ formats (let library catch invalid formats)
        for e, el, ef in zip(gs__, ll__, fmt_):
            plt.plot(*e, ef, label = el)
    # else if fmt_ is not iterable
    else:
        # if fmt_ is equal to AUTO_FORMAT
        if (fmt_ == AUTO_FORMAT):
            # plot all xy series, letting pyplot decide format and colors
            for e, el in zip(gs__, ll__):
                plt.plot(*e, label = el)
        # else it is not equal to AUTO_FORMAT, so use the manual format for each
        # xy-series being plotted
        else:
            for e, el in zip(gs__, ll__):
                plt.plot(*e, fmt_, label = el)
    # set x label; use default font size if fontsize_x is None
    if (fontsize_x == None):
        plt.xlabel(xlab)
    else:
        plt.xlabel(xlab, fontsize = fontsize_x)
    # set y label (rotate by 90 or 0); use default font size if fontsize_y is None
    if (fontsize_y == None):
        plt.ylabel(ylab, rotation = tilt_y)
    else:
        plt.ylabel(ylab, rotation = tilt_y, fontsize = fontsize_y)
    # graph title; use default font size if fontsize_t is None
    if (fontsize_t == None):
        plt.title(title)
    else:
        plt.title(title, fontsize = fontsize_t)
    # if hide_x is True, hide x axis ticks
    if (hide_x == True):
        #fg.gca().axes.get_xaxis().set_visible(False)
        plt.xticks([])
    # if hide_y is True, hide y axis
    if (hide_y == True):
        #fg.gca().axes.get_yaxis().set_visible(False)
        plt.yticks([])
    # show legend on plot
    plt.legend()
    # save to fout if fout is not None
    if (fout != None):
        plt.savefig(fout)
    # return figure
    return fg

if (__name__ == "__main__"):
    print("{0}: do not run in standalone mode.".format(LIB_NAME))
