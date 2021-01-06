# A record class that represents axis-aligned rectangles in a coordinate plane. That plane
# is nominally the xz plane of a 3 dimensional coordinate system because of the
# application I developed this class for, but clients can actually map it to any plane
# they want. In any case, I represent these rectangles by their minimum and maximum
# coordinates in each dimension, so that the fields available to clients are named "minX,"
# "minZ," "maxX," and "maxZ."

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2019. Created by Doug Baldwin to support a program that models and renders
#	  crystal aggregates.




class Rectangle :
	
	
	
	
	# Initialize a rectangle with its bounds in each dimension.
	
	def __init__( self, minX, maxX, minZ, maxZ ) :
		
		self.minX = minX
		self.maxX = maxX
		self.minZ = minZ
		self.maxZ = maxZ
	
	
	
	
	# Generate a string that represents a rectangle as a Cartesian product of intervals in
	# the reals.
	
	def __str__( self ) :
		return "[{},{}] × [{},{}]".format( self.minX, self.maxX, self.minZ, self.maxZ )
	
	
	
	
	# Determine whether two rectangles have a non-empty (including possibly a line or
	# point) overlap. Return True if so, or False if not.
	
	def overlaps( self, other ) :
		
		
		# Rectangles overlap if, in both dimensions, the highest coordinate of one is
		# larger than the smallest coordinate of the other, while the smallest coordinate
		# is less than the larger of the other.
		
		return self.maxX >= other.minX and self.minX <= other.maxX and self.maxZ >= other.minZ and self.minZ <= other.maxZ
