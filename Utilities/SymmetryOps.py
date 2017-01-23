# A collection of operations that define various symmetry operations to help build
# three-dimensional crystals

# Copyright 2016 by Amelia Mindich and Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/).


from VectorOps import transpose, matrixMultiply




# Transform a list of vertices in homogeneous coordinates by applying a 4-by-4
# transformation matrix to them. Returns the list of transformed vertices. 

def transform4( vertices, transformation ) :
	
	Intermediate = transpose( vertices )

	Mult = matrixMultiply( transformation, Intermediate )
	return transpose( Mult )