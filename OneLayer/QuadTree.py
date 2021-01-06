# A class that represents quadtrees for keeping track of associations between regions in a
# rectangle and objects that occupy those regions. These trees divide a bounded rectangle
# into 4 smaller rectangular "quadrants," which may be of different sizes from each other,
# with each rectangle being fully or partially covered by zero or more objects. The leaves
# of the tree are rectangles that are fully covered by their associated set of objects.
# Because graphics programs think of the horizontal plane as being the xz plane, quadtrees
# describe positions in their rectangles in terms of x and z coordinates, although clients
# can actually think of the rectangles lying in any plane.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin to support a program that builds single-layer
#     crystal aggregates and needs to keep track of which crystals cover which portions
#     of a rectangular substrate.
#
#   July 2019. Replaced in the crystal aggregate program because quadtrees can have
#     exponentially growing insertion times in that application. The role quadtrees played
#     in it was reconceptualized at this time in terms of an abstract "AreaMap" type,
#     which quadtrees could be an implementation of, although this file doesn't quite
#     provide the right interface to do that at present.




class QuadTree :
	
	
	
	
	# Quadtrees store information in the following attributes:
	#   minX, maxX, minZ, maxZ - The bounds of the rectangle that this tree covers in the
	#     x and z dimensions.
	#   objects - A set of objects that cover all of the rectangle described by this tree
	#     or one of its descendants (i.e., cover all of this tree if it's just a leaf, or
	#     at least part of it if it's not a leaf).
	#   subtrees - A list of 4 quadtrees that cover the quadrants, if any, into which this
	#     tree is divided. If this tree isn't divided, i.e., it represents a leaf, then
	#     this list is empty, otherwise it contains exactly 4 members, which are the
	#     low-x/low-z, high-x/low-z, low-x/high-z, and high-x/high-z subtrees, in that
	#     order. Whether this list is empty vs length 4 is the feature that distinguishes
	#     leaves of a quadtree from internal nodes.
	#   splitX, splitZ - the x and z coordinates at which this tree, if it has children,
	#     splits into quadrants. If this tree has no children, these attributes are
	#     undefined and may not exist at all.
	
	
	
	
	# Initialize a quadtree with the lower and upper bounds for the rectangle it covers,
	# and a set of objects that fill that rectangle (since the new quadtree is a leaf,
	# these object must each fill the entire rectangle). The set of objects can be
	# omitted, in which case it defaults to an empty set -- typical use cases are that
	# client code outside the QuadTree class shouldn't need to worry about the requirement
	# that objects completely fill leaves, or that when they create a quadtree it's a
	# leaf, etc., and so won't mention any objects. Algorithms inside the QuadTree class,
	# on the other hand, can know these things, and find it easier to grow quadtrees if
	# they can specify the initial contents of new leaves.
	
	def __init__( self, minX, maxX, minZ, maxZ, objects = set() ) :
		
		
		# Initialize the bounds of this tree's rectangle from the parameters. Everything
		# else is empty to begin with.
		
		self.minX = minX
		self.maxX = maxX
		self.minZ = minZ
		self.maxZ = maxZ
		
		self.objects = objects
		
		self.subtrees = []
	
	
	
	
	# Insert an object into a quadtree. The arguments to this method are the object to
	# insert and the lower and upper bounds on its bounding rectangle in the xz plane.
	# This method modifies the quadtree, but has no explicit return value.
	
	def insert( self, object, minX, maxX, minZ, maxZ ) :
		
		
		# A utility function that calculates where to split a quadtree node in order to
		# make the split point as near the center as possible. This function does the
		# calculation for one dimension, given the quadtree's bounds in that dimension and
		# the bounds of the object forcing the split. This will pick a split point on one
		# side of the object, but as close to the center of the original quadtree as
		# possible. This function returns 2 results, one being the coordinate value to
		# split at, and the other being an index that indicates whether the object lies
		# above (index = 1) or below (index = 0) the splitting point.
		
		def split( treeMinX, treeMaxX, objMinX, objMaxX ) :
					
			midX = ( treeMinX + treeMaxX ) / 2.0
					
			if abs( objMinX - midX ) < abs( midX - objMaxX ) :
				return objMinX, 1
			else :
				return objMaxX, 0
				
				
		
		
		# Insertion starts by making sure the object's bounds overlap the bounds of this
		# tree. There's nothing to do if they don't.
		
		if  self.overlaps( minX, maxX, minZ, maxZ ) :
		
		
			# If this tree has children, add the object to any of those children that it
			# overlaps.
		
			if len( self.subtrees ) > 0 :
				
				for child in self.subtrees :
					child.insert( object, minX, maxX, minZ, maxZ )
						
	
			elif minX > self.minX or maxX < self.maxX or minZ > self.minZ or maxZ < self.maxZ :
			
				# This tree is a leaf. Furthermore, the new object does not completely
				# fill it. So split this node at whichever corner of the new object is
				# closest to the node's center, turning this tree into an internal
				# node with new leaves as its children. Insert the new object into
				# whichever child it overlaps -- since the split is at one corner of
				# the object, there will only be one overlapped child. I keep track of
				# which it is via indices that tell me whether the object lies on the
				# low (index = 0) or high (index = 1) side of the split in each
				# dimension.
				
				self.splitX, xIndex = split( self.minX, self.maxX, minX, maxX )
				self.splitZ, zIndex = split( self.minZ, self.maxZ, minZ, maxZ )
				
				self.subtrees = [ QuadTree( self.minX, self.splitX, self.minZ, self.splitZ, self.objects.copy() ),
								  QuadTree( self.splitX, self.maxX, self.minZ, self.splitZ, self.objects.copy() ),
								  QuadTree( self.minX, self.splitX, self.splitZ, self.maxZ, self.objects.copy() ),
								  QuadTree( self.splitX, self.maxX, self.splitZ, self.maxZ, self.objects.copy() ) ]
				
				self.subtrees[ zIndex * 2 + xIndex ].insert( object, minX, maxX, minZ, maxZ )
			
			
			# Finally, add the new object to this tree's list of objects, since I know
			# that the object overlaps part or all of this tree's rectangle; if the object
			# only overlaps part of the rectangle, then splitting or recursive insertions
			# ensured that it completely fills some descendant.
			
			self.objects.add( object )
	
	
	
	
	# Remove an object from a quadtree. This method modifies the quadtree, but has no
	# explicit return value.
	
	def remove( self, object ) :
		
		
		# There's only work to do if this quadtree contains the object in the first place.
		
		if object in self.objects :
			
			
			# Remove the object from this tree, and any subtrees of this tree that contain
			# it.
		
			self.objects.remove( object )
			
			for s in self.subtrees :
				s.remove( object )
			
			
			# As a result of removing the object from some subtrees, it's now possible
			# that all subtrees contain the same objects as this one and have no subtrees
			# of their own. In that case, the subtrees provide no information about how
			# space is occupied that isn't already present in this tree, so delete the
			# subtrees.
			
			if all( [ ( len(s.subtrees) == 0 and s.objects == self.objects ) for s in self.subtrees ] ) :
				self.subtrees = []
	
	
	
	
	# Update a quadtree to reflect a new size for one of its existing objects. The object
	# in question, and its old and new bounds in the x and z dimensions, are the arguments
	# to this method. This method updates the quadtree, but has no explicit return value.
	
	def resize( self, object, oldMinX, oldMaxX, oldMinZ, oldMaxZ, newMinX, newMaxX, newMinZ, newMaxZ ) :
		
		
		# Resize the object by removing it from the tree and then re-inserting with its
		# new size. In principle it might be more efficient to try to edit those parts of
		# the existing tree that contain the object in order to reflect its new size, but
		# the special cases that could arise, and the potential to create lots of small
		# regions as objects repreatedly grow in small steps, suggest that might be harder
		# and less effective than it seems.
		
		self.remove( object )
		self.insert( object, newMinX, newMaxX, newMinZ, newMaxZ )
	
	
	
	
	# Return a set of all the objects in this quadtree that overlap a given region. The
	# region is a rectangle, specified by its lower and upper bounds in the x and z
	# dimensions.
	
	def occupants( self, minX, maxX, minZ, maxZ ) :
		
		if not self.overlaps( minX, maxX, minZ, maxZ ) :
			
			# No objects from the quadtree overlap the rectangle at all.
			
			return set()
		
		
		elif self.fills( minX, maxX, minZ, maxZ ) :
			
			# The quadtree's region completely fills the region of interest, everything in
			# the tree overlaps that region.
			
			return self.objects
		
		
		elif len( self.subtrees ) == 0 :
			
			# This tree is just a leaf. Leaves are uniformly filled with their objects,
			# and this one partially overlaps the region of interest, so everything in
			# this tree partially overlaps that region.
			
			return self.objects
		
		
		else :
			
			# This is a non-leaf tree with a partial overlap of the region of interest.
			# Get the objects overlapping that region from the subtrees.
			
			objects = set()
			
			for sub in self.subtrees :
				objects |= sub.occupants( minX, maxX, minZ, maxZ )
			
			return objects
	
	
	
	
	# Print a quadtree in a readable way to standard output. This method mainly helps
	# debug quadtree code when it seems a tree isn't evolving as expected. The argument
	# is the subtree nesting depth for this tree, which helps this method indent its
	# output for readability.
	
	def prettyPrint( self, depth ) :
		
		template = " " * 4 * depth + "[{},{}] x [{},{}]: {}"
		print( template.format( self.minX, self.maxX, self.minZ, self.maxZ, self.objects ) )
		
		for s in self.subtrees :
			s.prettyPrint( depth + 1 )
	
	
	
		
	# A utility method that determines whether a quadtree's rectangle overlaps another
	# one. The second rectangle is described by its x and z bounds. This method returns
	# True if the rectangles overlap, and False if they don't.
	
	def overlaps( self, minX, maxX, minZ, maxZ ) :
		
		
		# Rectangles overlap if one starts before the other ends and ends after the other
		# starts, in both dimensions.
		
		return minX <= self.maxX and maxX >= self.minX and minZ <= self.maxZ and maxZ >= self.minZ
	
	
	
	
	# A utility method that determines whether this quadtree's region completely fills a
	# given rectangle. This method returns True if the quadtree fills the rectangle, and
	# False if not. The rectangle is described by its minimum and maximum values in the
	# x and z dimensions.
	
	def fills( self, minX, maxX, minZ, maxZ ) :
		
		
		# The quadtree fills the rectangle if each of the quadtree's bounds is at or
		# outside of the corresponding bound for the rectangle.
		
		return self.minX <= minX and self.maxX >= maxX and self.minZ <= minZ and self.maxZ >= maxZ
