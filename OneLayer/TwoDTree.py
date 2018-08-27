# Classes that represents 2D trees (i.e., kD trees with k=2) of amethysts. Most of the
# work is in classes TwoDEmptyTree and TwoDNonemptyTree, which represent empty and non-
# empty 2D tree respectively. This file also defines a base class that mostly just takes
# care of knowing whether a tree splits its root in the X dimension or the Y. These
# classes are part of a program that generates crystal aggregates consisting of a single
# layer of crystals on a substrate; see file "OneLayer.py" for more information.

# Copyright (C) 2018 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   May 2018 -- Created by Doug Baldwin.


from MathUtilities import nearlyEqual
import sys




# Constants that indicate what dimension a 2D tree uses to split itself when inserting a
# new amethyst or searching. Clients pass one or the other of these as the "dimension"
# argument when creating new 2D trees. These constants can also be used as indices to
# pick the appropriate component out of a list representing a point.

X = 0
Z = 2





#  The base class.

class TwoDTree ( object ) :
	
	
	
	
	# Internally I represent 2D trees with the following member variables:
	#   - dimension: which of a point's coordinates (i.e., which dimension) to split on
	#     when inserting or searching. 
	
	
	
	
	# Initialize a 2D tree with the dimension it should split on.
	
	def __init__( self, dimension ) :
		
		
		# Initialization just requires storing this tree's splitting dimension in the
		# corresponding member variable.
		
		self.dimension = dimension
	
	
	
	
	# Return the dimension to split on in this tree's children.
	
	def nextDimension( self ) :
		
		
		# Children split on whichever dimension this tree doesn't, which I can calculate
		# as the non-zero dimension code minus this tree's dimension code.
		
		return Z - self.dimension
		
		




#  The class that represents empty 2D trees.

class TwoDEmptyTree ( TwoDTree ) :
	
	
	
	
	# Initialize an empty 2D tree with the dimension it should split in.
	
	def __init__( self, dimension ) :
		
		super(TwoDEmptyTree,self).__init__( dimension )
	
	
	
	
	# Insert a new amethyst into an empty tree, returning the resulting non-empty tree.
	
	def insert( self, amethyst ) :
		
		
		# To insert into an empty tree, make a non-empty tree that is split at either the
		# amethyst's x coordinate or z, depending on which dimension this tree splits
		# on.
		
		return TwoDNonemptyTree( amethyst, self.dimension )
	
	
	
	
	# Apply a function to all the amethysts in this empty tree.
	
	def traverse( self, f ) :
		
		# There's nothing to do in an empty tree.
		pass
	
	
	
	
	# Nominally find the amethyst from this tree that is closest to the apex of an open
	# triangle and the associated t value. Or, if nothing in this tree is closer than
	# a client-provided amethyst and t value, return them -- which is what always
	# happens, since this is an empty tree.
	
	def getNeighbor( self, triangle, clientT, clientAmethyst ) :
		return ( clientAmethyst, clientT )






# The class that represents non-empty 2D trees.

class TwoDNonemptyTree ( TwoDTree ) :
	
	
	
	
	# I represent non-empty 2D trees with the following pieces of information (in addition
	# to the dimension information they inherit from the superclass):
	#   - mid: The coordinate value to compare against in order to decide if a point is
	#     on the high or low side of this tree.
	#   - amethysts: A list of amethysts whose coordinate in this tree's dimension is
	#     equal to "mid".
	#   - highSide: A 2D tree for the half of space with coordinates higher than "mid" in
	#     this tree's dimension.
	#   - lowSide: A 2D tree for the half of space with coordinates lower than "mid" in
	#     this tree's dimension.
	
	
	
	
	# Initialize a non-empty tree with the amethyst it contains and the dimension it
	# should split on for insertions and searches.
	
	def __init__( self, amethyst, dimension ) :
		
		
		# Initialize the superclass with this tree's dimension.
		
		super(TwoDNonemptyTree,self).__init__(  dimension )
		
		
		# Find out what this amethyst's coordinate is in the appropriate dimension, and
		# use it to set up the new tree's midpoint value. Both subtrees of the new tree
		# are empty, and split in the other dimension from the one this tree splits in.
		
		position = amethyst.getPosition()
		
		self.mid = position[ dimension ]
		self.amethysts = [ amethyst ]
		
		nextDimension = self.nextDimension()
		self.highSide = TwoDEmptyTree( nextDimension )
		self.lowSide = TwoDEmptyTree( nextDimension )
	
	
	
	
	# Insert a new amethyst into a non-empty 2D tree, returning the resulting tree.
	
	def insert( self, amethyst ) :
		
		
		# Insert the amethyst into either the high subtree, the low subtree, or this node,
		# according to whether the amethyst's position is higher, lower, or equal to this
		# node's "mid" value in the appropriate dimension.
		
		amethystCoordinate = amethyst.getPosition()[ self.dimension ]
		
		if amethystCoordinate > self.mid :
			self.highSide = self.highSide.insert( amethyst )
		elif amethystCoordinate < self.mid :
			self.lowSide = self.lowSide.insert( amethyst )
		else :
			self.amethysts.append( amethyst )
		
		return self
	
	
	
	
	# Map a function over all the amethysts in this tree. The function needs to produce
	# whatever results it has via side effects, this method doesn't collect results or
	# return anything. This method also doesn't guarantee that the function will be
	# applied to amethysts within the tree in any particular order.
	
	def traverse( self, f ) :
		
		
		# Apply the function to all of this tree's amethysts, then to any amethysts in
		# each subtree.
		
		map( f, self.amethysts )
		
		self.highSide.traverse( f )
		self.lowSide.traverse( f )
	
	
	
	
	# Find the amethyst, if any, whose center is closest to the apex of a given open
	# triangle (and inside that triangle). Return that amethyst and its t value (a very
	# abstract version of the "time" at which the growing triangle first encloses the
	# amethyst; about all clients can count is that smaller ts correspond to amethysts
	# closer to the triangle's apex). If there is no such amethyst within this tree,
	# return an amethyst and t value provided by the client (which might be the results
	# of a search in some sibling or cousin of this tree, or might be client-specific
	# default values).
	
	def getNeighbor( self, triangle, clientT, clientAmethyst ) :
		
		# This function would theoretically be faster if it figured out which subtree
		# contained the apex of the triangle and started its search there, only checking
		# this tree's data and the other subtree if it was possible for them to contain a
		# triangle nearer than any found in the first subtree. But the code to do that
		# would be more complicated than the code below that always checks both subtrees,
		# which might outweigh any time saving (although empirical tests show that the
		# "smarter" trees are in fact faster).
		
		
		# A local utility function that figures out a new minimum t and associated
		# amethyst given old values for those things and possible better ones.
		
		def best( minT, minAmethyst, newT, newAmethyst ) :
			if newT < minT :
				return ( newT, newAmethyst )
			else :
				return ( minT, minAmethyst )
		
		
		# Find the closest amethyst stored in the root of this tree, then see if either
		# subtree can better it. Return the smallest t and associated amethyst from this
		# process.
		
		minT = clientT
		minAmethyst = clientAmethyst
	
		for a in self.amethysts :			
			minT, minAmethyst = best( minT, minAmethyst, triangle.amethystT( a ), a )
	
		minAmethyst, minT = self.lowSide.getNeighbor( triangle, minT, minAmethyst )
	
		minAmethyst, minT = self.highSide.getNeighbor( triangle, minT, minAmethyst )
		
		return ( minAmethyst, minT )
