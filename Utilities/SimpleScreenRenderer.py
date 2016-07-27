# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class renders to a window, using the GPU rendering
# pipeline to quickly produce reasonably realistic images.

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from Renderer import Renderer
from VectorOps import normalize3, orthogonalize3, cross, matrixMultiply
from GLUtilities import PROGRAM, GLError, readShader, compileShader, abortOnShaderError, \
						getUniformLocation, getAttributeIndex, CStringToPython
import pyglet
from pyglet.gl import *
from ctypes import POINTER, pointer, sizeof
from math import sqrt




# The actual renderer class.

class SimpleScreenRenderer( Renderer ) :




	# Initialize a basic renderer.
	
	def __init__( self ) :
		
		super(SimpleScreenRenderer,self).__init__()
		
		
		# Create a window for this renderer to draw in, allowing the user to resize it.
		
		self.window = pyglet.window.Window( resizable = True )
		
		@self.window.event
		def on_resize( width, height ) :
			glViewport( 0, 0, width, height )
			return pyglet.event.EVENT_HANDLED
		
		
		# Install shaders.
		
		try :
			
			vertexCode = readShader( "Utilities/CrystalVertexShader.glsl" )
			vertexShader = compileShader( vertexCode, GL_VERTEX_SHADER )
		
			fragmentCode = readShader( "Utilities/CrystalFragmentShader.glsl" )
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
		
		
		# Initialize other OpenGL state.
		
		glEnable( GL_DEPTH_TEST )
		
		glClearColor( 0.9, 0.9, 0.9, 1.0 )
		glClearDepth( 1.0 )
		
		glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
		glEnable( GL_BLEND )
		
		nLights = 4;					# Number of lights the shader expects, though I only use 1
		lightDirections = ( GLfloat * (nLights * 3) )( 0.2, 0.9, sqrt( 1.0 - 0.2**2 - 0.9**2 ),
													   1.0, 0.0, 0.0,
													   1.0, 0.0, 0.0,
													   1.0, 0.0, 0.0  )
		lightIntensities = ( GLfloat * nLights )( 1.0, 0.0, 0.0, 0.0 )
		
		directionLocation = getUniformLocation( self.shaders, "lightDirections" )
		glUniform3fv( directionLocation, nLights, lightDirections )
		
		intensityLocation = getUniformLocation( self.shaders, "lightIntensities" )
		glUniform1fv( intensityLocation, nLights, lightIntensities )
		
		ambientLocation = getUniformLocation( self.shaders, "ambientIntensity" )
		glUniform1f( ambientLocation, 0.6 )
	
	
	
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
		
		
		# Give the vertex shader the product of the viewing and projection matrices.
		
		vpMatrix = matrixMultiply( projectionMatrix, viewMatrix )
		
		matrixBuffer = ( GLfloat * 16 )( vpMatrix[0][0], vpMatrix[0][1], vpMatrix[0][2], vpMatrix[0][3],
										 vpMatrix[1][0], vpMatrix[1][1], vpMatrix[1][2], vpMatrix[1][3],
										 vpMatrix[2][0], vpMatrix[2][1], vpMatrix[2][2], vpMatrix[2][3],
										 vpMatrix[3][0], vpMatrix[3][1], vpMatrix[3][2], vpMatrix[3][3] )
										 
		glUniformMatrix4fv( self.vpMatrixLocation, 1, GL_TRUE, (POINTER(GLfloat))( matrixBuffer ) )
		
		
		# Finally, tell the vertex shader where the viewer is now.
		
		positionBuffer = ( GLfloat * 3 )( x, y, z )
		glUniform3fv( self.viewerLocation, 1, positionBuffer )
	
	
	
	
	# Report the versions of OpenGL and GLSL that this renderer uses.
	
	def version( self ) :
	
		glVersion = glGetString( GL_VERSION )
		glslVersion = glGetString( GL_SHADING_LANGUAGE_VERSION )
		
		return "OpenGL " + CStringToPython( glVersion ) + "; GLSL " + CStringToPython( glslVersion )
