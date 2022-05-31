# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class is a superclass for all renderers that render to a
# window using the GPU rendering pipeline. This class and its descendants therefore
# favor fast rendering over high realism. One of the main engineering reasons for this
# class is to encapsulate the technology (e.g., Pyglet vs some other windowing library,
# etc.) that performs such rendering.

# Copyright (C) 2016 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   July 2016 -- Created by Doug Baldwin.
#
#   May 2017 -- Modified by Doug Baldwin to look for shaders in whatever directory this
#     module was loaded from, regardless of what the working directory might be.


from Renderer import Renderer
from VectorOps import normalize3, orthogonalize3, cross, matrixMultiply
from GLUtilities import PROGRAM, GLError, readShader, compileShader, abortOnShaderError, \
						getUniformLocation, getAttributeIndex, CStringToPython
import pyglet
from pyglet.gl import *
from ctypes import POINTER, pointer, sizeof, cast
from math import sqrt
import os
import time							# For performance testing




# The actual renderer class.

class ScreenRenderer( Renderer ) :
	
	
	
	
	# Screen renderers use the following attributes, in addition to those they inherit,
	# to manage rendering:
	#   window - The Pyglet window in which the renderer draws.
	#   shaders - An OpenGL/GLSL shader program the renderer uses to put pixels on screen.
	#   positionIndex,
	#   normalIndex,
	#   colorIndex,
	#   specularIndex,
	#   shineIndex - GLSL vertex attribute indices for vertex positions, normal vectors,
	#     colors, coefficients of specular reflection, and shininess exponents.
	#   vpMatrixLocation - The location for a GLSL uniform variable that holds a matrix
	#     defining the viewing and projection transformations to use in rendering.
	#   viewerLocation -  The location of a GLSL uniform variable that holds the viewer's
	#     position as a three-element vector.
	#   facesLocation - The location of a GLSL uniform variable that indicates whether
	#     shaders are to draw front or back faces of polygons (the shaders operate in 2
	#     passes, one for back faces and then one for front, to get better results from
	#     alpha blending).
	#   modelSame - A Boolean value that indicates whether the model now being drawn is
	#     definitely the same as the one drawn last time (True) or might have changed
	#     (False).
	#   oldVertexCount - The number of vertices the model had last time it was drawn.
	
	# For now, all screen renderers have a fixed number of light sources, dictated by the
	# shaders that screen renderers use.
	
	N_LIGHTS = 4




	# Initialize a screen renderer, given descriptions of the desired direct and ambient
	# lighting. In particular, clients provide the overall intensity of ambient light,
	# and lists specifying the directions to and intensities of each direct light source.
	# The directions form a list of 12 numbers, with each consecutive group of 3 being the
	# x, y, and z components of one direction vector. Each intensity is a single real
	# number between 0 and 1. Using the lighting information, this constructor creates a
	# window to draw in and initializes the graphics library.
	
	def __init__( self, ambientIntensity, lightDirections, lightIntensities ) :
		
		super().__init__()
		
		
		# Create the window, allowing the user to resize it. But as the window resizes,
		# always draw in a square part, to match a square cross-section of views.
		
		self.window = pyglet.window.Window( width=512, height=512, resizable = True )
		
		# @self.window.event
		# def on_resize( width, height ) :
		#	if width > height :
		#		margin = ( width - height ) // 2
		#		glViewport( margin, 0, height, height )
		#	else :
		#		margin = ( height - width ) // 2
		#		glViewport( 0, margin, width, width )
		#	return pyglet.event.EVENT_HANDLED
		
		
		# Install shaders.
		
		try :
		
			utilityDirectory = os.path.dirname( __file__ )
			
			vertexCode = readShader( utilityDirectory + "/CrystalVertexShader.glsl" )
			vertexShader = compileShader( vertexCode, GL_VERTEX_SHADER )
		
			fragmentCode = readShader( utilityDirectory + "/CrystalFragmentShader.glsl" )
			fragmentShader = compileShader( fragmentCode, GL_FRAGMENT_SHADER )
		
			self.shaders = glCreateProgram()
			glAttachShader( self.shaders, vertexShader )
			glDeleteShader( vertexShader )
			glAttachShader( self.shaders, fragmentShader )
			glDeleteShader( fragmentShader )
			glLinkProgram( self.shaders )
			abortOnShaderError( self.shaders, PROGRAM )
			
			self.positionIndex = getAttributeIndex( self.shaders, "vertexPosition" )
			self.normalIndex = getAttributeIndex( self.shaders, "vertexNormal" )
			self.colorIndex = getAttributeIndex( self.shaders, "vertexColor" )
			self.specularIndex = getAttributeIndex( self.shaders, "ks" )
			self.shineIndex = getAttributeIndex( self.shaders, "shine" )
			self.vpMatrixLocation = getUniformLocation( self.shaders, "viewProjection" )
			self.viewerLocation = getUniformLocation( self.shaders, "viewerPosition" )
			self.facesLocation = getUniformLocation( self.shaders, "whichFaces" )
		
			glUseProgram( self.shaders )
				
		except IOError as error :
			print( "Error! Unable to read shader: ", error.strerror )
		
		except GLError as error :
			print( "Error! Couldn't build shader: ", error.args[0] )
		
		
		# Initialize key OpenGL state.
		
		glEnable( GL_DEPTH_TEST )
		
		glClearColor( 0.9, 0.9, 0.9, 1.0 )
		glClearDepth( 1.0 )
		
		glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
		glEnable( GL_BLEND )
		
		
		# Initialize light sources
		
		CDirections = ( GLfloat * (ScreenRenderer.N_LIGHTS * 3) )( *lightDirections  )
		CIntensities = ( GLfloat * ScreenRenderer.N_LIGHTS )( *lightIntensities )
		
		directionLocation = getUniformLocation( self.shaders, "lightDirections" )
		glUniform3fv( directionLocation, ScreenRenderer.N_LIGHTS, CDirections )
		
		intensityLocation = getUniformLocation( self.shaders, "lightIntensities" )
		glUniform1fv( intensityLocation, ScreenRenderer.N_LIGHTS, CIntensities )
		
		ambientLocation = getUniformLocation( self.shaders, "ambientIntensity" )
		glUniform1f( ambientLocation, ambientIntensity )
		
		
		# Right now the model has no vertices in it. Call that a change from the
		# previous time it was drawn, since there is no "previous time."
		
		self.oldVertexCount = 0
		self.modelSame = False
	
	
	
	
	# Draw this renderer's model.
	
	def draw( self ) :

		
		# Give this renderer an "on_draw" handler that builds and draws an OpenGL vertex
		# buffer that contains the information about each vertex in the model. For now,
		# that information is the x, y, and z coordinates, normal, and red, green, blue,
		# and alpha color components of the vertex. Each vertex's data is contiguous in
		# the buffer, which means that the corresponding OpenGL vertex, color, and other
		# arrays have non-0 strides between their elements. For best (but not necessarily
		# perfect) translucency effects, I draw the vertex buffer in 2 passes, the first
		# drawing back faces and the second drawing front faces. I also set up as much
		# OpenGL state as possible, namely the ID for the vertex buffer and enabling the
		# attributes my shader uses, before the "on_draw" function rather than inside it,
		# to avoid doing those things more often than necessary.
		
		FRONT = 1						# Code that tells shader to draw front faces
		BACK = 2						# Code for back faces
		
		pythonStride = 12								# Number of Python numbers between vertices in the buffer
		byteStride = pythonStride * sizeof( GLfloat )	# Number of bytes between vertices
		vertexOffset = 0								# Offset (in Python numbers) for vertex coordinates
		normalOffset = 3								# Offset for normal vector
		colorOffset = 6									# Offset for RGB color components
		specularOffset = 10								# Offset for coefficient of specular reflection
		shineOffset = 11								# Offset for shininess exponent
			
		bufferID = GLuint( 0 )
		glGenBuffers( 1, pointer(bufferID) )
			
		glEnableVertexAttribArray( self.positionIndex )
		glEnableVertexAttribArray( self.normalIndex )
		glEnableVertexAttribArray( self.colorIndex )
		glEnableVertexAttribArray( self.specularIndex )
		glEnableVertexAttribArray( self.shineIndex )

		
		@self.window.event
		def on_draw() :
			
			glBindBuffer( GL_ARRAY_BUFFER, bufferID )
			
			glVertexAttribPointer( self.positionIndex, 3, GL_FLOAT, GL_FALSE, byteStride, vertexOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.normalIndex, 3, GL_FLOAT, GL_FALSE, byteStride, normalOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.colorIndex, 4, GL_FLOAT, GL_FALSE, byteStride, colorOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.specularIndex, 1, GL_FLOAT, GL_FALSE, byteStride, specularOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.shineIndex, 1, GL_FLOAT, GL_FALSE, byteStride, shineOffset * sizeof(GLfloat) )
			
			
			# If the vertices that define the model have changed, I need to put their new
			# descriptions into the vertex buffer for the shaders. Otherwise I can  jump
			# straight to drawing that buffer.
			
			if not self.modelSame :
				
				if len( self.vertices ) <= self.oldVertexCount :
					
					# I can re-use existing buffer memory, but have to re-populate it with
					# new contents.
					
					GLfloatPTR = POINTER( GLfloat )
					
					bufferAddress = glMapBuffer( GL_ARRAY_BUFFER, GL_WRITE_ONLY )
					vertexArray = cast( bufferAddress, GLfloatPTR )
					
					if vertexArray != GLfloatPTR() :				# Make sure map produced a non-NULL result
					
						vertexIndex = 0
					
						for v in self.vertices :
					
							vertexArray[ vertexIndex ] = v.x
							vertexArray[ vertexIndex+1 ] = v.y
							vertexArray[ vertexIndex+2 ] = v.z
							vertexArray[ vertexIndex+3 ] = v.nx
							vertexArray[ vertexIndex+4 ] = v.ny
							vertexArray[ vertexIndex+5 ] = v.nz
							vertexArray[ vertexIndex+6 ] = v.red
							vertexArray[ vertexIndex+7 ] = v.green
							vertexArray[ vertexIndex+8 ] = v.blue
							vertexArray[ vertexIndex+9 ] = v.alpha
							vertexArray[ vertexIndex+10 ] = v.specular
							vertexArray[ vertexIndex+11 ] = v.shine
						
							vertexIndex += pythonStride
					
					glUnmapBuffer( GL_ARRAY_BUFFER )
					
				
				else :
					
					# I need to allocate a new, bigger, block of memory for the buffer.
		
					vertexData = []
		
					for v in self.vertices :
						vertexData += [ v.x, v.y, v.z,
										v.nx, v.ny, v.nz,
										v.red, v.green, v.blue, v.alpha,
										v.specular, v.shine ]
		
					vertexArray = ( GLfloat * len(vertexData) )(*vertexData)
					glBufferData( GL_ARRAY_BUFFER, sizeof(vertexArray), vertexArray, GL_STREAM_DRAW )
				
					self.oldVertexCount = len( self.vertices )

			
			# Actually draw the model.
			
			glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
			
			glUniform1i( self.facesLocation, BACK )
			glDrawArrays( GL_TRIANGLES, 0, len( self.vertices ) )
			glUniform1i( self.facesLocation, FRONT )
			glDrawArrays( GL_TRIANGLES, 0, len( self.vertices ) )
			
			
			# At this moment, the model is the same as it was an instant ago when I drew
			# it.
			
			self.modelSame = True
		
		
		# Run Pyglet's event loop, thus running the "draw" handler and then waiting for
		# the user to close the window to stop the program.
		
		pyglet.app.run()
		
		
		# Now delete this renderer's shaders, since they're no longer needed.
		
		glDeleteProgram( self.shaders )

	
	
	
	# Set the position from which calls to "draw" (or Pyglet's on_draw callback, if the
	# actual rendering is happening in an animation loop) will view the model.
	
	def viewer( self, x, y, z ) :
		
		
		# Give this renderer a viewing and projection transformation suitable for looking
		# towards the origin from the new position.
		
		distance = sqrt( x**2 + y**2 + z**2 )
		self.setViewingTransformation( self.originView( x, y, z ), self.clipAroundOrigin( distance ) )
									   
		
		# Tell the shaders where the viewer is.
		
		positionBuffer = ( GLfloat * 3 )( x, y, z )
		glUniform3fv( self.viewerLocation, 1, positionBuffer )
	
	
	
	
	# Report the versions of OpenGL and GLSL that this renderer uses.
	
	def version( self ) :
	
		glVersion = glGetString( GL_VERSION )
		glslVersion = glGetString( GL_SHADING_LANGUAGE_VERSION )
		
		return "OpenGL " + CStringToPython( glVersion ) + "; GLSL " + CStringToPython( glslVersion )
	
	
	
	
	# Add a triangle to this renderer's model, or erase the model. Both of these methods
	# mostly just do whatever the superclass would do, except that both actions also
	# represent changes to the model, which the superclass presumably doesn't care about.
	
	def triangle( self, v1, v2, v3, material ) :
		super().triangle( v1, v2, v3, material )
		self.modelSame = False
	
	def eraseModel( self ) :
		super().eraseModel()
		self.modelSame = False
	
	
	
	
	# A collection of utility methods that perform common actions related to viewing.
	
	# Construct a matrix that transforms the world coordinate system into a viewer
	# coordinate system, given that the viewer is looking towards the origin from point
	# (x,y,z).
	
	def originView( self, x, y, z ) :
		
		# The basis vectors for the viewer-centered coordinate system form the columns of
		# a transformation from viewer to world coordinates, and thus the rows of the
		# inverse of that transformation (since the basis vectors are orthonormal). This
		# observation gives me a basic transformation from world to viewer coordinates.
		# Extending the transformation matrix with a 4th column that translates the
		# viewer origin to the world origin produces the complete transformation. Note
		# that this translation just moves points the negative of the distance from the
		# world origin to the viewer in the viewer's "back" direction.
		
		back = normalize3( [x, y, z] )
		up = normalize3( orthogonalize3( [0.0, 1.0, 0.0], back ) )
		right = cross( up, back )
		
		return [ [ right[0],  right[1],  right[2],  0.0 ],
				 [ up[0],     up[1],     up[2],     0.0 ],
				 [ back[0],   back[1],   back[2],   -sqrt( x**2 + y**2 + z**2 ) ],
				 [ 0.0,       0.0,       0.0,       1.0 ] ]
	
	
	
	
	# Build a projection matrix that transforms viewer-relative coordinates into clipping
	# coordinates in a viewing volume whose front plane is 1 unit in front of (i.e.,
	# towards the origin from) the viewer, and whose back plane is the same distance from
	# the origin as the front plane, but on the opposite side of the origin. The front
	# face of this viewing volume is 1 unit wide and high, centered on the viewer. The
	# 2nd argument to this method is the distance from the origin to the viewer. The
	# coefficients for the matrix come from the viewing volume parameters, using
	# calculations derived in my July 21, 2016 project notes.
	
	def clipAroundOrigin( self, distance ) :
		
		a = distance / ( 1.0 - distance )
		b = ( 2.0 * distance - 1 ) / ( 1.0 - distance )
		
		return [ [ 2.0,  0.0,   0.0,  0.0 ],
				 [ 0.0,  2.0,   0.0,  0.0 ],
				 [ 0.0,  0.0,   a,    b   ],
				 [ 0.0,  0.0,  -1.0,  0.0 ] ]
	
	
	
	
	# Build a world-to-clip coordinates transformation from separate world-to-viewer and
	# viewer-to-clip transformations, and tell the shaders to use that transformation.
	# Both transformations should be 4-by-4 matrices, represented as lists of lists in
	# row-major order.
	
	def setViewingTransformation( self, viewMatrix, projectionMatrix ) :
		
		vpMatrix = matrixMultiply( projectionMatrix, viewMatrix )
		
		matrixBuffer = ( GLfloat * 16 )( vpMatrix[0][0], vpMatrix[0][1], vpMatrix[0][2], vpMatrix[0][3],
										 vpMatrix[1][0], vpMatrix[1][1], vpMatrix[1][2], vpMatrix[1][3],
										 vpMatrix[2][0], vpMatrix[2][1], vpMatrix[2][2], vpMatrix[2][3],
										 vpMatrix[3][0], vpMatrix[3][1], vpMatrix[3][2], vpMatrix[3][3] )
										 
		glUniformMatrix4fv( self.vpMatrixLocation, 1, GL_TRUE, (POINTER(GLfloat))( matrixBuffer ) )
