# A class that represents area usage maps as dictionaries (hash tables) that map objects
# to information about the areas they cover and the neighbor objects that overlap those
# areas. See the July 30, 2019 notes for my crystal aggregates project for background on
# why I want such maps. Because of the context in which I designed these maps, they
# nominally map space in the xz coordinate plane, although clients can in fact use them on
# any plane they want.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2019. Created by Doug Baldwin to support a program that models and renders
#     single-layer amethyst aggregates.




class HashAreaMap :
	
	
	
	
	# A record class that stores the rectangle an object covers and the object's set of
	# neighbors. The dictionary in dictionary-based area maps associates each object with
	# one of these records. The fields in these records are...
	#   area - The rectangle the object covers
	#   neighbors - A set of other objects that also overlap that area.
	
	class Info :
		
		def __init__( self, area, neighbors ) :
			self.area = area
			self.neighbors = neighbors
	
	
	
	
	# I represent a dictionary-based area map with just one attribute, namely...
	#   mapping  - The dictionary that maps objects to the regions they cover and their
	#     set of neighbors.
	
	
	
	
	# Initialize a dictionary-based area map with the total area it has to cover.
	
	def __init__( self, minX, maxX, minZ, maxZ ) :
		
		
		# Initialization just requires making the dictionary empty.
		
		self.mapping = {}
	
	
	
	
	# Add a new object to a dictionary-based area map. The object being added should not
	# already be in the map, although this method doesn't check to make sure that's the
	# case. This method modifies the map, but has no explicit return value.
	
	def insert( self, newObject ) :
		
		
		# Run through the dictionary, collecting all the objects that overlap the new one,
		# and updating all their entries with the new object as a neighbor.
		
		newArea = newObject.xzBounds()
		newNeighbors = set()
		
		for (obj,info) in self.mapping.items() :
			
			if newArea.overlaps( info.area ) :
				info.neighbors.add( newObject )
				newNeighbors.add( obj  )
		
		
		# Make an information record for this object and add it to the dictionary.
		
		self.mapping[newObject] = HashAreaMap.Info( newArea, newNeighbors )
	
	
	
	
	# Increase the size of an object in a dictionary-based area map, given the object and
	# its original bounds. The object in question must already be in the map. This method
	# modifies the map, but has no explicit return value.
	
	def grow( self, object, oldMinX, oldMaxX, oldMinZ, oldMaxZ ) :
		
		
		# Update the area associated with this object in the map.
		
		self.mapping[object].area = object.xzBounds()
		
		
		# Run through the dictionary, finding objects (other than this one itself) that
		# overlap this one. Make sure that each is recorded as a neighbor of this one,
		# and that this one is recorded as a neighbor of each. This loop takes advantage
		# of the fact that objects only grow larger but never smaller to not worry about
		# removing neighbors that no longer overlap the expanded object.
		
		for (obj,info) in self.mapping.items() :
			
			if obj != object and info.area.overlaps( self.mapping[object].area ) :
				info.neighbors.add( object )
				self.mapping[object].neighbors.add( obj )
	
	
	
	
	# Return a set of all the objects in a dictonary-based area map that overlap a given
	# object.
	
	def neighbors( self, object ) :
		return self.mapping[object].neighbors
