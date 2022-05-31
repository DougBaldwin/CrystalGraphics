# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class renders a rotating image to a window, with optional
# animation of the model shown in that window. The rotation is as if the viewer is
# orbiting the Y axis while looking towards the origin. All graphics use the GPU rendering
# pipeline.

# Copyright (C) 2016, 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from AnimatedScreenRenderer import AnimatedScreenRenderer
from math import sin, cos, pi, fmod




# The actual renderer class.

class RotatingScreenRenderer( AnimatedScreenRenderer ) :
	
	
	
	
	# The main attributes for a rotating screen renderer, in addition to the inherited
	# ones, are...
	#    r, theta, y - The viewer's position, in cylindrical coordinates. Angle theta is
	#      measured in radians counterclockwise (as seen from above) from the positive z
	#      axis.
	#    orbiting - A Boolean value that indicates whether the viewer is orbiting the y
	#      axis (if true) or is stationary (if false).




	# Initialize a rotating screen renderer. Clients provide the viewer's height (y
	# coordinate) and distance from the origin, from which the renderer calculates
	# successive x, y, and z coordinates as the viewer orbits. Since rotating screen
	# rendering is a special case of animated rendering, clients also have the option of
	# giving this renderer a callback function for updating the model being rendered. If
	# clients don't provide this callback the model is whatever was built through calls to
	# this renderer's "triangle" method before telling it to draw its model.
	
	def __init__( self, height, distance, modelCB = None ) :
		
		
		# Rotating screen renderers are really animated screen renderers with a view
		# callback that rotates the view around the Y axis, so initialize the superclass
		# accordingly.
		
		super().__init__( modelCB, lambda r, dt : self.orbit( r, dt ) ) 
		
		
		# Install a keyboard callback that toggles orbiting on and off every time the user
		# presses a key. Whether orbiting is on or off is recorded in an "orbiting" flag,
		# which is initially off.
		
		self.orbiting = False
		
		@self.window.event
		def on_key_press( symbols, modifiers ) :
			self.orbiting = not self.orbiting
			
		
		# Set up the initial viewer position.
		
		self.r = distance
		self.theta = 0.0
		self.y = height
		
		self.viewer( self.viewerX(), self.y, self.viewerZ() )
	
	
	
	
	# Move the viewer along its orbit, simulating the passage of "dt" seconds. Update
	# the viewing position for renderer "renderer" accordingly. But note that if the
	# "orbiting" flag is false, the viewer doesn't move.
	
	def orbit( self, renderer, dt ) :
	
		radiansPerSecond = pi / 10.0;				# Do 1 complete orbit every 20 seconds
		
		if self.orbiting :
			self.theta = fmod( self.theta + radiansPerSecond * dt, 2.0 * pi )
			renderer.viewer( self.viewerX(), self.y, self.viewerZ() )
	
	
	
	
	# Utility methods for internal use that calculate Cartesian x and z coordinates for
	# the viewer from this renderer's current r and theta values.
	
	def viewerX( self ) :
		return self.r * sin( self.theta )
	
	def viewerZ( self ) :
		return self.r * cos( self.theta )
