# This class represents amethyst crystals for use in a program that generates and
# renders crystal aggregates consisting of a single layer of crystal on top of a
# substrate. I base these crystals on information from "mindat.org," particularly its
# "Quart no. 7" data and visualization.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May 2017 -- Created by Doug Baldwin.


from ConvexPolyhedron import ConvexPolyhedron, Vertex
from VectorOps import cross, orthogonalize3, normalize3
from SymmetryOps import transform4
from math import sin, cos, pi




class Amethyst( ConvexPolyhedron ) :
	
	
	
	
	# Initialize an amethyst crystal from the position of its center, its extent (half
	# length) along the c and a crystallographic axes, and the orientation of the c axis
	# relative to the global coordinate frame (given as an azimuthal angle theta and an
	# altitude angle phi).
	
	def __init__( self, x, y, z, theta, phi, cExtent, aExtent ) :
			
		
		# Tell the superclass what color amethysts are.
		
		super(Amethyst,self).__init__( [ 0.8, 0.3, 0.75, 0.55, 0.9, 100.0 ] )
		
		
		# Build a list of vertices for the amethyst. This amethyst is a hexagonal prism
		# with pyramidal ends. I define this geometry in a local coordinate frame in which
		# the crystallographic c axis aligns with the Cartesian y axis, one of the
		# crystallographic a axes aligns with the Cartesian x axis, and the center of the
		# crystal is at the origin. As I generate vertices, I put them into a list that
		# contains the apexes of the pyramids in its first two elements, then 6 pairs of
		# upper and lower vertices around the prism proper.
		
		# Start generating vertices by finding the local y coordinates of the apex points.
		# The pyramids extend one unit up the crystallographic c axis for each unit out
		# the crystallographic a axis, but the trick is that the units aren't the same in
		# the two dimensions.
		
		cToARatio = 1.1
		topApexY = cExtent + aExtent * cToARatio

		
		# Start the vertex list with the apexes. Note that I use homogeneous coordinates,
		# to make it easy to transform to the global coordinate frame later.
		
		vertices = [ [ 0, topApexY, 0, 1 ],
					 [ 0, -topApexY, 0, 1 ] ]
		
		
		# Add in vertices around the top and bottom of the prism.

		angleStep = pi / 3

		for i in range( 6 ) :
			angle = i * angleStep
			vertexX = aExtent * cos( angle )
			vertexZ = aExtent * sin( angle )
			vertices += [ [vertexX, cExtent, vertexZ, 1], [vertexX, -cExtent, vertexZ, 1] ]

		
		# It was easy to generate the amethyst in the local frame, but I have to convert
		# those results to the global frame in order to be use them. Build the
		# transformation, starting with a basis vector along the crystallographic c axis.
		
		c = [ cos(phi) * cos(theta), sin(phi), cos(phi) * sin(theta) ]
		
		
		# The crystallographic a1 (aka local x) axis is the global x axis rotated through
		# the azimuth angle and then made orthogonal to the c axis and normalized:
		
		a1 = normalize3( orthogonalize3( [ cos(theta), 0, sin(theta) ], c ) )
		
		
		# The last local axis is the local z axis and doesn't correspond to any
		# crystallographic axis. It's the normalized cross product of the a1 and c axes.
		
		localZ = normalize3( cross( a1, c ) )
		
		
		# Finally, the complete local-to-global transformation has the basis vectors as
		# its first 3 columns, and the origin point as its fourth column:
		
		transformation = [ [ a1[0], c[0], localZ[0], x ],
						   [ a1[1], c[1], localZ[1], y ],
						   [ a1[2], c[2], localZ[2], z ],
						   [ 0,     0,    0,         1 ] ]


		# Put everything into the global coordinate frame.
		
		globalVertices = [ Vertex( v[0], v[1], v[2] ) for v in transform4( vertices, transformation ) ]
				

		# Use the transformed vertices to define the faces of the crystal. Define them
		# in groups of 3, one group for each side of the prism. Each group contains a
		# triangle from the top pyramid, a rectangle from the side of the prism, and a
		# triangle from the bottom pyramid.

		for i in range( 6 ) :
			nextI = ( i + 1 ) % 6
			thisTop = globalVertices[ self.topIndex(i) ]				# Top corner of prism at current angle
			thisBottom = globalVertices[ self.bottomIndex(i) ]			# Bottom corner of prism at current angle
			nextTop = globalVertices[ self.topIndex(nextI) ]			# Top corner at next angle
			nextBottom = globalVertices[ self.bottomIndex(nextI) ]		# Bottom corner at next angle
			self.defineFace( [ globalVertices[0], nextTop, thisTop ] )
			self.defineFace( [ thisTop, nextTop, nextBottom, thisBottom ] )
			self.defineFace( [ thisBottom, nextBottom, globalVertices[1] ] )
	
	
	
	
	# Utility methods that compute indices into the list of vertices created in the
	# constructor. Specifically, these methods compute indices to the vertices at the
	# top and bottom of the prism at the i-th angle around the prism. The calculation is
	# based on the idea that the first 2 vertices in the list are the apexes of the
	# pyramids, and the remaining vertices are pairs from the prism, with a top vertex
	# first in each pair and the corresponding bottom vertex second.
	
	def topIndex( self, i ) :
		return 2 + 2 * i
	
	def bottomIndex( self, i ) :
		return 3 + 2 * i
