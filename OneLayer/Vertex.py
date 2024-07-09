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




from math import sqrt




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




	# Calculate the distance between this vertex and another.

	def distance( self, other ) :
		return sqrt( (self.x - other.x) ** 2 + (self.y-other.y) ** 2 + (self.z-other.z) ** 2 )




	# Write this vertex to a stream, using (or creating) an ID number for it
	# from an ID manager. See my August 17, 21, and 22, 2023, project notes for
	# more on why I want to write geometry to streams, some of how I do it, and
	# the stream format.

	def write( self, stream, ids ) :

		# No matter what, identify this geometry as a vertex.
		stream.write( "[Vertex " )

		# If the ID manager already knows about this vertex, just write its ID.
		if ids.contains( self ) :
			stream.write( "{}]\n".format( ids.find(self) ) )

		else :
			# Otherwise, give the vertex an ID and write it out in detail.
			id = ids.next()
			ids.store( self, id )

			stream.write( "{} {} {} {}]\n".format( id, self.x, self.y, self.z ) )
