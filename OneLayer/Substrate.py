# This class represents a rocky substrate for a layer of crystals. As such, it represents
# one of the main structures in a model of crystal aggregates consisting of such layers on
# a substrate. See file "OneLayer.py" for more information about a program that models and
# renders such an aggregate.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May 2017 -- Created by Doug Baldwin.


from ConvexPolyhedron import ConvexPolyhedron, Vertex




class Substrate( ConvexPolyhedron ) :
	
	
	
	
	# Initialize a substrate from its bounds in the X and Z dimensions and its upper
	# bound in the Y dimension (the lower bound is always at y = 0).
	
	def __init__( self, minX, maxX, minZ, maxZ, maxY ) :
		
		
		# Tell the superclass what color the substrate is.
		
		super(Substrate,self).__init__( [ 0.62, 0.53, 0.49, 1, 0.1, 1 ] )
		
		
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
	
	
	
	
	# Add this substrate's triangles to a renderer. This method alters the renderer's
	# internal state but has no explicit return value.
	
	def OLD_addToRenderer( self, renderer ) :
		
		
		# The substrate is 12 (2 per side) opaque, rock-colored, triangles. The bounds
		# of the substrate's block are in world coordinates, so use them directly to
		# calculate the vertices of the block and from there the triangles.
		
		leftBottomBack = [ self.minX, self.minY, self.minZ ]
		leftBottomFront = [ self.minX, self.minY, self.maxZ ]
		leftTopBack = [ self.minX, self.maxY, self.minZ ]
		leftTopFront = [ self.minX, self.maxY, self.maxZ ]
		rightBottomBack = [ self.maxX, self.minY, self.minZ ]
		rightBottomFront= [ self.maxX, self.minY, self.maxZ ]
		rightTopBack = [ self.maxX, self.maxY, self.minZ ]
		rightTopFront = [ self.maxX, self.maxY, self.maxZ ]
		
		color = [ 0.62, 0.53, 0.49, 1, 0.1, 1 ]
		
		renderer.triangle( leftTopFront, leftBottomFront, rightBottomFront, color )		# Front of substrate
		renderer.triangle( leftTopFront, rightBottomFront, rightTopFront, color )
		renderer.triangle( rightTopFront, rightBottomFront, rightBottomBack, color )	# Right side
		renderer.triangle( rightTopFront, rightBottomBack, rightTopBack, color )
		renderer.triangle( rightTopBack, rightBottomBack, leftBottomBack, color )		# Back
		renderer.triangle( rightTopBack, leftBottomBack, leftTopBack, color )
		renderer.triangle( leftTopBack, leftBottomBack, leftBottomFront, color )		# Left side
		renderer.triangle( leftTopBack, leftBottomFront, leftTopFront, color )
		renderer.triangle( leftBottomFront, leftBottomBack, rightBottomBack, color )	# Bottom
		renderer.triangle( leftBottomFront, rightBottomBack, rightBottomFront, color )
		renderer.triangle( leftTopBack, leftTopFront, rightTopFront, color )			# Top
		renderer.triangle( leftTopBack, rightTopFront, rightTopBack, color )
 