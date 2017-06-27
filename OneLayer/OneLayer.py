# This program generates and displays crystal aggregates consisting of a single layer of
# crystals on a rock substrate. I describe this aggregate and the overall program
# requirements and design in the project notes for May 23 and 24, and June 8, 2017.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May 2017 -- Created by Doug Baldwin.


from Amethyst import Amethyst
from Substrate import Substrate
from RotatingScreenRenderer import RotatingScreenRenderer
from StaticScreenRenderer import StaticScreenRenderer
from Distribution import uniform4, halfNormal
from math import pi
from random import seed, uniform




# Initialize Python's random number generator.

seed()


# Create a renderer with which to display the aggregate.

renderer = RotatingScreenRenderer()
renderer.viewer( 0, 2.3, 3 )


# Create the substrate and add it to what the renderer will draw.

minX = -1								# Minimum and maximum X and Z coordinates on the substrate
maxX = 1
minZ = -1
maxZ = 1

topY = 0.5								# Y coordinate of top of substrate (bottom is automatically at y=0)

base = Substrate( minX, maxX, minZ, maxZ, topY )
base.addToRenderer( renderer )


# Create the crystals at random positions, sizes, and orientations. Positions, sizes, and
# orientations are all governed by probability distributions that give probabilities of
# crystals appearing at certain positions, or of having certain sizes or orientations at
# certain positions. Positions and sizes may be correlated, i.e., bigger crystals may
# appear at certain places on the substrate, so I draw position (x,y) and size (length
# along the crystallographic c and a axes) from a single 4-dimensional distribution. But
# I treat orientation angles (of the crystal's c axis relative to the global coordinate
# frame, given as angle theta clockwise from the x axis in the xz plane and angle phi
# above the xz plane) as independent of everything including each other, and so draw them
# from 1-dimensional distributions. After creating each crystal, I clip it to lie in the
# space above the substrate and add it to what the renderer will draw.

N_CRYSTALS = 100								# Number of crystals to generate

for i in range( N_CRYSTALS ) :

	
	# Generate a crystal.
	
	( x, z, c, a ) = uniform4( minX, maxX, minZ, maxZ, 0.1, 0.4, 0.1, 0.2 )
	theta = uniform( 0, 2 * pi )
	phi = halfNormal( pi / 2, -0.5 )
	
	crystal = Amethyst( x, topY, z, theta, phi, c, a )
	
	
	# Clip the faces of the crystal to lie a bit below the top of the substrate and a bit
	# inside its edges. Making these offsets depend on the crystal's size reduces the
	# chance of getting coincident overlapping faces that flicker when animated.
	
	sideGap = a / 100
	
	crystal.clip( 0, -1, 0, -(topY-0.005) )
	crystal.clip( -1, 0, 0, -(minX+sideGap) )
	crystal.clip( 1, 0, 0, maxX-sideGap )
	crystal.clip( 0, 0, -1, -(minZ+sideGap) )
	crystal.clip( 0, 0, 1, maxZ-sideGap )
	
	
	# Add the crystal to the renderer.
	
	crystal.addToRenderer( renderer )


# Draw the aggregate.

renderer.draw()
