# A collection of utility functions for working with linear systems of equations. I
# generally represent a system of equations as a Python list of lists, where each inner
# list is one of the equations in the system. These lists are of the form [A1,A2,...,An,Y],
# representing the equation A_1 x_1 + A_2 x_2 + ... + A_n x_n = Y. I return results as
# lists of vectors, where in general a list of the form [v0,v1,...,vn] represents a set of
# solutions of the form v_0 + t_1 v_1 + ... + t_n v_n where the t_i are parametric
# variables. Thus a 1-element list represents a unique solution to a system, a 0-element
# list indicates that there are no solutions, and longer lists indicate infinite numbers
# of solutions of various dimensionalities.

# Copyright 2019 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)

# History:
#
#   June 2019 -- Created by Doug Baldwin.


from MathUtilities import nearlyEqual




# Solve a system of n equations in n or fewer variables, i.e., a system that is
# represented by a list of n lists, each of (n+1) or fewer elements. See the comments at
# the beginning of this file for a description of the form of systems of equations and
# results. This function guarantees not to change the contents of the system of equations
# while solving it. This function also requires all equations in the system to be the same
# length.

def solve( originalEqns ) :
	
	
	# Make a copy of the list of equations to work in; that copy will get drastically
	# changed, but the originals won't.
	
	equations = [ e.copy() for e in originalEqns ]
	
	
	# This function's basic strategy is Gauss-Jordan reduction. The way I implement it
	# assumes there are at least as many equations as there are variables. If the client
	# provided a system with  fewer equations than variables, pad it with equations that
	# basically say "0 = 0."
	
	nVars = len( equations[0] ) - 1
	nEqns = len( equations )
	
	if nEqns < nVars :
		equations += [ [0] * ( nVars + 1 ) for i in range( nEqns, nVars ) ]
	
	
	# Thinking of the equations as a matrix, try to zero out all but one use of each
	# variable (i.e., all but one element in each column). Ideally, if there are n
	# variables, the first n rows (equations) will form an identity matrix in their first
	# n columns. However, this won't always be possible, notably when the system has
	# infinitely many solutions, so at least put the matrix into a form where the first
	# few rows all have 1s as their leftmost non-zero element, and the positions of those
	# 1s increase as row index increases. To do this I keep track of which variable I'm
	# trying to give a leading 1 coefficient to, and which equation I'm trying to do it
	# with. When the variable number exceeds the number of variables in the system, I'm
	# done.
	
	v = 0												# The index of the variable I'm working on
	e = 0												# The index of the equation I'm working in
	
	while v < nVars :
		
		
		# For best numerical results, I want the e-th equation to be the one with the
		# largest (in absolute value) coefficient for the v-th variable, at least among
		# equations that haven't already been used. This largest coefficient is the
		# "pivot." Find it.
		
		p = e											# Assume the pivot is already in equation e
		absPivot = abs( equations[e][v] )
		
		for r in range( e + 1, nEqns ) :
			pivotCandidate = abs( equations[r][v] )
			if pivotCandidate > absPivot :
				p = r
				absPivot = pivotCandidate
		
		
		# Equation p is now known to contain the pivot. What I do with that fact depends
		# on whether that pivot is 0 or not.
		
		if nearlyEqual( absPivot, 0.0 ) :
		
			# If the pivot is 0, none of the remaining equations depend on it, and so I'll
			# never be able to 0 it out any more than it already is. Go on to the next
			# variable in the same equation and hope I can do better with it.
			
			v += 1
			continue
			
		
		else :
		
			# If the pivot is non-zero, I can use it to zero out all uses of variable v
			# except in equation e. To do that, first swap the equation with the pivot
			# into row e of the matrix...
			
			swapRows( equations, p, e )
			
			
			# ...then scale that equation so the pivot coefficient becomes 1...
			
			pivotRow = equations[e]
		
			for scaleIndex in range( v + 1, nVars + 1 ) :
				pivotRow[scaleIndex] /= pivotRow[v]
		
			pivotRow[v] = 1.0
		
		
			# ... and finally subtract a multiple of row e from each other row, the
			# multiple being chosen to make the coefficient of variable v become 0 in each
			# other equation.
			
			for r in range( nEqns ) :
				if r != e :
					currentRow = equations[r]
					multiplier = currentRow[v]
					for combineIndex in range( v + 1, nVars + 1 ) :
						currentRow[combineIndex] -= pivotRow[combineIndex] * multiplier
					currentRow[v] = 0.0
			
			
			# Now I can go on to use the next equation to zero out the next variable.
			
			v += 1
			e += 1
	
	
	# The equation matrix is now reduced. Now I can build the general solution,
	# v_0 + t_1 v_1 + ... + t_n v_n using the following ideas: every variable associated
	# with one of the leading 1s in the reduced equations puts the corresponding value
	# from the constant's column of the matrix into v_0, i.e., if variable v is associated
	# with a leading 1 in some equation, then the v-th element of v_0 is equal to the
	# constant from that equation. Every
	# variable not associated with a leading 1 is essentially a parameter in the
	# parametric solution, i.e., if variable v is not associated with a leading 1, then
	# one of the v_i has a 1 in position v; additionally, if variable v has a non-zero
	# coefficient, c, in the equation whose leading 1 is associated with variable u, then
	# position u in v_i is equal to -c. However, if at any point I find an equation whose
	# coefficients are all 0s but whose constant is not 0, then all of the above is moot
	# because the system has no solution.
	
	v0 = [0] * nVars							# Assume there will be a v_0, although I don't know its value yet.
	solution = [ v0 ]
	
	v = 0										# Ideally I'll pick up 1 variable for v_0 per equation...
	e = 0										# ...but be prepared to step through variables and equations independently
	
	while v < nVars :
		
		
		# Skip leading 0s in the current equation. Each value of v I skip represents
		# another parameter I've discovered, which therefore needs a vector of
		# coefficients added to the solution.
		
		while v < nVars and nearlyEqual( equations[e][v], 0 ) :
			
			newCoefficients = []
			for j in range( nVars ) :
				newCoefficients.append( -equations[j][v] )
			newCoefficients[v] = 1.0
			solution.append( newCoefficients )
			
			v += 1
		
		
		# If skipping stopped at a non-zero coefficient, which had better be 1, copy the
		# constant from this equation to variable v's slot in the v_0 vector, and look for
		# future variables in the next equation.
		
		if  v < nVars :
		
			# Found a non-zero coefficient; assume it's 1. Copy the constant
			
			v0[v] = equations[e][nVars]			
			v += 1
			e += 1
	
	
	# Values have been assigned to all variables. Every equation from index e to the end
	# must have only 0 coefficients, by the way pivoting brings rows with non-zero leading
	# coefficients towards the top of the matrix. So check that all those remaining
	# equations are of the form 0 = 0, i.e., have 0s in their constant column.
	
	for constant in [ equation[nVars] for equation in equations[e:nEqns] ] :
		if not nearlyEqual( constant, 0.0 ) :
			return []
	
	
	# I never saw any sign that the system isn't solvable, so I've got a solution!
	
	return solution
			
			




