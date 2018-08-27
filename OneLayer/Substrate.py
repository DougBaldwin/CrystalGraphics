# This class represents a rocky substrate for a layer of crystals. As such, it represents
# one of the main structures in a model of crystal aggregates consisting of such layers on
# a substrate. See file "OneLayer.py" for more information about a program that models and
# renders such an aggregate.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May 2018 -- Unused "OLD_addToRenderer" method removed by Doug Baldwin.
#
#   May 2017 -- Created by Doug Baldwin.


from ConvexPolyhedron import ConvexPolyhedron, Vertex




class Substrate( ConvexPolyhedron ) :
	
	
	
	
	# Initialize a substrate from its bounds in the X and Z dimensions and its upper
	# bound in the Y dimension (the lower bound is always at y = 0).
	
	def __init__( self, minX, maxX, minZ, maxZ, maxY ) :
		
		
		# Tell the superclass what color the substrate is.
		
		super(Substrate,self).__init__( [ 0.45, 0.45, 0.5, 1, 0.1, 1 ] )
		
		
		# Define the substrate's faces and vertices. The substrate is a rectangular
		# block, so has 6 faces defined by 8 vertices.
		
		leftBottomBack = Vertex( minX, 0, minZ )
		leftBottomFront = Vertex( minX, 0, maxZ )
		leftTopBack = Vertex( minX, maxY, minZ )
		leftTopFront = Vertex( minX, maxY, maxZ )
		rightBottomBack = Vertex( maxX, 0, minZ )
		rightBottomFront = Vertex( maxX, 0, maxZ )
		rightTopBack = Vertex( maxX, maxY, minZ )
		rightTopFront = Vertex( maxX, maxY, maxZ )
		
		self.defineFace( [ leftBottomFront, rightBottomFront, rightTopFront, leftTopFront ] )		# Front
		self.defineFace( [ rightTopFront, rightBottomFront, rightBottomBack, rightTopBack ] )		# Right side
		self.defineFace( [ rightTopBack, rightBottomBack, leftBottomBack, leftTopBack ] )			# Back
		self.defineFace( [ leftTopBack, leftBottomBack, leftBottomFront, leftTopFront ] )			# Left side
		self.defineFace( [ leftBottomFront, leftBottomBack, rightBottomBack, rightBottomFront ] )	# Bottom
		self.defineFace( [ leftTopBack, leftTopFront, rightTopFront, rightTopBack ] )				# Top
 