# A collection of utility functions for performing vector arithmetic useful in graphics.
# The vectors that these functions work with are of fixed length, for now always 3
# elements, represented as Python lists.

# Copyright 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from math import sqrt




# Compute the length of a 3D vector

def length3( v ) :
	return sqrt( v[0]**2 + v[1]**2 + v[2]**2 )




# Compute the difference between 2 vectors

def subtract3( v1, v2 ) :
	return [ v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2] ]




# Compute the scalar product of a 3D vector and a scalar.

def scale3( v, a ) :
	return [ a * v[0], a * v[1], a * v[2] ]




# Compute the dot product of two 3D vectors.

def dot3( v1, v2 ) :
	return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]




# Calculate the cross product of two vectors (v1 X v2, in that order)

def cross( v1, v2 ) :
	return [ v1[1] * v2[2] - v2[1] * v1[2],
			 v2[0] * v1[2] - v1[0] * v2[2],
			 v1[0] * v2[1] - v2[0] * v1[1] ]




# Scale a 3D vector to unit length.

def normalize3( v ) :
	length = length3( v )
	return [ v[0] / length, v[1] / length, v[2] / length ]




# Given two 3D vectors, compute a new vector that points more or less in the same
# direction as the first, but is orthogonal to the second.

def orthogonalize3( source, reference ) :
	return subtract3( source, scale3( reference, dot3( source, reference ) / length3( reference ) ** 2 ) )




# Multiply two matrices. The matrices can be of any compatible sizes, but should be
# represented as lists of lists, where each inner list is a row.

def matrixMultiply( M1, M2 ) :
	
	
	# Use the textbook "iterate over all rows and columns" algorithm to multiply the
	# matrices, assuming the matrices are properly formed so that the number of items
	# in the first row of a matrix is the number of items in all rows.
	
	rows1 = len( M1 )
	cols1 = len( M1[0] )
	cols2 = len( M2[0] )
	
	product = []
	
	for r1 in range( rows1 ) :
		product = product + [ [0] * cols2 ]
		for c2 in range( cols2 ) :
			for i in range( cols1 ) :
				product[r1][c2] = product[r1][c2] + M1[r1][i] * M2[i][c2]
	
	return product