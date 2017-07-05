# A collection of operations that define various symmetry operations to help build
# three-dimensional crystals

# Copyright 2016 by Amelia Mindich and Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/).


from VectorOps import dot3, subtract3, add3, scale3, transpose, matrixMultiply
from MathUtilities import nearlyEqual




# Classify a point as being on the boundary of, inside, or outside the halfspace bounded
# by a plane. Typically, but not necessarily, the plane is a symmetry plane and the
# point comes from some object being clipped to the plane before being reflected across
# it. I define the plane by its normal vector and a constant d such that the dot product
# of the normal with a point in the plane equals d. The normal to the plane is considered
# to point out of the halfspace for purposes of defining "inside" and "outside." Both the
# normal and the point are represented as 3-element (or 4 if in homogeneous coordinates)
# lists of x, y, and z components, This function returns an integer classification ON,
# INSIDE, or OUTSIDE.

INSIDE = -1
ON = 0
OUTSIDE = 1

def clipClass( point, normal, d ) :
	
	
	# The point is inside, on, or outside the halfspace according to whether its dot
	# product with the boundary's normal is less than, equal to, or greater than d.
	
	dotProd = dot3( point, normal )
		
	return ON if nearlyEqual( dotProd, d ) \
		   else INSIDE if dotProd < d \
		   else OUTSIDE




# Find the point at which a line intersects a plane. Typically, though not inevitably,
# the line will be an edge of a crystal and the plane will be a symmetry plane. The first
# two arguments are points on the line, given as 3-element (or 4 if in homogeneous
# coordinates) lists of x, y, and z components. The other arguments are the plane's
# normal (nx, ny, nz) and the constant d from the implicit equation for the plane,
# nx * x + ny * y + nz * z = d. This returns the intersection point as a 3-element list,
# or raises a ValueError exception if the line is parallel to the plane.

def linePlaneIntersection( p1, p2, normal, d ) :
	
	
	# Find the vector, u, from the starting point, p1, to the ending point, p2, of the
	# line segment.
	
	u = subtract3( p2, p1 )

	
	# Defining the line by the parametric form v1 + t*u, find the t value at which it
	# intersects the plane. See my project notes for June 23, 2017 for the derivation of
	# this calculation.

	denominator = dot3( normal, u )
	
	if nearlyEqual( denominator, 0 ) :					# Check that line isn't parallel to plane
		raise ValueError( "Intersection between parallel line and plane" )
	
	t = ( d - dot3(normal,p1) ) / denominator
	
	
	# Use the t value to find an actual point where the line intersects the plane.
	
	return add3( p1, scale3( u, t ) )




# Transform a list of vertices in homogeneous coordinates by applying a 4-by-4
# transformation matrix to them. Returns the list of transformed vertices. 

def transform4( vertices, transformation ) :
	
	Intermediate = transpose( vertices )

	Mult = matrixMultiply( transformation, Intermediate )
	return transpose( Mult )




# Transform a single point or vector in homogeneous coordinates (i.e., a 4-element row
# vector) by applying a 4-by-4 transformation matrix to it. Return the resulting row
# vector.

def transformRow4( v, transformation ) :
	
	
	# Build a column vector from the row, multiply it by the transformation, and return
	# a row vector built from the resulting column.
	
	column = [ [x] for x in v ]
	transformedColumn = matrixMultiply( transformation, column )
	return [ r[0] for r in transformedColumn ]
