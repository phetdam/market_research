# makefile for rate models in . (rate_models)
#
# Changelog:
#
# 10-27-2018
#
# changed CIR_MAIN_DEPS to short_rate_1f.py, reflecting the change in
# name of cir.py to sr1fsim.py. added additional argument for specifying
# the type of model used in the simulation
#
# 10-26-2018
#
# added more variables for data file names (so i don't have to keep
# copy-pasting them over and over again), and added data for new files
# containing yields on high yield bonds. modified cir_main arguments
# so that each of run of cir_main calibrates a cir process to the input
# data, and runs the number of processes specified at the command line.
#
# note: be careful with spaces! newlines will be turned into a single
# space, which may cause a single argument to be interpreted as multiple
# arguments in the command line.
#
# 10-25-2018
#
# renamed log_transform.py and associated targets to to_lnr.py, added
# target for to_ln, nn_shift
#
# 10-24-2018
#
# added targets for cir_main (renamed cir), dummy, clean, log_transform
#

# c and python flags
CC = gcc
CFLAGS = -Wall -g
PYC = python
PYFLAGS = 

# targets and dependencies
SR1FSIM_PY = sr1fsim.py
SR1FSIM_DEPS = short_rate_1f.py
TO_LN_PY = to_ln.py
TO_LNR_PY = to_lnr.py
NN_SHIFT_PY = nn_shift.py

# args for sr1fsim
#SR1FSIM_ARGS = -cf=$(RATES_DDIR)/$(TB_Y0_CSV):DTB3 -mt=cir -np=5
SR1FSIM_ARGS = -cf=$(RATES_DDIR)/$(HY_Y0_CSV):BAMLHY -mt=vas -np=5
# args for to_ln
TO_LN_ARGS = $(RATES_DDIR)/$(HY_Y0_CSV) BAMLHY --quiet
# args for to_lnr
TO_LNR_ARGS = $(RATES_DDIR)/$(HY_Y0_CSV) BAMLHY --quiet
# args for nn_shift
# manual shift for treasury data to get rates above 0
#NN_SHIFT_ARGS = $(RATES_DDIR)/$(TB_Y0_CSV) DTB3 --quiet 0.03
NN_SHIFT_ARGS = $(RATES_DDIR)/$(HY_Y0_CSV) BAMLHY --quiet

# other variables
# ./rate_data directory
RATES_DDIR = ./rate_data
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
sr1fsim: $(SR1FSIM_PY) $(SR1FSIM_DEPS) # helps catch name changess
	$(PYC) $(PYFLAGS) $(SR1FSIM_PY) $(SR1FSIM_ARGS)

# to_ln (transforms values into log values)
to_ln: $(TO_LN_PY)
	$(PYC) $(PYFLAGS) $(TO_LN_PY) $(TO_LN_ARGS)

# to_lnr (transforms single column time series into a series of log returns)
to_lnr: $(TO_LNR_PY)
	$(PYC) $(PYFLAGS) $(TO_LNR_PY) $(TO_LNR_ARGS)

# nn_shift (takes the absolute value of the most negative value and shifts
# all values by that value, or if given a particular integer (must be > 0),
# will shift all values by that value)
nn_shift: $(NN_SHIFT_PY)
	$(PYC) $(PYFLAGS) $(NN_SHIFT_PY) $(NN_SHIFT_ARGS)

# clean
clean:
	$(RM) -vf *~
