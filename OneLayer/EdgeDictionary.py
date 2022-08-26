# A class that represents dictionaries that store edges from a polyhedron, with
# vertices as keys. Each edge in one of these dictionaries appears twice, once
# for each of its ends. Clients can thus search for an edge by either of its
# endpoints, and there is also a search method that takes two endpoints as
# arguments, locating an edge between those points.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin, based on an earlier version with
#     somewhat different functionality.
#
#   July 2021. Original version created by Doug Baldwin.




from PythonUtilities import pickElement




class EdgeDictionary :




	# I represent edge dictionaries as Python dictionaries that map the
	# vertices at the ends of an edge to the edge. Each edge in an edge
	# dictionary will thus appear twice in this Python dictionary, once for
	# each of its ends. The Python dictionary is attribute "edges".

	
	
	
	# Initialize an edge dictionary to be empty.
	
	def __init__( self ) :
		
		self.edges = {}




	# Search a dictionary for an edge between 2 given vertices. If there are
	# multiple such edges, return any one of them; if there are none, return
	# None.

	def find2( self, vertex1, vertex2 ) :


		# If both vertices are in the dictionary, and the intersection of their
		# edge sets isn't empty, return an arbitrary element of that
		# intersection (by returing the first thing an iterator over the
		# intersection would return). Otherwise, return None.

		try :
			edges = self.edges[vertex1] & self.edges[vertex2]
			return next( iter(edges), None )

		except KeyError :
			return None




	# Search this dictionary for all edges incident on a given vertex,
	# returning a list of those edges. If there's no entry for the vertex at
	# all, return an empty list.

	def find1( self, vertex ) :

		try :
			return list( self.edges[vertex] )

		except KeyError :
			return []




	# Insert an edge into a dictionary. This modifies the dictionary, but has
	# no explicit return value.

	def insert( self, newEdge ) :


		# Insert the new edge into the Python dictionary at each of its ends.

		self.insertAtPoint( newEdge, newEdge.end1 )
		self.insertAtPoint( newEdge, newEdge.end2 )




	# Pick an arbitrary edge out of this dictionary and return it. If the
	# dictionary is empty, return None.

	def element( self ) :


		# Pull any value out of the vertices-to-edges map. That value will be a
		# set of edges, so pull any value out of it to return.

		try :
			edges = pickElement( self.edges.values() )
			return pickElement( edges )

		except StopIteration :
			return None




	# Test to see if this edge dictionary is empty, returning True if so and
	# False otherwise.

	def isEmpty( self ) :


		# For now, assume the dictionary is empty.

		print( "EdgeDictionary.isEmpty assuming {} is empty".format( self ) )
		return True




	# A utility method that inserts an edge into this edge dictionary's Python
	# dictionary at a specific point. This method modifies the edge dictionary,
	# but has no explicit return value.

	def insertAtPoint( self, edge, point ) :


		# If the Python dictionary has an entry for this point, then that entry
		# should be a list. Append this edge to that list. Otherwise create a
		# list containing just this edge and insert it into the Python
		# dictionary.

		try :
			self.edges[ point ] |= { edge }
		except KeyError :
			self.edges[ point ] = { edge }
