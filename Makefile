# top level makefile with targets for anything that should be user executed
#
# Changelog:
#
# 01-01-2019
#
# changed xy_grapher config back to original SPY 03-15-2019 options config.
#
# 12-31-2018
#
# happy new year's eve! corrected some spacing.
#
# 12-19-2018
#
# added target for config file used by options_grapher, and renamed
# options_grapher to xy_grapher. its usage showed potential for more general
# applications.
#
# 01-01-2019
#
# happy new year! modified configuration for xy_grapher.
#
# 12-09-2018
#
# initial creation. includes targets for sr1fsim and options_grapher.
#

# c and python flags
CC = gcc
CFLAGS = -Wall -g
PYC = python
PYFLAGS =

# directory targets
# overall data directory
DATA_DIR = ./data
# rate_models dir
RATE_MODELS_DIR = ./rate_models

# targets
SR1FSIM_T = sr1fsim
XY_GRAPHER_T = xy_grapher

# deps
SR1FSIM_DEPS = $(RATE_MODELS_DIR)/short_rate_1f.py

# args
SR1FSIM_ARGS = -cf=$(DATA_DIR)/$(TB_Y0_CSV):DTB3 -mt=cir -np=5
#SR1FSIM_ARGS = -cf=$(DATA_DIR)/$(HY_Y0_CSV):BAMLHY -mt=cir -np=5
OPTIONS_GRAPHER_ARGS = ./options/spy_03-15-2019_bopm.xyc

# other variables
# 3m treasury yields file (1981-2018), DTB3 is main data column
TB_Y0_CSV = treasury_3m_yield_1981-2018.csv
# ice boaml high yield yields (1996-2018), BAMLHY is renamed main data col
HY_Y0_CSV = ice-boaml_us_hy_yield_1996-2018.csv
# ice boaml bbb option-adjusted spread (1996-2018), BAMLBBB is the main
# data column (renamed from original)
BBB_OAS0_CSV = ice-boaml_us_bbb_oas_1996-2018.csv

# dummy target
dummy:

# sr1fsim (python script to simulate short rate using one-factor model)
$(SR1FSIM_T): $(SR1FSIM_T).py $(SR1FSIM_DEPS) # helps catch name changes
	$(PYC) $(PYFLAGS) $(SR1FSIM_T).py $(SR1FSIM_ARGS)

# options_grapher, a python script to graph the actual and modeled options
# prices to graphically illustrate their differences
$(XY_GRAPHER_T): $(XY_GRAPHER_T).py
	$(PYC) $(PYFLAGS) $(XY_GRAPHER_T).py $(OPTIONS_GRAPHER_ARGS)

# clean
clean:
	$(RM) -vf *~
