# makefile for rate models in . (rate_models)
#
# Changelog:
#
# 10-26-2018
#
# added more variables for data file names (so i don't have to keep
# copy-pasting them over and over again), and added data for new files
# containing yields on high yield bonds
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
CIR_MAIN_PY = cir_main.py
CIR_MAIN_DEPS = cir.py
TO_LN_PY = to_ln.py
TO_LNR_PY = to_lnr.py
NN_SHIFT_PY = nn_shift.py

# args for cir_main
CIR_MAIN_ARGS = #--help
# args for to_ln
TO_LN_ARGS = $(RATES_DDIR)/$(HY_Y0_CSV) BAMLHY --quiet
# args for to_lnr
TO_LNR_ARGS = $(RATES_DDIR)/$(HY_Y0_CSV) BAMLHY --quiet
# args for nn_shift
#NN_SHIFT_ARGS = $(RATES_DDIR)/$(TB_Y0_CSV) DTB3 --quiet 0.03
NN_SHIFT_ARGS = $(RATES_DDIR)/$(HY_Y0_CSV) BAMLHY --quiet

# other variables
# ./rate_data directory
RATES_DDIR = ./rate_data
# 3m treasury yields file (1981-2018)
TB_Y0_CSV = treasury_3m_yield_1981-2018.csv # DTB3 (data column header)
# ice boaml high yield yields (1996-2018)
HY_Y0_CSV = ice-boaml_us_hy_yield_1996-2018.csv # BAMLHY (data column header, renamed)

# dummy target
dummy:

# cir_main (python script to mimic cir process; uses cir.py)
cir_main: $(CIR_MAIN_PY) $(CIR_MAIN_DEPS) # i think this is unnecessary lol
	$(PYC) $(PYFLAGS) $(CIR_MAIN_PY) $(CIR_MAIN_ARGS)

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
