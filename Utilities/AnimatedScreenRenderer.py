# Part of a hierarchy of Python classes that render graphical models built from triangles
# to various output devices. This class carries out animated rendering to the monitor.
# In other words, the model and the view of it can change from frame to frame. Changes to
# the model and view are produced by calling client-provided callback functions, one for
# updating the viewing position and one for updating the triangles in the model. Both
# callbacks take the renderer they were called by and the time since the last update as
# their arguments, and should work by calling the renderer's "viewer" and "triangle"
# methods. But either callback can be None instead of being a function, in which case the
# corresponding renderer information doesn't get updated on each frame. Animation
# renderers use the GPU rendering pipeline for their graphics operations.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   June 2019. Created by Doug Baldwin.


from ScreenRenderer import ScreenRenderer
from VectorOps import normalize3, orthogonalize3, cross
import pyglet




class AnimatedScreenRenderer( ScreenRenderer ) :
	
	
	
	
	# Animated screen renderers save their callback functions in attributes...
	#   o modelCallback - the callback for updating the model
	#   o viewCallback - the callback for updating the view
	
	
	
	
	# Initialize an animation renderer with its model and viewer callbacks.
	
	def __init__( self, modelCB, viewCB ) :
		
		
		# Save the arguments in the corresponding attributes.
		
		self.modelCallback = modelCB
		self.viewCallback = viewCB
		
		
		# Initialize general screen renderer features, notably lighting.
		
		light1Pos = normalize3( [ 1.0, 9.0, 2.0 ] )
		light2Pos = normalize3( [ -1.0, -0.9, -0.05 ] )
		
		super().__init__( 0.6,
						  [ light1Pos[0], light1Pos[1], light1Pos[2],
							light2Pos[0], light2Pos[1], light2Pos[2],
							1.0, 0.0, 0.0,
							1.0, 0.0, 0.0  ],
						  [ 1.0, 0.5, 0.0, 0.0 ] )
		
		
		# Tell Pyglet to periodically call an animation function that in turn calls the
		# client's callback functions, if they have been defined. Have this function run
		# nominally 40 times per second, although it may be slightly slower.
		
		pyglet.clock.schedule_interval( lambda dt: self.animate( dt ), 1.0/40.0 )
	
	
	
	
	# Update this renderer's model and view for the next animation frame. The argument to
	# this method is the elapsed time since the last frame.
	
	def animate( self, dt ) :
		
		
		# Updating just requires calling any client callback functions that were provided.
		# Note that for the model callback, this erases any old model before calling the
		# callback, so the callback function can (and must) completely redefine what this
		# renderer draws.
		
		if self.modelCallback :
			self.eraseModel()
			self.modelCallback( self, dt )
		
		if self.viewCallback :
			self.viewCallback( self, dt )
