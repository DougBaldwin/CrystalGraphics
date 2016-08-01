# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class renders a rotating image to a window, using the GPU
# rendering pipeline. The rotation is as if the viewer is orbiting the Y axis while
# looking towards the origin.

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from ScreenRenderer import ScreenRenderer
from VectorOps import normalize3, orthogonalize3, cross
import pyglet
from math import sqrt, atan2, sin, cos, pi, fmod




# The actual renderer class.

class RotatingScreenRenderer( ScreenRenderer ) :




	# Initialize a rotating screen renderer.
	
	def __init__( self ) :
		
		
		# Initialize general screen renderer features, notably lighting.
		
		light1Pos = normalize3( [ 1.0, 9.0, 2.0 ] )
		light2Pos = normalize3( [ -1.0, -0.9, -0.05 ] )
		
		super(RotatingScreenRenderer,self).__init__( 0.6,
													 [ light1Pos[0], light1Pos[1], light1Pos[2],
													   light2Pos[0], light2Pos[1], light2Pos[2],
													   1.0, 0.0, 0.0,
													   1.0, 0.0, 0.0  ],
													 [ 1.0, 0.5, 0.0, 0.0 ] )
		
		
		# Install a keyboard callback that toggles orbiting on and off every time the user
		# presses a key. Whether orbiting is on or off is recorded in an "orbiting" flag,
		# which is initially on.
		
		self.orbiting = True
		
		@self.window.event
		def on_key_press( symbols, modifiers ) :
			self.orbiting = not self.orbiting
		
		
		# Tell Pyglet to periodically call an animation function that moves this
		# renderer's viewer around its orbit. Have this function run nominally 40 times
		# per second, although it may be slightly slower.
		
		pyglet.clock.schedule_interval( lambda dt: self.orbit( dt ), 1.0/40.0 )
			
		
		# Set up a default viewer position, just in case someone starts the orbit without
		# saying where to start from.
		
		self.r = 1.0
		self.theta = 0.0
		self.y = 1.0
		
		self.projectionMatrix = self.clipAroundOrigin( sqrt( self.r**2 + self.y**2 ) )
		
		self.updatePosition()
	
	
	
	
	# Set the position from which the orbit will begin. When clients call "draw," the
	# view will begin orbiting from here, maintaining its height and distance from the
	# y axis, but orbiting around the y axis.
	
	def viewer( self, x, y, z ) :
		
		
		# I record the viewer's position in cylindrical form, so convert (x,y,z) to
		# that form.
		
		self.r = sqrt( x**2 + z**2 )
		self.theta = atan2( x, z )
		self.y = y
		
		
		# The viewer's distance from the origin never changes during the orbit, so I can
		# build the projection part of the viewing transformation now. Doing so saves
		# redoing it every time I update the view during the orbit.
		
		self.projectionMatrix = self.clipAroundOrigin( sqrt( x**2 + y**2 + z**2 ) )
		
		
		# Be sure the viewing parts of the system know about this position.
		
		self.updatePosition()
	
	
	
	
	# Update the view for a new viewer position, based on the "r," "theta," and "y" member
	# variables. The view is always towards the origin from the viewer's current position,
	# with a view volume extending from 1 unit in front of (i.e., towards the origin from)
	# the viewer and then continuing on 1 unit less than the viewer's distance past the
	# origin. The front face of this viewing volume is 1 unit wide and high, centered on
	# the viewer.
	
	def updatePosition( self ) :
		
		
		# Set up the world-to-viewer coordinates part of the viewing transformation.
		# For computing the viewer's x and z coordinates, recall that theta is measured
		# from the z axis.
		
		x = self.r * sin( self.theta )
		z = self.r * cos( self.theta )
		
		viewMatrix = self.originView( x, self.y, z )
		
		
		# Build the complete viewing transformation from the world-to-viewer
		# transformation and the projection/clipping transformation built in "viewer".
		
		self.setViewingTransformation( viewMatrix, self.projectionMatrix )
		
		
		# Be sure the superclass knows where the viewer is now.
		
		super(RotatingScreenRenderer,self).viewer( x, self.y, z )
	
	
	
	
	# Move the viewer along its orbit, simulating the passage of "dt" seconds. But note
	# that if the "orbiting" flag is false, the viewer doesn't move.
	
	def orbit( self, dt ) :
	
		radiansPerSecond = pi / 6.0;				# Do 1 complete orbit every 12 seconds
		
		if self.orbiting :
			self.theta = fmod( self.theta + radiansPerSecond * dt, 2.0 * pi )
			self.updatePosition()

