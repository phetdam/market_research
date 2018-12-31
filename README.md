# market research

by Derek Huang

_last updated on: 12-31-2018_  
_file created on: 12-23-2018_

![./readme_banner.png](./readme_banner.png)

The market_research repo consists of useful financial models and data, useful Python scripts implementing the models, visualizing the results, or simply performing useful general purpose tasks, and some resulting plots.

## Directories

### data

Data directory, with some .csv files.

### lib

Shared general purpose code. Below is a list of modules and a brief description of what they do:

 * __data_transform:__ Contains functions for performing transformations on data in a pandas DataFrame, for example taking the natural log of values in a column while ignoring values that are NaN values or outside of the natural log function's domain.
 * __fast_plot:__ Simple and flexible wrapper around matplotlib.plot(). Motivated by a need to quickly graph time series or two-dimensional data while also having a few customization options available.

### options

Contains options pricing models, mostly for the American or European flavor. List of modules and a brief descriptions of each:

 * __bopm:__ Implemention of the original Cox-Rox-Rubenstein binomial tree options pricing model. Plans to allow integration with stochastic volatility instead of constant volatility.

### plots

Contains various plots created from running the models.

### rate_models

Contains interest rate models. List of modules and a brief description of each:

 * __short_rate_1f:__ Contains implementations for CIR and Vasicek one-factor interest rate models, as well as a very crude calibrating function. 

The top-level directory contains entry points and a Makefile configured to make those targets with predefined arguments. Below is a list of targets and a brief description of each:

 * __sr1fsim:__ Simulates a few paths of a specifiable single-factor short rate model. Currently configured to simulate 5 paths of a Cox-Ingersoll-Ross process, (crudely) calibrated off of 3m Treasury yields. 
 * __xy_grapher:__ Plots two-dimensional xy graphs (hence the name) from .csv file columns specified in a required configuration file. Currently configured to graph binomial options prices against market calls and puts on SPY expiring 03-15-2019.

Note that this repository is a work in progress, and the contents and directory structure are subject to frequent changes. 