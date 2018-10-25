# makefile for rate models in . (rate_models)
#
# Changelog:
#
# 10-25-2018
#
# renamed log_transform.py and associated targets to to_lnr.py, added
# target for to_ln
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

# args for cir_main
CIR_MAIN_ARGS = #--help
# args for to_ln
TO_LN_ARGS = ./rate_data/treasury_3m_rates_1981-2018.csv DTB3 --quiet
# args for to_lnr
TO_LNR_ARGS = ./rate_data/treasury_3m_rates_1981-2018.csv DTB3 --quiet

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

# clean
clean:
	$(RM) -vf *~
