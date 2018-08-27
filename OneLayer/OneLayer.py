# This program generates and displays crystal aggregates consisting of a single layer of
# crystals on a rock substrate. 

# Copyright (C) 2017, 2018 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May-June, 2018 -- Version that "adaptively sizes" crystals, i.e., lets them be as
#     big as possible until they butt up against their neighbors, created by Doug
#     Baldwin. See project notes from May 17 through 31, 2018 for how the design of this
#     version and how its main algorithmic ideas developed.
#
#   May 2017 -- Original version created by Doug Baldwin; see project notes for May 23 and
#     24, and June 8, 2017 for the original requirements and design.


from Amethyst import Amethyst
import TwoDTree
from TwoDTree import TwoDEmptyTree
from Substrate import Substrate
from Logger import makeLogger
from RotatingScreenRenderer import RotatingScreenRenderer
from StaticScreenRenderer import StaticScreenRenderer
from VectorOps import add3, subtract3, scale3, dot3
from MathUtilities import lessOrNearlyEqual, infinity
from random import uniform, seed
from math import pi
import sys




# A utility function that determines whether a 2D point is inside or on an axis-parallel
# rectangle, returning True if it is and False if not. Because the rectangle is parallel
# to the axes, I define it by it minimum and maximum x and z coordinates (the point and
# rectangle are nominally in the xz plane). I define the point as a 2-element list
# containing the x and z coordinates.

def inRect( point, minX, maxX, minZ, maxZ ) :
	
	return     lessOrNearlyEqual( minX, point[0] ) \
		   and lessOrNearlyEqual( point[0], maxX ) \
		   and lessOrNearlyEqual( minZ, point[1] ) \
		   and lessOrNearlyEqual( point[1], maxZ )




# A function that figures out what a particular crystal neighbors in a 2D tree. Once this
# function knows the neighbors, it gives the crystal and its neighbors clipping planes.
# This function's last 4 parameters are the bounds of the substrate on which the crystal
# grows, to be used as clipping planes if there is no neighbor in some directions.

def findNeighbors( xtal, tree, minX, maxX, minZ, maxZ ) :
	
	
	# A utility function that finds the D coefficient in clipping planes' equations.
	# Given a point, a direction vector, and a distance to move from the point in that
	# direction (given as a fraction of the vector's length) in order to reach a new
	# point, this function returns a D value for a plane that has the direction vector
	# as a normal and that passes through the new point.
	
	def calculateD( point, direction, distance ) :
		newPoint = add3( point, scale3( direction, distance ) )
		return dot3( newPoint, direction )
	
	
	# Find the triangles that define the crystal's footprint in the xz plane, then get
	# the nearest neighbor in each triangle's direction.
	
	triangles = xtal.getFootprint()
	
	for face in triangles :
		
		( neighbor, t ) = tree.getNeighbor( face, infinity(), None )
		
		
		# If there really is a nearest neighbor, make a clipping plane between it and this
		# amethyst. Otherwise clip to the side(s) of the substrate that this triangle
		# intersects.
		
		if neighbor :
			
			
			# Clip the crystal to a plane in between it and a neighbor. The plane should
			# be the same regardless of which crystal is the neighor, so that when the
			# neighbor eventually finds this amethyst as a neighbor, the neighbor will get
			# the same clipping plane this amethyst gets now. But it's not completely sure
			# that the neighbor will find this amethyst as a neighbor, so assign the
			# clipping plane to both crystals now (but with opposite-facing normals) to
			# be safe. If these amethysts find each other as neighbors again, the plane
			# will be detected as a duplicate then.
			#   For now, I take the clipping plane to be halfway between the centers of
			# the amethysts, and perpendicular to the line between their centers. To
			# calculate its coefficients, I find a vector from this amethyst to the
			# neighbor; that vector will be the normal to the plane, conveniently
			# pointing away from this amethyst as the normal to a clipping plane should.
			# The point just slightly less than halfway along the vector from this
			# amethyst is a point on the plane (slightly less than halfway to avoid visual
			# artifacts if this amethyst and the neighbor have faces in exactly the same
			# place when drawn). Given that point and the normal, the D coefficient for
			# the plane is just the dot product of the normal and the point. Similar
			# calculations with a point slightly more than halfway between the amethysts
			# give me a D coefficient for the neighbor's clipping plane.
			
			here =  xtal.getPosition()
			hereToNeighbor = subtract3( neighbor.getPosition(), here )
			hereD = calculateD( here, hereToNeighbor, 0.499 )
			neighborD = calculateD( here, hereToNeighbor, 0.501 )
			
			xtal.addClippingPlane( hereToNeighbor[0], hereToNeighbor[1], hereToNeighbor[2], hereD )
			neighbor.addClippingPlane( -hereToNeighbor[0], -hereToNeighbor[1], -hereToNeighbor[2], -neighborD )
			
		
		else :
			
			
			# Clip the crystal to some sides of the substrate. Define lines in xz along
			# those sides, then find the side the first (counterclockwise) side of this
			# triangle intersects. Walk clockwise around the substrate from there until
			# finding a side intersected by the clockwise side of the triangle. All
			# substrate sides between those two intersections become clipping planes for
			# this crystal. All lines and clipping planes are slightly inside the
			# substrate to avoid flicker if I were to draw crystals and substrates with
			# faces in exactly the same plane; lines are defined as triples of
			# coefficients for equations of the form ax + bz = c, with the vector <a,b>
			# pointing out of the substrate for compatibility with normal vectors for
			# clipping planes.
			
			shrink = 0.99
			insideMinX = minX * shrink
			insideMaxX = maxX * shrink
			insideMinZ = minZ * shrink
			insideMaxZ = maxZ * shrink
			
			substrateLines = [ [ 0.0, -1.0, -insideMinZ ],
							   [ 1.0, 0.0, insideMaxX ],
							   [ 0.0, 1.0, insideMaxZ ],
							   [ -1.0, 0.0, -insideMinX ] ]
			
			
			# Find the first side of the substrate intersected by this triangle.
			
			for start in range( len(substrateLines) ) :
				
				line = substrateLines[ start ]
				
				( t1, t2 ) = face.lineT( line[0], line[1], line[2] )
				
				if t1 < sys.float_info.max :
					hit1 = face.side1Pt( t1 )
					if inRect( hit1, insideMinX, insideMaxX, insideMinZ, insideMaxZ ) :
						break
			
			
			# The first side of the triangle intersects side "start" of the substrate;
			# check subsequent sides until finding one intersected by the second side
			# of the triangle. Add a clipping plane corresponding to each substrate side
			# checked.
			
			for stop in range( start, start + len(substrateLines) ) :
				
				line = substrateLines[ stop % len(substrateLines) ]
				
				xtal.addClippingPlane( line[0], 0.0, line[1], line[2] )
				
				( t1, t2 ) = face.lineT( line[0], line[1], line[2] )
				
				if t2 < sys.float_info.max :
					hit2 = face.side2Pt( t2 )
					if inRect( hit2, insideMinX, insideMaxX, insideMinZ, insideMaxZ ) :
						break




