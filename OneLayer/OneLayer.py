# The driver for a program that generates and displays crystal aggregates consisting of a
# single layer of crystals on a rock substrate. The core idea is to model the development
# of individual crystals as they grow into and around each other in order to make the
# shapes of and abutments between crystals visually realistic. See my project notes from
# June 13 - 17, 2019 for more about this idea and the proposed program to test it.
#
# This driver processes command-line arguments and uses them and/or default values to
# create an aggregate and a renderer for it, then lets the crystals in the aggregate
# grow while the renderer draws them. By default the renderer is an animated renderer, so
# users can see the aggregate growing.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin. Despite being part of a series of programs that
#     draw single-layer amethyst aggregates, this file doesn't substantially draw on
#     previous programs in that series.


from AmethystAggregate import AmethystAggregate
from RotatingScreenRenderer import RotatingScreenRenderer
from CrystalSpec import CrystalSpec
import Logger
from argparse import ArgumentParser




# Carry out one step of growing an aggregate and drawing the result. The aggregate to
# grow and the renderer on which to display it are arguments to this function; there is no
# return value.

def growAggregate( aggregate, renderer ) :
	
	
	# Since the aggregate encapsulates the representation of the parts that need to grow,
	# draw, etc., this function just has to tell the aggregate to grow itself and then
	# draw itself.
	
	aggregate.grow()
	aggregate.draw( renderer )






# The main program starts by creating an argument parser for reading command-line arguments.

parser = ArgumentParser()

parser.add_argument( "-c", "--crystals", nargs="*", type=float, action="append",
					 help="Provide x, z, azimuth, polar angle, and creation time for 0 or more crystals" )

parser.add_argument( "-t", "--time", type=int, default=100, help="Specify the amount of simulated time the aggregate grows for" )


# Get a logger for whatever sort of logging the user wants (default is no logging).

log = Logger.makeLogger( parser )


# Create a list of positions, orientations, and creation times for the crystals in this
# aggregate. The user can spell out the list by hand with the "--crystals" command-line
# option, or this program can generate the list randomly.

otherArguments = parser.parse_args()

if otherArguments.crystals :
	
	# The user provided crystal specifications on the command line. Python's argument
	# parser delivers them as a list of lists, where each inner list is the arguments
	# following one "-c" in the command line. Ideally there will be one such group, which
	# will contain a multiple of 5 numbers (each crystal's x coordinate, z coordinate,
	# azimuth angle theta, polar angle phi, and the simulation step in which to create it),
	# but allow multiple groups with unexpected lengths (e.g., in case the user forgets
	# a creation time and adds it in a subsequent group). So start by flattening the
	# crystal specifications from the command line, then regroup them into groups of 5 for
	# later use.
	
	flatSpecs = []
	for group in otherArguments.crystals :
		flatSpecs += group
	
	crystalSpecs = []
	
	if len( flatSpecs ) % 5 == 0 :
		for i in range( 0, len(flatSpecs), 5 ) :
			crystalSpecs.append( CrystalSpec( flatSpecs[i], flatSpecs[i+1], flatSpecs[i+2], flatSpecs[i+3], flatSpecs[i+4] ) )
	
	else :
		print( "Error. Command-line crystal specification", flatSpecs, "should contain 5 values per crystal." )

else :
	
	print( "Grown crystals not generating random crystal specifications." )
	crystalSpecs = []


# Create the aggregate, including the amount of time it should grow for from the argument
# parser.

aggregate = AmethystAggregate( crystalSpecs, otherArguments.time, log )


# Create the renderer, giving it an initial viewer position and any triangles the as-yet
# ungrown aggregate has.

renderer = RotatingScreenRenderer( 2.5, 3, lambda r, dt : growAggregate( aggregate, r ) )
aggregate.draw( renderer )


# Finally, since the renderer does animation, telling it to draw kicks off a whole series
# of drawing followed by updating the aggregate followed by drawing it again, etc.

renderer.draw()
