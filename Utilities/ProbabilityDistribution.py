# A class that represents probability distributions. This class is the root of
# a hierarchy of probability distribution classes, and is mostly a place to
# document how I expect probability distributions to work in general. In
# particular, every probability distribution provides the following methods to
# clients, although specific implementations depend on the distribution:
#   o pdf( x ). Calculate the PDF value associated with x.
#   o sample(). Draw a random sample from the distribution.
# Probability distributions also have constructors that take whatever
# parameters the particular distribution needs.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.




class ProbabilityDistribution :
	
	
	
	
	# All state associated with a probability distribution is maintained by
	# subclasses, so this superclass no constructor.
	
	
	
	
	# A stub for sampling from a probability distribution. This reminds its
	# user that it ought to be over-ridden by a subclass, but returns 0 in
	# order to give programmers marginally useful values while they're
	# developing and testing those subclasses.
	
	def sample( self ) :
		
		print( "ProbabilityDistribution.sample needs to be over-ridden by subclasses." )
		return 0.0
	
	
	
	
	# A stub for calculating a PDF value for a probability distribution. This
	# mainly reminds its user that some subclass needs to over-ride the stub,
	# but it also returns 0 as the PDF value so that programmers can get some
	# value to work with while developing subclasses.
	
	def pdf( self, x ) :
		
		print( "ProbabilityDistribution.pdf needs to be over-ridden by subclasses." )
		return 0.0
