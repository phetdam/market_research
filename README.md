# market research

by Derek Huang

_last updated on: 12-23-2018_  
_file created on: 12-23-2018_

The market_research repo consists of useful financial models and data, useful Python scripts implementing the models, visualizing the results, or simply performing useful general purpose tasks, and some resulting plots.

## Directories

### data

Data directory, with some .csv files.

### lib

Shared general purpose code. Below is a list of modules and a brief description of what they do:

#### fast_plot.py

Wrapper around matplotlib that allows a flexible yet simply interface with the matplotlib.plot() function. Motivated by a need to quickly graph time series or two-dimensional data while offering a few graph customization options.

### options

Contains options pricing models, mostly for the American or European flavor. List of modules and a brief descriptions of each:

#### bopm.py

Implemention of the original Cox-Rox-Rubenstein binomial tree options pricing model. Plans to allow integration with stochastic volatility instead of constant volatility. 

### rate_models

Contains interest rate models. List of modeuls and a brief description of each:

#### short_rate_1f.py

Contains implementations for CIR and Vasicek one-factor interest rate models, as well as a very crude calibrating function. 

Note that this repository is a work in progress, and the contents and directory structure are subject to frequent changes. 