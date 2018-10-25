# makefile for rate models in . (rate_models)
#
# Changelog:
#
# 10-24-2018
#
# added targets for cir_main (renamed cir), dummy, clean
#

# c and python flags
CC = gcc
CFLAGS = -Wall -g
PYC = python
PYFLAGS = 

# targets and dependencies
CIR_MAIN_PY = cir_main.py
CIR_MAIN_DEPS = cir.py

# args for CIR_PY
CIR_MAIN_ARGS = #--help

# dummy target
dummy:

# cir_main (python script to mimic cir process; uses cir.py)
cir_main: $(CIR_MAIN_PY) $(CIR_MAIN_DEPS) # i think this is unnecessary lol
	$(PYC) $(PYFLAGS) $(CIR_MAIN_PY) $(CIR_MAIN_ARGS)

# clean
clean:
	$(RM) -vf *~
