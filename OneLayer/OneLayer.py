# The driver for a program that generates and displays crystal aggregates consisting of a
# single layer of crystals on a rock substrate. The central idea is to try to get a
# visually plausible distribution of crystal sizes by picking those sizes from a
# probability distribution that crystals are really believed to follow, in this case a
# lognormal one. See my project notes from late December 2020 and early January 2021 for
# more about this idea.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   January 2021. Created by Doug Baldwin. Despite being part of a series of programs that
#     draw single-layer amethyst aggregates, this file doesn't substantially draw on
#     previous programs in that series.


from Substrate import Substrate
from Amethyst import Amethyst
from LogNormalDistribution import LogNormalDistribution
from UniformDistribution import UniformDistribution
from RecordedDistribution import RecordedDistribution
from RotatingScreenRenderer import RotatingScreenRenderer
from argparse import ArgumentParser
from math import pi




# Process command-line arguments.

parser = ArgumentParser( description="Generate and draw a single-layer amethyst aggregate" )

parser.add_argument( "-c", "--crystals", type=int, default=100, help="The number of crystals to create" )
parser.add_argument( "-s", "--scale", type=float, default=0.3, help="Scale factor from random distribution to crystal sizes" )
parser.add_argument( "-v", "--variation", type=float, default=0.4, help="Sigma parameter for crystal size distribution" )
parser.add_argument( "-r", "--replay", help="File containing recorded distributions for crystal sizes, positions, etc." )


arguments = parser.parse_args()


# Create a renderer for drawing the aggregate.

renderer = RotatingScreenRenderer( 3.0, 3.5 )


# Start by creating the substrate that the crystals grow on.

substrateMinX = -1.0
substrateMaxX = 1.0
substrateMaxY = 0.5
substrateMinZ = -1.0
substrateMaxZ = 1.0

base = Substrate( substrateMinX, substrateMaxX, 0.0, substrateMaxY, substrateMinZ, substrateMaxZ )

base.draw( renderer )


# Check to see if there's a "replay" file to take crystal parameters from. If
# there is, open it and get the distributions of crystal sizes, positions, etc.
# from it.

if arguments.replay :

	with open( arguments.replay ) as replayFile  :
		sizeDistribution = RecordedDistribution( replayFile )
		xDistribution = RecordedDistribution( replayFile )
		zDistribution = RecordedDistribution( replayFile )
		polarDistribution = RecordedDistribution( replayFile )
		azimuthDistribution = RecordedDistribution( replayFile )

else :

	sizeDistribution = LogNormalDistribution( arguments.variation )
	xDistribution = UniformDistribution( substrateMinX, substrateMaxX )
	zDistribution = UniformDistribution( substrateMinZ, substrateMaxZ )
	polarDistribution = UniformDistribution( 0.0, pi / 2.0 )
	azimuthDistribution = UniformDistribution( 0.0, 2.0 * pi )



# Generate the requested number of crystal sizes, taking them from a lognormal
# distribution and ordering them from largest to smallest.

sizes = []

for i in range( arguments.crystals ) :
	sizes.append( arguments.scale * sizeDistribution.sample() )

sizes.sort( reverse=True )


# Generate the actual crystals, in decreasing order of size. Place the crystals
# randomly across the substrate, as long as no crystal's center is inside
# another. As I place each crystal, I clip it against the ones already created,
# and draw it into the renderer. Because the random placement of crystals
# outside of all others takes longer and longer to find a place for new
# crystals as the number already placed grows, I also set an upper limit on how
# many placements I do before declaring the aggregate finished.

crystals = []

remainingPlacements = 50 * arguments.crystals
actualPlacements = 0

for crystalSize in sizes :
	
	
	# Trace for debugging.
	
	print( "OneLayer placing crystal of size {}".format( crystalSize ) )
	
	
	# Find a location for this crystal.
	
	isInCrystal = True
	while isInCrystal and remainingPlacements > 0 :
	
		place = [ xDistribution.sample(), substrateMaxY, zDistribution.sample() ]
		remainingPlacements -= 1
		
		isInCrystal = False
		
		for crystal in crystals :
			isInCrystal = isInCrystal or crystal.contains( place )
	
	
	# If I've used up all my placement opportunities, stop generating crystals
	# and go draw them.
	
	if remainingPlacements <= 0 :
		print( "Placement budget exhausted after {} crystals.".format( actualPlacements ) )
		break


	# Create the crystal at the location found, with random polar and
	# azimuth angles.
	
	polar = polarDistribution.sample()
	azimuth = azimuthDistribution.sample()
	
	newCrystal = Amethyst( place, polar, azimuth, crystalSize )

	print( "\tCrystal at ({0[0]:.3}, {0[1]:.3}, {0[2]:.3}) with polar angle {1} and azimuth angle {2}".format( place, polar, azimuth ) )
	
	
	# Every crystal gets clipped against the substrate.
	
	newCrystal.clipTo( base )
	
	
	# New crystals also get clipped against all previous ones.
	
	for oldCrystal in crystals :
		newCrystal.clipTo( oldCrystal )
	
	
	# Draw the crystal to the renderer and save it as part of the aggregate.
	
	newCrystal.draw( renderer )
	
	crystals.append( newCrystal )
	
	actualPlacements += 1


# Draw the aggregate.

renderer.draw()