# Initialize Python's random number generator.

seed()


# Create a logger to record what this run does (although makeLogger looks at command-line
# arguments to decide whether this run should be recorded, so just because there's a
# logger that looks like it's logging, it might not be).

log = makeLogger()


# Create a renderer with which to display the aggregate.

renderer = RotatingScreenRenderer()
renderer.viewer( 0, 3, 3 )


# Create the substrate and add it to what the renderer will draw.

minX = -1								# Minimum and maximum X and Z coordinates on the substrate
maxX = 1
minZ = -1
maxZ = 1

topY = 0.5								# Y coordinate of top of substrate (bottom is automatically at y=0)

base = Substrate( minX, maxX, minZ, maxZ, topY )
base.addToRenderer( renderer )


# Create the crystals at random positions and orientations. Positions are taken from a
# uniform probablity distribution over the top of the substrate. Orientations consist
# of an azimuthal angle for the crystal's a1 crystallographic axis (and also the projection
# onto the xz plane of the crystallographic c axis) counterclockwise from the global x
# axis, and a polar angle for the crystallographic c axis down from the global y axis.
# Both angles come from uniform probability distributions, the azimuth angle between 0 and
# 2 pi radians and the altitude between 0 and pi/2. Once I know each crystal's position
# and orientation I find its neighbors, from which I calculate its size. With sizes known,
# I can generate the actual crystal objects, clip them to their neighbors, and finally
# add them to the renderer for drawing.

N_CRYSTALS = 100								# Number of crystals to generate

crystals = TwoDEmptyTree( TwoDTree.X )			# An initially empty 2D tree to arrange crystals by position


# Generate positions and orientations, and give each amethyst a clipping plane just below
# the top of the substrate since there's no point in drawing parts of the amethyst below
# there.

for i in range( N_CRYSTALS ) :
	
	x = uniform( minX, maxX )
	z = uniform( minZ, maxZ )
	theta = uniform( 0, 2 * pi )				# Azimuthal angle
	phi = uniform( 0, pi / 2 )					# Altitude angle
	
	newAmethyst = Amethyst( x, topY, z, theta, phi )
	newAmethyst.addClippingPlane( 0.0, -1.0, 0.0, -0.99 * topY )
	crystals = crystals.insert( newAmethyst )
	
	newAmethyst.log( log )

# amethyst1 = Amethyst( 0.0, topY, -0.3, 0.0, 0.0 )
# amethyst1.addClippingPlane( 0.0, -1.0, 0.0, -0.99 * topY )
# crystals = crystals.insert( amethyst1 )
# amethyst1.log( log )
#
# amethyst2 = Amethyst( 0.0, topY, 0.0, 0.0, 0.0  )
# amethyst2.addClippingPlane(  0.0, -1.0, 0.0, -0.99 * topY )
# crystals = crystals.insert( amethyst2 )
# amethyst2.log( log )
#
# amethyst3 = Amethyst( -0.1, topY, 0.03, -16.0 * pi / 180.0, 0.0  )
# amethyst3.addClippingPlane(  0.0, -1.0, 0.0, -0.99 * topY )
# crystals = crystals.insert( amethyst3 )
# amethyst3.log( log )


# Find neighbors and set up corresponding clipping planes. This is just a matter of
# mapping a neighbor-finding function over the crystals in the 2D tree. Measure the
# time this takes as a test of whether the code complexity of 2D trees that only look
# at necessary subtrees as opposed to blindly checking both subtrees when finding
# neighbors pays off in shorter running times.

timer = log.startTimer()
crystals.traverse( lambda xtal: findNeighbors( xtal, crystals, minX, maxX, minZ, maxZ ) )
log.stopTimer( timer, "Time to find neighbors (seconds)" )


# Size and clip the crystals.

crystals.traverse( lambda xtal : xtal.build() )


# Write the log for this session.

log.writeAll()


#  Draw the crystals and substrate.

crystals.traverse( lambda xtal : xtal.addToRenderer( renderer ) )

renderer.draw()
