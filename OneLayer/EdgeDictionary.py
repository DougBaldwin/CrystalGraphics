# A class that represents dictionaries that store edges from a polyhedron, with
# vertices as keys. These dictionaries differ from standard Python dictionaries
# by having the equality test for keys be approximate equality rather than
# exact.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2021. Created by Doug Baldwin.




class EdgeDictionary :
	
	
	
	
	# Internally, I represent an edge dictionary as a list of vertex/edge
	# tuples. I store this list in attribute "entries"
	
	
	
	
	# Initialize an edge dictionary to be empty.
	
	def __init__( self ) :
		
		self.entries = []
	
	
	
	
	# Generate a human-readable string representation of this edge dictionary.
	# That representation focuses on the fact that this is an edge dictionary
	# and its vertex-edge mapping.
	
	def __str__( self ) :
		
		rep = "<EdgeDictionary " + hex( hash(self) ) + " ="
		
		for e in self.entries :
			rep += " " + str( e[0] ) + ": " + str( e[1] )
		
		return rep + ">"
	
	
	
	
	# Add an edge to a dictionary, using a specified vertex as its key. If the
	# edge is already in the dictionary with a key near the given one, raise a
	# "KeyError" exception. Otherwise, this changes the dictionary, but has no
	# explicit return value.
	
	def add( self, vertex, edge ) :
		
		
		# Check that the vertex/edge pair is not already in the dictionary,
		# adding it if not.
		
		i = self.position( vertex )
		
		if i < 0 :
			self.entries.append( ( vertex, edge ) )
		else :
			raise KeyError( "{} duplicates existing key {}".format( vertex, self.entries[i][0] ) )
	
	
	
	
	# Search an edge dictionary for a given vertex, and return the associated
	# edge. If no vertex in the dictionary is near the desired one, raise a
	# "KeyError" exception.
	
	def find( self, vertex ) :
		
		i = self.position( vertex )
		
		if i >= 0 :
			return self.entries[i][1]
		else :
			raise KeyError( "{} not in dictionary".format( vertex ) )
	
	
	
	
	# Return the number of entries in this edge dictionary.
	
	def size( self ) :
		
		return len( self.entries )
	
	
	
	
	# Return a list of all the vertices that appear as keys in this edge
	# dictionary.
	
	def keys( self ) :
		
		return [ pair[0] for pair in self.entries ]
	
	
	
	
	# A helper method that searches for a vertex in this edge dictionary, and
	# returns its position. If no vertex close to the desired one is in the
	# dictionary, this returns -1.
	
	def position( self, vertex ) :
		
		
		# Loop through the dictionary, checking for tuples whose vertex member
		# has x, y, and z values close to those of the desired vertex. Count
		# how many tuples I pass along the way.
		
		p = 0
		
		for pair in self.entries :
			
			if pair[0].isCloseTo( vertex ) :
				return p
			
			else :
				p += 1
		
		
		# I've checked every entry in this dictionary and none matched the
		# vertex I want.
		
		return -1
