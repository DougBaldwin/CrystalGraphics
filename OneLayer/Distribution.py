# This module provides functions that sample from various probability distributions.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May 2017 -- Created by Doug Baldwin.


from random import uniform, gauss
	
	
	
	
# Draw a sample from half of a normal distribution, i.e., a distribution that more or less
# follows the normal distribution on one side of its mean but has density 0 on the other
# side. I say this distribution "more or less" follows a normal distribution because the
# actual probability density function is double that for the normal distribution wherever
# it's not 0, since these half normal distributions remove half of the domain and thus
# need double the density in what's left in order to integrate to 1 over all reals. The
# distribution sampled by this function can have non-0 density either below or above the
# mean, according to whether the standard deviation is positive (non-0 probability above
# the mean) or negative (non-0 probability below the mean).
	
def halfNormal( mean, stdDev ) :
		
		
	# Get a sample from a regular normal distribution, then find its difference from the
	# mean. If that difference has the same sign as the standard deviation, then this
	# sample is on the right side of the mean. Otherwise reflect the sample about the mean.
		
	sample = gauss( mean, abs(stdDev) )
	difference = sample - mean
		
	if difference * stdDev < 0 :			# Do difference and std dev have different signs?
		sample = mean - difference
		
	return sample

	
	
	
# Draw a sample from a uniform distribution over a hyper-rectangle in 4 dimensions. The
# arguments to this function are the bounds of the rectangle in each dimension.
	
def uniform4( minX, maxX, minY, maxY, minZ, maxZ, minW, maxW ) :
		
		
	# Each dimension is independent of the others, so generate 4 numbers uniformly
	# distributed between the appropriate bounds and return them.
		
	return ( uniform( minX, maxX ),
			 uniform( minY, maxY ),
			 uniform( minZ, maxZ ),
			 uniform( minW, maxW ) )
