# A class that represents vertices of polyhedra in my effort to draw realistic
# amethyst aggregates as sets of clipped polyhedra with sizes taken from an
# appropriate probability distribution. See my crystal aggregates project notes
# for 2021 for more about this project.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.


from VectorOps import dot3
from math import isclose




class Vertex :
	
	
	
	
	# I represent vertices by their X, Y, and Z coordinates, in member
	# variables x, y, and z.
	
	
	
	
	# Initialize a vertex from its X, Y, and Z coordinates.
	
	def __init__( self, x, y, z ) :
		
		self.x = x
		self.y = y
		self.z = z
	
	
	
	
	# Create a human-readable representation of this vertex, showing an ID that
	# is unique to this vertex and its coordinates.
	
	def __str__( self ) :
		
		numberFormat = "{:.7g}"
		return "<Vertex " + hex( hash(self) ) \
						  + " = " + numberFormat.format( self.x ) \
						  + ", " + numberFormat.format( self.y ) \
						  + ", " + numberFormat.format( self.z ) + ">"
	
	
	
	
	# Decide whether this vertex lies on the "outside" or "inside" of a plane
	# defined by equation Ax + By + Cz = D. The "outside" of the plane is the
	# side towards which the normal vector <A,B,C> points. This method returns
	# a positive number if the vertex lies outside the plane, a negative number
	# if it lies inside, and 0 if the vertex lies on the plane.
	
	def sideOfPlane( self, A, B, C, D ) :
		
		
		# This vertex's dot product with the plane's normal is less than D,
		# equal to D, or greater than D according to whether the vertex is
		# inside, on, or outside the plane. So calculate the dot product and
		# subtract D to get a return value.
		
		return dot3( [self.x,self.y,self.z], [A,B,C] ) - D
	
	
	
	
	# Decide whether two vertices are close to each other, in particular close
	# enough that they are probably the same point. This returns True if this
	# vertex is that close to the other, and False otherwise.
	
	def isCloseTo( self, other ) :
	
		return isclose( self.x, other.x ) and isclose( self.y, other.y ) and isclose( self.z, other.z )
