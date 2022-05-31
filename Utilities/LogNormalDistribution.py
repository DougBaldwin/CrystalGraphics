# A class that represents standard lognormal probability distributions, i.e.,
# distributions in which the logarithms of the values are normally
# distributed. In a standard lognormal distribution, as here, the median random
# value is 1, but the distribution of values around that median is governed by
# a client-provided shape parameter. For more about these distributions, see
#		https://www.itl.nist.gov/div898/handbook/eda/section3/eda3669.htm

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.


from ProbabilityDistribution import ProbabilityDistribution
from math import exp, log, sqrt, pi
from random import lognormvariate




class LogNormalDistribution ( ProbabilityDistribution ) :
	
	
	
	
	
	# Initialize a lognormal distribution with its shape parameter.
	
	def __init__( self, shape ) :
		
		self.sigma = shape
	
	
	
	
	# Pick a sample value from this lognormal distribution.
	
	def sample( self ) :
		
		
		# A standard lognormal distribution has (I believe) a corresponding
		# normal distribution whose mean is 0. I can use that, with this
		# distribution's shape parameter as the standard deviation of the
		# normal distribution, to draw the sample using Python's library
		# function for lognormal samples.
		
		return lognormvariate( 0.0, self.sigma )
	
	
	
	
	# Calculate the value of a lognormal distribution PDF at a given x value.
	
	def pdf( self, x ) :
		
		
		# As long as x > 0, calculate the PDF from the formula give in the
		# reference. But if X <= 0, set the PDF to 0.
		
		result = 0.0 if x <= 0.0 else exp( -log(x)**2 / ( 2.0 * self.sigma ** 2 ) ) / ( x * self.sigma * sqrt( 2.0 * pi ) )
		return result
