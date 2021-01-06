# A class that represents a rock substrate on which a layer of crystals might grow. These
# substrates are rectangular parallelepipeds, defined by their bounds in each of the 3
# dimensions. They are thus special cases of convex polyhedra, and in fact most of what
# substrates can do is just what they do by virtue of being polyhedra. The main thing this
# class provides distinct from polyhedra is a color in which to draw substrates.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin to support a program that builds single-layer
#     crystal aggregates.


from ConvexPolyhedron import ConvexPolyhedron
from Plane import Plane




class Substrate ( ConvexPolyhedron ) :
	
	
	
	
	# All substrates are a dull opaque grayish-brown color. This constant is available for
	# clients who want to draw that color.
	
	COLOR = [ 0.45, 0.43, 0.4, 1.0, 0.1, 1.0 ]
	
	
	
	
	# Initialize a substrate with its x, y, and z bounds.
	
	def __init__( self, minX, maxX, minY, maxY, minZ, maxZ ) :
		
		
		# Substrates are bounded by 6 planes. Create those planes, tell them how they
		# neighbor each other in a parallelepiped, and use them to initialize the
		# superclass.
		
		front = Plane( 0.0, 0.0, 1.0, maxZ )
		back = Plane( 0.0, 0.0, -1.0, -minZ )
		left = Plane( -1.0, 0.0, 0.0, -minX )
		right = Plane( 1.0, 0.0, 0.0, maxX )
		bottom = Plane( 0.0, -1.0, 0.0, -minY )
		top = Plane( 0.0, 1.0, 0.0, maxY )
		
		front.addNeighbors( [top,left,bottom,right] )
		back.addNeighbors( [top,right,bottom,left] )
		left.addNeighbors( [top,back,bottom,front] )
		right.addNeighbors( [top,front,bottom,back] )
		bottom.addNeighbors( [front,left,back,right] )
		top.addNeighbors( [front,right,back,left] )
		
		super().__init__( [front,back,left,right,bottom,top] )
