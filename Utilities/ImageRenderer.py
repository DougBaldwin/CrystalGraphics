# Part of a hierarchy of Python classes that render crystals or crystal aggregates in
# various ways. This class renders an arbitrary image -- nominally one of a crystal or
# aggregate, and nominally produced from some model of said crystal or aggregate by a ray
# tracer or other renderer, but in fact the images can come from anywhere. Clients simply
# need to provide those images as lists in the form
#   [ [ [R11,G11,B11], [R12,G12,B12], ... ]             # top row of image
#     [ [R21,G21,B21], [R22,G22,B22], ... ]				# 2nd row
#     ...
#     [ [Rn1,Rn1,Bn1], [Rn2,Gn2,Bn2], ... ] ]			# bottom row of image
# In other words, an image is a list of rows, each of which is a list of columns, each
# of which is a list of pixels. Each pixel is specified by red, green, and blue color
# intensities (Rij, Bij, Gij in the above template), which are real numbers between 0
# (lowest intensity) and 1 (highest intensity). All rows of the image must have the same
# number of columns. This class renders the image to a resizable window. See file
# "Renderer.py" and the crystals project notes for more information on the renderer class
# hierarchy.

# Copyright (C) 2016 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from Renderer import Renderer
import pyglet
from pyglet.gl import *




# The number of color components in a pixel. This is really intended to be a constant
# for use inside the image renderer class, although Python allows clients who try hard
# enough to access it.

_COLOR_COMPONENTS = 3




# The image renderer class definition.

class ImageRenderer ( Renderer ) :
	
	
	
	
	# The following are internal details of image renderers that clients don't need to
	# know about:
	
	# Image renderers do their rendering by storing the image that they are to display
	# and a sprite that actually displays it. The image holds the image dimensions and the
	# raw pixels that form it, while the sprite takes care of positioning and scaling the
	# image to mostly fill its window when drawn.
	
	# The following method changes this renderer's image and sprite to render a new image
	# of a given width and height. The pixel data for the image is given as a byte array
	# in row-major order, with rows ordered from the bottom of the image to the top.
	
	def newImage( self, width, height, pixels ) :
	
	
		# Build the new image.
		
		self.img = pyglet.image.ImageData( width, height, "RGB", str(pixels) )
		
		
		# Replace the sprite with one for the new image, after purging the old one from
		# GPU memory. Also make sure the new sprite is appropriately scaled and positioned
		# for the new image.
		
		if self.imgSprite != None :
			self.imgSprite.delete()
		
		self.imgSprite = pyglet.sprite.Sprite( self.img )

		self.scaleSprite()
	
	
	
	
	# A utility method that sets the position and scale factor of this renderer's sprite
	# so that it draws its image centered in the window and as large as possible while
	# still fitting entirely inside the window.
	
	def scaleSprite( self ) :
	
	
		# The scale factor is the smaller of what it would take to scale the image to the
		# full width of the window, and what it would take to scale it to the full height.
		
		self.imgSprite.scale = min( float(self.window.width) / self.img.width,		\
									float(self.window.height) / self.img.height )
		
		
		# The horizontal and vertical offsets of the sprite center the pixels actually
		# occupied by the image in the window.
		
		self.imgSprite.x = int( ( self.window.width - self.imgSprite.scale * self.img.width ) / 2 )
		self.imgSprite.y = int( ( self.window.height - self.imgSprite.scale * self.img.height ) / 2 )
	
	
	
	
	# The public interface to image renderers starts here:
	
	# Initialize an image renderer.
	
	def __init__( self ) :
		
		
		# Create a resizable window in which to eventually render the image and
		# initialize the OpenGL state that matters.
		
		self.window = pyglet.window.Window( resizable = True )
		
		glClearColor( 0.9, 0.9, 0.9, 1.0 )
		
		
		# Create the image that will eventually store any image associated with this
		# renderer, and the sprite that will display it. The initial image contains a
		# single black pixel. Note that "newImage" assumes there is something in the
		# "imgSprite" attribute.
		
		self.imgSprite = None
		self.newImage( 1, 1, bytearray( [0,0,0] ) )
		
		
		# Define a callback function for drawing the image. This function just clears the
		# window and draws the sprite.
		
		@self.window.event
		def on_draw() :
			glClear( GL_COLOR_BUFFER_BIT )
			self.imgSprite.draw()
		
		
		# Define a callback function for resizing the window. This function just adjusts
		# the sprite's size and position to fit the new window.
		
		@self.window.event
		def on_resize( w, h ) :
			self.scaleSprite()
	
	
	
	
	# Clean up an image renderer that's being garbage collected.
	
	def __del__( self ) :
		
		
		# Clean up only requires deleting the sprite in case it's tying up GPU memory.
		
		self.imgSprite.delete()
	
	
	
	
	# Define the image that an image renderer will later render. This image replaces any
	# previously set for this renderer. See the comments at the beginning of this file
	# for the image representation.
	
	def image( self, img ) :
		
		
		# Convert the image from external form (a 3-dimensional list of real numbers
		# ordered from the top of the image to the bottom) into a string of bytes
		# representing pixels in row-major order but from bottom to top.
		
		height = len( img )
		width = len( img[0] )
		pixels = bytearray( height * width * _COLOR_COMPONENTS )
		
		for row in range( height ) :
			imageRow = height - row - 1
			for col in range( width ) :
				for component in range( _COLOR_COMPONENTS ) :
					i = ( imageRow * width + col ) * _COLOR_COMPONENTS + component
					pixels[ i ] = int( img[row][col][component] * 255.99 )
		
		
		# Give this renderer a new image and sprite based on these pixels.
		
		self.newImage( width, height, pixels )
	
	
	
	
	# Draw this renderer's current image.
	
	def draw( self ) :
	
	
		# All it takes to draw is running Pyget's event loop, which will call the "draw"
		# callback.
		
		pyglet.app.run()
