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
from ctypes import POINTER, pointer, sizeof
from math import sqrt
import os




# The actual renderer class.

class ScreenRenderer( Renderer ) :
	
	
	
	
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
		
		super(ScreenRenderer,self).__init__()
		
		
		# Create the window, allowing the user to resize it. But as the window resizes,
		# always draw in a square part, to match a square cross-section of views.
		
		self.window = pyglet.window.Window( resizable = True )
		
		@self.window.event
		def on_resize( width, height ) :
			if width > height :
				margin = ( width - height ) // 2
				glViewport( margin, 0, height, height )
			else :
				margin = ( height - width ) // 2
				glViewport( 0, margin, width, width )
			return pyglet.event.EVENT_HANDLED
		
		
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
			print "Error! Unable to read shader: ", error.strerror
		
		except ShaderError as error :
			print "Error! Couldn't build shader: ", error.args[0]
		
		
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
	
	
	
	
	# Destroy a screen renderer. It seems very unlikely that a screen renderer would
	# have a usable OpenGL context after the first call to its "draw" method finishes,
	# but in case someone modifies "draw" so that renderers can continue to be used
	# after it returns, I provide this method to clean up any state under my control.
	
	def __del__( self ) :
		
		
		# The only state that needs to be cleaned up is the renderer's shader program.
		
		glDeleteProgram( self.shaders )
	
	
	
	
	# Draw this renderer's crystal.
	
	def draw( self ) :
		
		
		# Build an OpenGL vertex buffer that contains the information about each vertex
		# in the model. For now, that information is the x, y, and z coordinates, normal,
		# and red, green, and blue color components of the vertex. Each vertex's data
		# is contiguous in the buffer, which means that the corresponding OpenGL vertex,
		# color, and other arrays have non-0 strides between their elements.
		
		vertexData = []
		pythonStride = 12								# Number of Python numbers between vertices
		byteStride = pythonStride * sizeof( GLfloat )	# Number of bytes between vertices
		vertexOffset = 0								# Offset (in Python numbers) for vertex coordinates
		normalOffset = 3								# Offset for normal vector
		colorOffset = 6									# Offset for RGB color components
		specularOffset = 10								# Offset for coefficient of specular reflection
		shineOffset = 11								# Offset for shininess exponent
		
		for v in self.vertices :
			vertexData += [ v.x, v.y, v.z,
							v.nx, v.ny, v.nz,
							v.red, v.green, v.blue, v.alpha,
							v.specular, v.shine ]
		
		bufferID = GLuint( 0 )
		vertexArray = ( GLfloat * len(vertexData) )(*vertexData)
		glGenBuffers( 1, pointer(bufferID) )
		glBindBuffer( GL_ARRAY_BUFFER, bufferID )
		glBufferData( GL_ARRAY_BUFFER, sizeof(vertexArray), vertexArray, GL_STATIC_DRAW )
		glEnableVertexAttribArray( self.positionIndex )
		glEnableVertexAttribArray( self.normalIndex )
		glEnableVertexAttribArray( self.colorIndex )
		glEnableVertexAttribArray( self.specularIndex )
		glEnableVertexAttribArray( self.shineIndex )

		
		# Give this renderer an "on_draw" handler that will draw the contents of the
		# vertex buffer. For best (but not necessarily perfect) translucency effects,
		# draw the vertex buffer in 2 passes, the first drawing back faces and the
		# second drawing front faces.
		
		FRONT = 1						# Code that tells shader to draw front faces
		BACK = 2						# Code for back faces
		
		@self.window.event
		def on_draw() :
		
			glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
			
			glBindBuffer( GL_ARRAY_BUFFER, bufferID )
			glVertexAttribPointer( self.positionIndex, 3, GL_FLOAT, GL_FALSE, byteStride,
								   vertexOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.normalIndex, 3, GL_FLOAT, GL_FALSE, byteStride,
								   normalOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.colorIndex, 4, GL_FLOAT, GL_FALSE, byteStride,
								   colorOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.specularIndex, 1, GL_FLOAT, GL_FALSE, byteStride,
								   specularOffset * sizeof(GLfloat) )
			glVertexAttribPointer( self.shineIndex, 1, GL_FLOAT, GL_FALSE, byteStride,
								   shineOffset * sizeof(GLfloat) )
			
			glUniform1i( self.facesLocation, BACK )
			glDrawArrays( GL_TRIANGLES, 0, len( self.vertices ) )
			glUniform1i( self.facesLocation, FRONT )
			glDrawArrays( GL_TRIANGLES, 0, len( self.vertices ) )
		
		
		# Run Pyglet's event loop, thus running the "draw" handler and then waiting for
		# the user to close the window to stop the program.
		
		pyglet.app.run()
	
	
	
	
	# Set the position from which calls to "draw" will view the model.
	
	def viewer( self, x, y, z ) :
		
		# All that's appropriate for all screen renderers to do is tell the shaders
		# where the viewer is.
		
		positionBuffer = ( GLfloat * 3 )( x, y, z )
		glUniform3fv( self.viewerLocation, 1, positionBuffer )
	
	
	
	
	# Report the versions of OpenGL and GLSL that this renderer uses.
	
	def version( self ) :
	
		glVersion = glGetString( GL_VERSION )
		glslVersion = glGetString( GL_SHADING_LANGUAGE_VERSION )
		
		return "OpenGL " + CStringToPython( glVersion ) + "; GLSL " + CStringToPython( glslVersion )
	
	
	
	
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
