# The  driver for a program that generates and displays crystal aggregates consisting of a
# single layer of crystals on a rock substrate. The core idea is to model the development
# of individual crystals as they grow into and around each other in order to make the
# shapes of and abutments between crystals visually realistic. See my project notes from
# June 13 - 17, 2019 for more about this idea and the proposed program to test it.
#
# This driver processes command-line arguments and uses them and/or default values to
# create an aggregate and a renderer for it, then lets the crystals in the aggregate
# grow while the renderer draws them. By default the renderer is an animation renderer,
# so users can see the aggregate growing.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin. Despite being part of a series of programs that
#     draw single-layer amethyst aggregates, this file doesn't substantially draw on
#     previous programs in that series.


import Logger
from argparse import ArgumentParser




# The first thing to do is to get user requests for number of crystals, logging, etc. This
# requires a command-line argument parser....

parser = ArgumentParser()

parser.add_argument( "-c", "--crystals", nargs="*", type=float, action="append",
					 help="Provide position, orientation, and creation time for 0 or more crystals" )


# Get a logger for whatever sort of logging the user wants (default is no logging).

log = Logger.makeLogger( parser )


# Create a list of positions, orientations, and creation times for the crystals in this
# aggregate. The user can spell out the list by hand with the "--crystals" command-line
# option, or this program can generate the list randomly.

otherArguments = parser.parse_args()

if otherArguments.crystals :
	
	crystalSpecs = []
	
	print( "Grown crystals not actually reading crystal specifications." )

else :
	
	print( "Grown crystals not generating random crystal specifications." )
	crystalSpecs = []
