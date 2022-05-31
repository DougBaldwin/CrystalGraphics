# A class that represents edges of polyhedra in my project to draw realistic
# amethyst aggregates as sets of clipped polyhedra with sizes taken from an
# appropriate probability distribution. See the project notes from 2021 for
# more about this project.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International
# License (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.




from Vertex import Vertex
from math import isclose




class Edge :
	
	
	
	
	# Edges store their endpoints in member variables vertex1 and vertex2.
	
	# Edges also store a dictionary of vertices at which they have previously
	# split themselves. This allows multiple splits at the same place to use
	# the same vertex, which is important when the split is part of splitting a
	# polyhedron, and a convenient space optimization in other cases. More
	# precisely, this dictionary is keyed by integers that measure the fraction
	# of the way from the 1st to the 2nd vertex at which the split happened
	# (e.g., the integer could be the number of thousandths of the total
	# distance between the ends of the edge), and associates with each key the
	# vertex object representing the actual split point.
	
	
	
	
	# Initialize an edge, given the two vertices that it connects.
	
	def __init__( self, v1, v2 ) :
		
		self.vertex1 = v1
		self.vertex2 = v2
		
		self.splits = {}
	
	
	
	
	# Return a human-readable string representation of this edge. That
	# representation concentrates on the vertices at the ends, but ignores the
	# cached splitting points.
	
	def __str__( self ) :
		
		return "<Edge " + hex( hash(self) ) \
						+ " = " + str( self.vertex1 ) \
						+ " " + str( self.vertex2 ) \
						+ ">"
	
	
	
	
	# Split this edge where it intersects a plane given by the equation
	# Ax + By + Cz = D. Return the segments of the edge that are on the outside
	# (i.e., normalward side) and inside of the plane, and the point at which
	# the original edge intersects the plane. If the edge doesn't actually
	# intersect the plane, either the outer or inner segment will be None, as
	# will be the intersection point.
	
	def split( self, A, B, C, D ) :
		
		
		# Decide whether the edge lies entirely in the plane, entirely on the
		# outer side, entirely on the inner side, or is split by the plane. In
		# the first case, I say that the edge is on both sides of the plane but
		# with no splitting point (because an edge in the plane could be part
		# of a face on either side). In the second and third cases the edge is
		# definitively on one side or the other, and in the last case I need to
		# calculate exactly where the split is.
		
		vertex1Side = self.vertex1.sideOfPlane( A, B, C, D )
		vertex2Side = self.vertex2.sideOfPlane( A, B, C, D )
		
		if isclose( vertex1Side, 0.0 ) and isclose( vertex2Side, 0.0 ) :
			return self, self, None
		
		elif vertex1Side >= 0 and vertex2Side >= 0 :		# Both sides can't equal 0 because of the first test,
			return self, None, None							# but either one might
		
		elif vertex1Side <= 0 and vertex2Side <= 0 :
			return None, self, None
		
		else :
			
			
			# The edge is split by the plane. Use equations from June 23, 2017
			# project notes to find the intersection point.
			
			divisor = A * ( self.vertex2.x - self.vertex1.x ) + B * ( self.vertex2.y - self.vertex1.y ) + C * ( self.vertex2.z - self.vertex1.z )
			
			if isclose( divisor, 0.0 ) :
				# Another case in which the edge seems to lie in the plane.
				return self, self, None
			
			t = ( D - A * self.vertex1.x - B * self.vertex1.y - C * self.vertex1.z ) / divisor
			
			splitPt = self.getSplitPoint( t )
			
			if vertex1Side > 0 :
				
				# Vertex 1 is outside the plane, so the outside part of the
				# split runs from the intersection point to vertex 1, and the
				# inside part from vertex 2 to the intersection.
				
				outsideEdge = Edge( splitPt, self.vertex1 )
				insideEdge = Edge( self.vertex2, splitPt )
			
			else :
			
				# Vertex 1 is inside the plane.
				
				outsideEdge = Edge( splitPt, self.vertex2 )
				insideEdge = Edge( self.vertex1, splitPt )

			return outsideEdge, insideEdge, splitPt
	
	
	
	
	# Return the vertex at the opposite end of this edge from the given
	# vertex.
	
	def oppositeEnd( self, v ) :
		
		return self.vertex1 if self.vertex2.isCloseTo( v ) else self.vertex2
	
	
	
	
	# Find and return the point that lies a given fraction of the distance
	# between this edge's first and second vertices. If a suitable point is
	# already in this edge's dictionary of splits, return it. Otherwise create
	# a new point, add it to the dictionary, and return it. In all cases I
	# return the point as a Vertex object.
	
	def getSplitPoint( self, fraction ) :
		
		
		# Generate an integer key for this (real) fraction. At the moment, I
		# use the fraction, in thousandths of a unit.
		
		keyFraction = int( fraction * 1000 )
		
		
		# If the key is in the splits dictionary, use the vertex associated
		# with it. Otherwise make a new vertex.
		
		if keyFraction in self.splits :
			return self.splits[ keyFraction ]
		
		else :
		
			newVertex = Vertex( splitValue( self.vertex1.x, self.vertex2.x, fraction ),
								splitValue( self.vertex1.y, self.vertex2.y, fraction ),
								splitValue( self.vertex1.z, self.vertex2.z, fraction ) )
			
			self.splits[ keyFraction ] = newVertex
			return newVertex




# A utility function that finds a value in between a pair of coordinates from
# two points. Specifically, this function calculates a(1-t) + bt, with typical
# usage being that a and b are the x, y, or z coordinates from two different
# points, and t is a parameter corresponding to some distance between those
# points. The calculation done by this function then finds the x, y, or z value
# at that distance.

def splitValue( a, b, t ) :
	return a * ( 1.0 - t ) + b * t
 