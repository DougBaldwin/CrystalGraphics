# A collection of utility functions for doing miscellaneous low-level mathematical
# operations useful in computer graphics.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   June 2017 -- Created by Doug Baldwin.




# Determine whether two double-precision real numbers are nearly equal. For most purposes,
# clients can use this function to test whether two numbers that might contain a small
# amount of round-off error are equal except for that round-off. However, the relation
# this function actually implements isn't an equivalence relation (it's not transitive),
# and so there will be some situations in which it isn't a drop-in replacement for
# actual equality.

def nearlyEqual( x, y ) :

	tolerance = 1e-10
	
	if -tolerance < y < tolerance :
		return -tolerance < x < tolerance
	else :
		return 1 / (1+tolerance)  <  x / y  <  1 + tolerance




# Determine whether all elements of some list satisfy a predicate, returning True if so
# and False if not.

def allSatisfy( predicate, list ) :

	return all( map( predicate, list ) )
