# A class that represents substrates for crystal aggregates to "grow" on. These
# substrates are rectangular blocks of dull rock; clients specify the block's
# bounds in the X, Y, and Z dimensions, so substrates can be any size, but are
# always aligned with the axes.
#
# This class is part of my attempt to generate realistic amethyst aggregates by
# sampling crystal sizes from an appropriate probability distribution. See the
# project notes from 2021 for more on this project.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.




from Vertex import Vertex
from Edge import Edge
from Face import Face
from Polyhedron import Polyhedron
from ConvexPolyhedron import ConvexPolyhedron




class Substrate ( Polyhedron ) :
	
	
	
	
	# Initialize a substrate from its bounds in each of the 3 dimensions. The
	# first bound in each dimension should be the lower one.
	
	def __init__( self, lowX, highX, lowY, highY, lowZ, highZ ) :
		
		
		# Even though the substrate is a simple shape, for purposes of this
		# program it's a polyhedron, which is a union of convex polyhedra (in
		# this case one of them), which in turn are defined by faces, with
		# edges, which connect vertices. So build up the substrate from those
		# things.
		
		
		# Vertices:
		
		topLeftFront = Vertex( lowX, highY, highZ )
		topLeftBack = Vertex( lowX, highY, lowZ )
		topRightFront = Vertex( highX, highY, highZ )
		topRightBack = Vertex( highX, highY, lowZ )
		bottomLeftFront = Vertex( lowX, lowY, highZ )
		bottomLeftBack = Vertex( lowX, lowY, lowZ )
		bottomRightFront = Vertex( highX, lowY, highZ )
		bottomRightBack = Vertex( highX, lowY, lowZ )
		
		vertices = [ topLeftFront, topLeftBack, topRightFront, topRightBack,
					 bottomLeftFront, bottomLeftBack, bottomRightFront, bottomRightBack ]
		
		
		# Edges:
		
		topFront = Edge( topLeftFront, topRightFront )
		topRight = Edge( topRightFront, topRightBack )
		topBack = Edge( topRightBack, topLeftBack )
		topLeft = Edge( topLeftBack, topLeftFront )
		bottomFront = Edge( bottomLeftFront, bottomRightFront )
		bottomRight = Edge( bottomRightFront, bottomRightBack )
		bottomBack = Edge( bottomRightBack, bottomLeftBack )
		bottomLeft = Edge( bottomLeftBack, bottomLeftFront )
		leftFront = Edge( topLeftFront, bottomLeftFront )
		rightFront = Edge( topRightFront, bottomRightFront )
		rightBack = Edge( topRightBack, bottomRightBack )
		leftBack = Edge( topLeftBack, bottomLeftBack )
		
		edges = [ topFront, topRight, topBack, topLeft, bottomFront, bottomRight,
				  bottomBack, bottomLeft, leftFront, rightFront, rightBack, leftBack ]
		
		
		# Faces:
		
		top = Face( [ topFront, topRight, topBack, topLeft ] )
		bottom = Face( [ bottomFront, bottomLeft, bottomBack, bottomRight ] )
		front = Face( [ leftFront, bottomFront, rightFront, topFront ] )
		back = Face( [ leftBack, topBack, rightBack, bottomBack ] )
		left = Face( [ leftBack, bottomLeft, leftFront, topLeft ] )
		right = Face( [ rightFront, bottomRight, rightBack, topRight ] )
		
		faces = [ top, bottom, front, back, left, right ]
		
		
		# Finally, the polyhedra:
		
		substrateColor = [ 0.5, 0.5, 0.52, 1.0, 0.05, 1.0 ]
		
		cube = ConvexPolyhedron( faces, edges, vertices, substrateColor )
		super().__init__( [cube] )
