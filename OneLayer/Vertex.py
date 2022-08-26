# A class that represents vertices of polyhedra in my effort to draw realistic
# amethyst aggregates as sets of clipped polyhedra with sizes taken from an
# appropriate probability distribution. See my crystal aggregates project notes
# for more about this project.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin, based on an earlier version.
#
#   June 2021. Original version created by Doug Baldwin.




class Vertex :
	
	
	
	
	# I represent vertices by their X, Y, and Z coordinates, in member
	# variables x, y, and z.
	
	
	
	
	# Initialize a vertex from its X, Y, and Z coordinates.
	
	def __init__( self, x, y, z ) :
		
		self.x = x
		self.y = y
		self.z = z




	# Retrieve this vertex's coordinates as a 3-element list (i.e., the form
	# most of the current vector utilities work on.

	def coordinates( self ) :

		return [ self.x, self.y, self.z ]
