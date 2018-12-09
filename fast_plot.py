# module for fast graphing of multiple series generically. makes matplotlib a little
# more tractable and removes the need for multiple lines or a deep understanding
# of the object hierarchy in matplotlib.
#
# Changelog:
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
# fast_plot.xy_plot((a, b, c), ll__ = ["cheese", "bacon", "germs"],
#                   fout = "xy_plot.png", title = "silly graph",
#                   xlab = "axis of folly", ylab = ":)", tilt_y = 0)

import matplotlib.pyplot as plt

# library name
LIB_NAME = "fast_plot"

# function names
XY_PLOT_N = "plot"

# list of acceptable picture formats to save to
__IMG__EXTS = [".jpg", ".png"]

# graphing function; creates a plot and saves it to specified .png file. dimensions,
# x and y labels, and title may be specified. formatting cannot be controlled except
# for whether or not the y axis label is vertical or horizontal, which can be made 
# vertical with the option tilt_y (by default 90, so the y axis will be vertical)
# legend and graph line colors are automatically determined. sorry
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
def xy_plot(gs__, w = 8, h = 4.5, fout = None, ll__ = None, xlab = "default_xlab",
         ylab = "default_ylab", plab = "default_plab", title = "default_title",
         fontsize_x = None, fontsize_y = None, fontsize_t = None, tilt_y = 90,
         hide_x = False, hide_y = False):
    # if fout is not None
    if (fout != None):
        # if fout does not have an extension in __IMG__EXTS, raise error
        # split fout
        fout_s = fout.split(".")
        # if len(fout_s) is not 2 or invalid file extension, raise error
        if (len(fout_s) != 2 or
            (len(fout_s) == 2 and ("." + fout_s[1] not in __IMG__EXTS))):
            raise TypeError("{0}.{1}: error: file type restricted to {2}".format(
                LIB_NAME, XY_PLOT_N, __IMG__EXTS))
    # first check if gs__ is iterable
    try:
        iter(gs__)
    except TypeError:
        raise TypeError("{0}.{1}: error: required argument must be iterable".format(
            LIB_NAME, XY_PLOT_N))
    # parse each series in gs__
    for e in gs__:
        # if e is not iterable, raise TypeError
        try:
            iter(e)
        except TypeError:
            raise TypeError("{0}.{1}: error: element must be iterable".format(
                LIB_NAME, XY_PLOT_N))
        # check if each element of e is iterable
        for ee in e:
            try:
                iter(ee)
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
        raise IndexError("{0}.{1}: number of labels must equal number of plotted "
                         "series".format(LIB_NAME, XY_PLOT_N))
    # if height and width are nonpositive, print error and exit
    if (w < 1 or h < 1):
        raise ValueError("{0}.{1}: cannot have nonpositive dimension".format(LIB_NAME,
                                                                             XY_PLOT_N))
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
        raise ValueError("{0}.{1}: cannot have nonpositive font size".format(LIB_NAME,
                                                                             XY_PLOT_N))
    # make new figure w by h
    fg = plt.figure(figsize = (w, h))
    # if ll__ is None, set it to the default labels
    if (ll__ == None):
        ll__ = ["plot_{}".format(i) for i in range(len(gs__))]
    # plot all xy series in gs__
    for e, el in zip(gs__, ll__):
        plt.plot(*e, label = el)
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
