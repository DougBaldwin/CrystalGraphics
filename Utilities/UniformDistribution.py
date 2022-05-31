# A class that represents uniform probability distributions over an interval
# in the real numbers.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.


from ProbabilityDistribution import ProbabilityDistribution
from random import uniform




class UniformDistribution ( ProbabilityDistribution ) :
	
	
	
	
	# Initialize a uniform distribution from the ends of its interval.
	
	def __init__( self, low, high ) :
		
		self.low = low
		self.high = high
	
	
	
	
	# Draw a sample value from this uniform distribution.
	
	def sample( self ) :
		
		return uniform( self.low, self.high )
	
	
	
	
	# The PDF value for any value between the bounds is the reciprocal of the
	# interval length; for any value outside the bounds the PDF is 0.
	
	def pdf( self, x ) :
		
		if x >= self.low and x <= self.high :
			return 1.0 / ( self.high - self.low )
		else :
			return 0.0
