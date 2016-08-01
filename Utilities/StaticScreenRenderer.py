# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class renders a static image to a window, using the GPU
# rendering pipeline.

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from ScreenRenderer import ScreenRenderer
from VectorOps import normalize3, orthogonalize3, cross
from math import sqrt




# The actual renderer class.

class StaticScreenRenderer( ScreenRenderer ) :




	# Initialize a static screen renderer.
	
	def __init__( self ) :
		lightPos = normalize3( [ 2.5, 9.0, 0.5 ] )
		super(StaticScreenRenderer,self).__init__( 0.6,
												   [ lightPos[0], lightPos[1], lightPos[2],
													 1.0, 0.0, 0.0,
													 1.0, 0.0, 0.0,
													 1.0, 0.0, 0.0  ],
													[ 1.0, 0.0, 0.0, 0.0 ] )
	
	
	
	
	# Set the position from which calls to "draw" will view the model. The view will be
	# towards the origin from the point specified to this method, with a view volume
	# extending from 1 unit in front of (i.e., towards the origin from) the point to the
	# origin and then the same distance again beyond the origin. The front face of this
	# viewing volume is 1 unit wide and high, centered on the viewer.
	
	def viewer( self, x, y, z ) :
		
		
		# Build matrices that transform from world to viewer-relative coordinates, and
		# from viewer coordinates to clipping coordinates. Use the product of those
		# matrices for actual viewing.
		
		viewMatrix = self.originView( x, y, z )
		projectionMatrix = self.clipAroundOrigin( sqrt( x**2 + y**2 + z**2 ) )
		
		self.setViewingTransformation( viewMatrix, projectionMatrix )
		
		
		# Do anything the superclass needs.
		
		super(StaticScreenRenderer,self).viewer( x, y, z )
