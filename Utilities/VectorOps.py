# A collection of utility functions for performing vector arithmetic useful in graphics.
# The vectors that these functions work with are of fixed length, either 3 or 4 elements,
# represented as Python lists. 3-element vectors are generally vectors in 3-space, which
# may also represent points, while 4-element lists are 3-space vectors or points in
# homogeneous form, i.e., those with a 4th component of 0 are vectors (contain only
# directional information) while those with a 4th component of 1 are points (contain
# positional information as well as directional).

# Copyright 2016 by Doug Baldwin.
# Additional contributions ("transpose" function) by Amelia Mindich.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from math import sqrt




# Compute the length of a 3D vector.

def length3( v ) :
	return sqrt( v[0]**2 + v[1]**2 + v[2]**2 )




# Compute the sum of 2 3D vectors.

def add3( v1, v2 ) :
	return [ v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2] ]




# Compute the sum of 2 points or vectors in homogeneous form. In order to make geometric
# sense, at most one of the arguments should be a point. With that restriction the sum
# of 2 vectors will be a vector, while the sum of a vector and a point will be another
# point.

def add4( v1, v2 ) :
	return [ v1[0] + v2[0], v1[1]+ v2[1], v1[2] + v2[2], v1[3] + v2[3] ]




# Compute the difference between 2 3D vectors.

def subtract3( v1, v2 ) :
	return [ v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2] ]




# Compute the difference between 2 points or vectors in homogeneous form. In order to
# make geometric sense, either both arguments should be points, or both should be vectors.
# Then the difference of 2 points will be the vector between them, while the difference
# of 2 vectors will be another vector.

def subtract4( v1, v2 ) :
	return [ v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2], v1[3] - v2[3] ]




# Compute the scalar product of a 3D vector and a scalar.

def scale3( v, a ) :
	return [ a * v[0], a * v[1], a * v[2] ]




# Scale a vector or point in homogeneous form by multiplying the first 3 components by a
# scalar while leaving the fourth component unchanged. This ensures that points scale to
# points and vectors to vectors.

def scale4H( v, a ) :
	return [ a * v[0], a * v[1], a * v[2], v[3] ]




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




# Transpose matrix M. M is any matrix, represented as a list of lists, with each inner list
# being a row (all inner lists must thus be of the same length). This function returns a
# new matrix in which the rows are the columns of M and the columns are the rows of M.

def transpose( M ):


	# All rows (j) become columns and all columns (i) become rows by copying the row values
	# into the column values

	result = [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]
	
	return result
