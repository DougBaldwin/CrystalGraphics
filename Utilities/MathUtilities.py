# A collection of utility functions for doing miscellaneous low-level mathematical
# operations useful in computer graphics.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   June 2017 -- Created by Doug Baldwin.


import sys




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




# Determine whether one number is less than or equal to another, taking possible roundoff
# errors into account. This returns True if its first argument appears less than or equal
# to its second with that stipulation, or False if not.

def lessOrNearlyEqual( x, y ) :
	return  x < y  or  nearlyEqual( x, y )




# Return a real number bigger than any other (so a plausible substitute for "infinity"
# in, e.g., comparisons).

def infinity() :
	return sys.float_info.max
