# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class renders a static image to a window, using the GPU
# rendering pipeline.

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from ScreenRenderer import ScreenRenderer
from VectorOps import normalize3, orthogonalize3, cross, matrixMultiply
from GLUtilities import PROGRAM, GLError, readShader, compileShader, abortOnShaderError, \
						getUniformLocation, getAttributeIndex, CStringToPython
import pyglet
from pyglet.gl import *
from ctypes import POINTER, pointer, sizeof
from math import sqrt




# The actual renderer class.

class StaticScreenRenderer( ScreenRenderer ) :




	# Initialize a static screen renderer.
	
	def __init__( self ) :
		super(StaticScreenRenderer,self).__init__( 0.6,
												   [ 0.2, 0.9, sqrt( 1.0 - 0.2**2 - 0.9**2 ),
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
		
		# This method builds a world-coordinates-to-clip-coordinates transformation for
		# the crystal vertex shader to apply to vertices. Build this transformation in 2
		# parts: First transform world coordinates to viewer-relative coordinates, then
		# transform viewer coordinates to clip coordinates with a perspective projection.
		
		
		# Build the world-to-viewer transformation matrix. This matrix is based on the
		# idea that the unit-length basis vectors for a viewer-centered coordinate
		# system are the columns of a transformation from viewer to world coordinates,
		# and thus the rows of the inverse of that transformation (since the basis
		# vectors are orthonormal). Extending this with a 4th column that translates
		# the viewer origin to the world origin completes the transformation. Note that
		# this translation just moves points the negative of the distance from the world
		# origin to (x,y,z) in the viewer's "back" direction.
		
		distance = sqrt( x**2 + y**2 + z**2 )			# Viewer distance from origin
		
		back = normalize3( [x, y, z] )
		up = normalize3( orthogonalize3( [0.0, 1.0, 0.0], back ) )
		right = cross( up, back )
		
		viewMatrix = [ [ right[0], right[1], right[2], 0.0 ],
					   [ up[0],    up[1],    up[2],    0.0 ],
					   [ back[0],  back[1],  back[2],  -distance ],
					   [ 0.0,      0.0,      0.0,      1.0 ] ]
		
		
		# Build the viewer-to-clip projection matrix. The coefficients come from the
		# viewing volume parameters described in the introductory comments to this
		# method, using calculations derived in July 21, 2016 project notes.
		
		a = distance / ( 1.0 - distance )
		b = ( 2.0 * distance - 1 ) / ( 1.0 - distance )
		
		projectionMatrix = [ [ 2.0,  0.0,   0.0,  0.0 ],
							 [ 0.0,  2.0,   0.0,  0.0 ],
							 [ 0.0,  0.0,   a,    b   ],
							 [ 0.0,  0.0,  -1.0,  0.0 ] ]
		
		
		# Use the product of the two matrices for subsequent viewing.
		
		self.setViewingTransformation( viewMatrix, projectionMatrix )
		
		
		# Do anything the superclass needs.
		
		super(StaticScreenRenderer,self).viewer( x, y, z )
