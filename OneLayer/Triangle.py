# A class that represents open 2-dimensional triangles, nominally in the  xz plane. These
# triangles have a definite apex, but are "open" in that they extend indefinitely along
# the two sides adjacent to that apex. These triangles can represent cross sections
# through the center and one face of a crystal where those sections simply extend outward
# until they meet another crystal. See file "OneLayer.py" for a program that uses these
# triangles in that way (and, in fact, for which this class was designed).

# Copyright (C) 2018 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2018 -- Created by Doug Baldwin.


from MathUtilities import nearlyEqual, lessOrNearlyEqual
import sys




class Triangle :
	
	
	
	
	# Triangles store the following information about themselves...
	#   o apex - The apex.
	#   o vertex1 - The reference point for the triangle's 1st side, in clockwise order.
	#   o vertex2 - The reference point for the triangle's 2nd side.
	
	
	
	
	# Initialize a triangle with its apex and a point on each adjacent side. The 2nd side
	# point should be clockwise from the 1st when viewing the triangle from above. All 3
	# points are represented by 2-element lists, containing the x and z coordinates of the
	# point.
	
	def __init__( self, apex, vertex1, vertex2 ) :
		
		self.apex = apex
		self.vertex1 = vertex1
		self.vertex2 =  vertex2
	
	
	
	
	# Return the apex of this triangle, as a 3-element list containing the x, y, and z
	# coordinates of the apex, in that order. Because triangles lie in the xz plane, the
	# y coordinate is always 0. Nonetheless, returning a 3-element list is useful when
	# code that works in a 3D world has to interact with triangles.
	
	def getApex( self ) :
		return [ self.apex[0], 0.0, self.apex[1] ]
	
	
	
	
	# Find the "t" value at which a triangle first encloses the center of an amethyst.
	# These t values are abstract measures of how close the center is to the triangle's
	# apex, with smaller values meaning closer. In principle negative t values mean that
	# the amethyst is behind the triangle's apex relative to the direction in which the
	# triangle opens, but this method will never return a negative t, it will return a
	# nearly infinite one instead, meaning that the triangle never grows to enclose the
	# amethyst.
	
	def amethystT( self, amethyst ) :
		
		
		# Calculate the t value at which it would be possible for the amethyst's center
		# to lie on the edge of this triangle opposite the apex. See the project notes
		# from June 12, 2018 for the derivation of the formula I use.
		
		# The numerator and denominator in the formula for t are both calculated in the
		# same basic way, just differing in the x and z values they use:
		
		def tTerm( x, z ) :
			return   ( x - self.apex[0] ) * ( self.vertex1[1] - self.vertex2[1] ) \
				   - ( z - self.apex[1] ) * ( self.vertex1[0] - self.vertex2[0] )
		
		
		position = amethyst.getPosition()
		amethystX = position[0]
		amethystZ = position[2]
		
		t = tTerm( amethystX, amethystZ ) / tTerm( self.vertex2[0], self.vertex2[1] )
		
		
		# Check that t is positive and that the corresponding parameter for where the
		# amethyst is between the edges of the triangle is between 0 and 1 (otherwise the
		# amethyst lines up with the triangle but is outside of it). If any of these tests
		# fail, the t value is infinite. Note that all tests are such that the amethyst
		# must be strictly inside the triangle, not on its boundary.
		
		if lessOrNearlyEqual( t, 0 ) :
			return sys.float_info.max
		
		s =   ( amethystX - self.apex[0] - t * ( self.vertex2[0] - self.apex[0] ) ) \
			/ (t * ( self.vertex1[0] - self.vertex2[0] ))
		
		if lessOrNearlyEqual( s, 0 ) or lessOrNearlyEqual( 1, s ) :
			return sys.float_info.max
		
		return t
	
	
	
	
	# Find the "t" values at which the sides of a triangle intersect a line. See comments
	# for the "amethystT" method for a discussion of "t" values. The line is defined by
	# the coefficients for an equation of the form ax + bz = c, and this function returns
	# two t values, the first indicating when the first side of this triangle intersects
	# that line and the second indicating when the second side intersects it. Either t
	# value can be the maximum representable floating point value if a side doesn't
	# intersect the line.
	
	def lineT( self, a, b, c ) :
		
		
		# A utility function that calculates the t value for the intersection of a line
		# through this triangle's apex and a given point (represented as a 2-element list
		# of x and z coordinates) and ax + by = c. See the June 15, 2018 project notes for
		# an explanation of the equation used here.
		
		def intersection( point ) :
		
			dx = point[0] - self.apex[0]			# X component of the vector from apex to point
			dz = point[1] - self.apex[1]			# Z component of the same vector
			
			denominator = a * dx + b * dz
			
			if nearlyEqual( denominator, 0.0 ) :
				return sys.float_info.max
			
			t = ( c - a * self.apex[0] - b * self.apex[1] ) / denominator
			
			if lessOrNearlyEqual( t, 0 ) :
				return sys.float_info.max
			else :
				return t
		
		
		# Use the above function to find t values for each side.
		
		return ( intersection(self.vertex1), intersection(self.vertex2) )
	
	
	
	
	# Given a "t" value, calculate the corresponding points on a triangle's first and
	# second sides. See the comments for the "amethystT" method for a definition of "t"
	# values. The returned point is represented as a two-element list containing the x
	# and z coordinates, in that order.
	
	def side1Pt( self, t ) :
		return self.evaluateSide( self.vertex1, t )
		
	
	def side2Pt( self, t ) :
		return self.evaluateSide( self.vertex2, t )
	
	
	
	
	# A utility method that finds a point on a side of this triangle. Specifically, it
	# treats that side as a parametric line between the apex and point provided as a
	# parameter, and returns the point that line reaches at the given t value. This
	# returns that point as a  2-element list containing the x and z coordinates, in that
	# order.
	
	def evaluateSide( self, point, t ) :
		
		deltaX = point[0] - self.apex[0]			# Change in x from apex to point
		deltaZ = point[1] - self.apex[1]			# Change in z
		
		return [  self.apex[0] +  t * deltaX,  self.apex[1] + t  * deltaZ  ]