# A utility function that swaps 2 rows in a matrix, represented as a list of lists, each
# inner list being a row of the matrix. This function receives the matrix and the indices
# of the rows to swap as arguments; it changes the matrix in place and so has no explicit
# return value.

def swapRows( matrix, i, j ) :
	temp = matrix[i]
	matrix[i] = matrix[j]
	matrix[j] = temp
	
	



# Unit tests.

if __name__ == "__main__" :
	
	
	# A system with 1 solution:
	#   x + y + z = 1
	#   x - y + z = 1
	#   x + y - z = 1
	# with solution x = 1, y = 0, z = 0.
	
	print( "Solve x + y + z = 1, x - y + z = 1, x + y - z = 1; should be x=1, y=0, z=0:" )
	print( solve( [[1,1,1,1], [1,-1,1,1], [1,1,-1,1]] ) )
	print()
	
	
	# A system with infinitely many solutions:
	#   x + y + z = 1
	#   x - y + z = 1
	# which has solution (x,y,z) = (1,0,0) + t(-1,0,1)
	
	print( "Solve x + y + z = 1, x - y + z = 1; should be (x,y,z) = (1,0,0) + t(-1,0,1):" )
	print( solve( [[1,1,1,1], [1,-1,1,1]] ) )
	print()
	
	
	# A system with no solutions:
	#   x + y + z = 1
	#   x - y + z = 1
	#   x + y + z = 2
		
	print( "Solve x + y + z = 1, x - y + z = 1, x + y + z = 2; should have no solutions" )
	print( solve( [[1,1,1,1], [1,-1,1,1], [1,1,1,2]] ) )
	print()
	
	
	# A system with nontrivial pivoting:
	#    2x +  y + z = 7
	#     x +  y - z = 0
	#    4x - 3y + z = 1
	# which has solution x = 1, y = 2, z = 3.
		
	print( "Solve 2x + y + z = 7, x + y - z = 0, 4x - 3y + z = 1; should be x=1, y=2, z=3:" )
	print( solve( [[2,1,1,7], [1,1,-1,0], [4,-3,1,1]] ) )
	print()
	
	
	# A system with infinitely many solutions despite having n equations in n unknowns:
	#    x + y + z =  1
	#    x - y - z = -1
	#   3x - y - z = -1
	# which has solutions (x,y,z) = (0,1,0) + t(0,-1,1)
	
	print( "Solve x + y + z = 1, x - y - z = -1, 3x - y - z = -1; should be (x,y,z) = (0,1,0) + t(0,-1,1)" )
	print( solve( [[1,1,1,1], [1,-1,-1,-1],[3,-1,-1,-1]] ) )
	print()
	
	
	# A system with other than 3 variables:
	#   x +  y = 0
	#   x - 2y = 1.5
	# which has solutions x = 0.5, y = -0.5
		
	print( "Solve x + y = 0, x - 2y = 1.5; should be x = 0.5, y = -0.5" )
	print( solve( [[1,1,0], [1,-2,1.5]] ) )
	print()
	
	
	# A system that is already solved, but has infinitely many solutions:
	#   x = 1
	#   z = 1
	# Formally, solutions to this have parametric form (1,0,1) + t(0,1,0).
	
	print( "Solve x = 1, z = 1; should be (x,y,z) = (1,0,1) +  t(0,1,0)" )
	print( solve( [[1,0,0,1],[0,0,1,1]] ) )
	print()
	
	
	# A system that is already "solved" in a form that looks like it has infinitely
	# many solutions, except for an impossible equation at the end:
	#   y = 1
	#   z = 0
	#   0 = 1
	# Exercises a bug fixed July 9, 2019.
	
	print( "Solve y = 1, z = 0, 0 = 1; should have no solutions." );
	print( solve( [[0,1,0,1],[0,0,1,0],[0,0,0,1]] ) )
	print()
	
	
	# A system that has infinitely many solutions, parameterized by two variables:
	#   x + y + z = 1
	# whose solution is (x,yz) = (1,0,0) + u(-1,1,0) + t(-1,0,1)
	
	print( "Solve x + y + z = 1; should be (x,y,z) = (1,0,0) + t(-1,1,0) + u(-1,0,1)" )
	print( solve( [[1,1,1,1]] ) )
	print()
