# A class that represents edges of polyhedra in my project to draw realistic
# amethyst aggregates as sets of clipped polyhedra with sizes taken from an
# appropriate probability distribution. Edges are hierarchical, in that an edge
# that is split in order to split a polyhedron is actually represented by a
# splitting point and two shorter edges, one on each side of the split. See my
# project notes for more about this class and project.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International
# License (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin, based on an earlier non-hierarchical
#     version
#
#   June 2021. Non-hierarchical edges created by Doug Baldwin.




from EdgeDictionary import EdgeDictionary
from GeometryUtilities import safeWrite
from VectorOps import cross, length3
from math import isclose




class Edge :




	# I keep track of all edges ever created in order to see if attempts to
	# join 2 edges during polyhedron or polygon splitting can be satisfied by
	# something that already exists, rather than needing a new edge.

	allEdges = EdgeDictionary()




	# All edges are line segments, and so have points at which they start and
	# end. I make no specific distinction between "starting" and "ending" for
	# these points. Edges may also be split into shorter sub-edges, arbitrarily
	# called a "front" sub-edge and a "back" one. I keep track of all of this
	# with the following attributes:
	#   - end1, end2. Vertex objects that represent the endpoints of this edge.
	#   - front. The front sub-edge, or None if this edge isn't split.
	#   - back. The back sub-edge or None.
	#   - splitterVertex. The vertex at which the front and back sub-edges
	#     meet, or None if this edge isn't split into sub-edges.

	
	
	
	# Initialize an unsplit edge, possibly as a part of some other edge.
	
	def __init__( self, vertex1, vertex2 ) :

		# For debugging, check to see if the new edge duplicates an edge that
		# already exists.
		if Edge.allEdges.find2( vertex1, vertex2 ) :
			raise RuntimeError( "Creating edge that already exists." )

		# Also see if the edge is too short to be worth representing.
		if length3( [vertex1.x - vertex2.x, vertex1.y - vertex2.y, vertex1.z - vertex2.z] ) < 0.00005 :
			raise RuntimeError( "Creating ultra short edge" )


		# The new edge is unique, so finish initializing it.

		self.end1 = vertex1
		self.end2 = vertex2

		self.front = None
		self.back = None
		self.splitterVertex = None

		Edge.allEdges.insert( self )




	# Split this edge with a plane. Return 3 pieces of information, namely the
	# part of the edge in front of the plane (i.e., on the side the normal
	# points to), the part of the edge in back of the plane, and a vertex at
	# which the edge intersects the plane. Any of these things can be None if
	# the plane doesn't intersect the edge, intersects at exactly at one end,
	# or if the edge lies entirely in the plane.

	def split( self, plane ) :


		# I handle edges that have been broken down into smaller sub-edges
		# recursively, whereas edges that aren't broken down get analyzed in
		# detail for their relationship to the plane. But in both cases, I can
		# quickly deal with edges that lie entirely in the plane or entirely on
		# one side of it.

		side1 = plane.whichSide( self.end1 )
		side2 = plane.whichSide( self.end2 )

		if side1 < 0 and side2 < 0 :
			# The edge lies entirely in back of then plane.
			return None, self, None

		elif side1 < 0 and side2 == 0 :
			# The edge is in back of the plane, but one end lies in it.
			# Indicate this by returning the edge as the back part of the split
			# and the end in the plane as the splitting vertex.
			return None, self, self.end2

		elif side1 == 0 and side2 < 0 :
			# Another case where the edge is behind the plane but with one end
			# in it.
			return None, self, self.end1

		elif side1 == 0 and side2 == 0 :
			# The edge lies in the plane. Signal this by saying the edge is in
			# front and in back of the plane, but has no splitter vertex.
			return self, self, None

		elif side1 == 0 and side2 > 0 :
			# The edge lies in front of the plane, with one end in it.
			return self, None, self.end1

		elif side1 > 0 and side2 == 0 :
			# Another way for the edge to be in front of the plane with one end
			# in it.
			return self, None, self.end2

		elif side1 > 0 and side2 > 0 :
			# The last easy case, the edge is entirely in front of the plane.
			return self, None, None

		elif self.front is None and self.back is None :

			# Now I have an unsplit edge that needs to actually be intersected
			# with the plane. After intersection, I might have...
			#   - One end in front of the plane and the other in back: the
			#     plane nontrivially splits the edge.
			#   - One end in front and the other in or at least close to the
			#     plane: the edge is really in front of the plane, but return
			#     the end in the plane as a splitting vertex.
			#   - One end in back of the plane and the other in (or close to)
			#     the plane: like the previous case, but the edge is in back of
			#     the plane.
			# Note that split points that are close to and end of the edge are
			# treated as being at the end, to avoid future problems with very
			# small geometry and round-off. At the moment, "close to" an end
			# means less than half of one percent of the edge's length away
			# from the end. Test for each possibility in an order that puts "an
			# end basically in the plane" cases first, since round-off could
			# make them look like other cases too.

			splitterVertex = plane.intersection( self.end1, self.end2 )

			if self.isSmallSplit( splitterVertex, self.end2 ) :
				# The plane intersects the edge ridiculously close to end 2.
				if side1 > 0 :							# Is the other end in front of the plane?
					return self, None, self.end2
				elif side1 < 0 :						# Is the other end behind the plane?
					return None, self, self.end2
				else :									# The other end must be in the plane
					return self, self, None

			elif self.isSmallSplit( splitterVertex, self.end1 ) :
				# The intersection is ridiculously close to end 1.
				if side2 > 0 :							# Is the other end in front of the plane?
					return self, None, self.end1
				elif side2 < 0 :						# Is the other end behind the plane?
					return None, self, self.end1
				else :									# The other end is in the plane
					return self, self, None

			else :

				# The plane non-trivially splits the edge.

				sub1 = Edge( self.end1, splitterVertex )
				sub2 = Edge( self.end2, splitterVertex )
				if side1 > 0 :
					self.front = sub1
					self.back = sub2
				else :
					self.front = sub2
					self.back = sub1

				self.splitterVertex = splitterVertex

				return self.front, self.back, self.splitterVertex


		else :

			# For an edge that has already been split, the plane can do one of
			# 4 things, each with its corresponding result:
			#   1. Split the front part of the edge. Return a new split edge
			#      object, combining the split front part and the unsplit back.
			#      Note that "front" and "back" as labels for the parts of the
			#      original split edge may not correspond to "front" and "back"
			#      relative to this new split.
			#   2. Split the back part. Return a new split edge similar to the
			#      case of splitting the front.
			#   3. Repeat the split that already exists, i.e., pass exactly
			#      through the point where the front and back parts meet.
			#      Return the parts of this edge, possibly switching "front" and
			#      "back" to agree with how the current splitting plane faces.
			#   4. Trivially "split" the edge at one of its endpoints. Return
			#      the entire edge as in front or in back (as appropriate) of
			#      the plane, but with the endpoint as the splitting vertex.
			#
			# To figure out which of these happens, try splitting the front
			# part with the plane. If that produces non-empty front, back, and
			# splitter results, then I'm in the first case above. If the split
			# produced a non-empty front and an empty back, or vice versa, and
			# the splitter was equal to the edge's existing splitter vertex,
			# then the plane repeats the existing split (third case above). If
			# one part of the split was empty and the other not, and the
			# splitter was the end of the front edge opposite the existing
			# splitting vertex, then the plane trivially splits this edge at
			# that end of the front, so I'm in case four above. If none of these
			# things happen, then I recursively split the back and do a similar
			# analysis, possibly detecting cases 2 and 4. If the plane doesn't
			# split the back, then it doesn't split the edge at all, case five.

			if self.front is not None :

				frontFront, frontBack, frontSplitter = self.front.split( plane )
				frontEnd = self.front.oppositeFrom( self.splitterVertex )

				if frontFront is not None and frontBack is not None and frontSplitter is not None :
					# Non-trivial split of front sub-edge. Combine either the
					# front or back from that split with the back of the whole
					# edge to form the return values.
					if frontFront.hasEnd( self.splitterVertex ) :
						return makeSplitEdge( self.back, frontFront, self.splitterVertex ), frontBack, frontSplitter
					else :
						return frontFront, makeSplitEdge( frontBack, self.back, self.splitterVertex ), frontSplitter

				elif frontFront is not None and frontBack is None and frontSplitter is self.splitterVertex :
					# Plane repeats the existing split exactly
					return self.front, self.back, self.splitterVertex

				elif frontFront is None and frontBack is not None and frontSplitter is self.splitterVertex :
					# Plane repeats existing split, but reverses front/back relative to plane
					return self.back, self.front, self.splitterVertex

				elif frontFront is not None and frontBack is None and frontSplitter is frontEnd :
					# Technically a split, but trivial, with the whole edge in front of plane
					return self, None, frontEnd

				elif frontFront is None and frontBack is not None and frontSplitter is frontEnd :
					# Trivial split, whole edge is in back of plane
					return None, self, frontEnd


			# Plane didn't split front sub-edge, or there was no front
			# sub-edge. Try the back.

			if self.back is not None :

				backFront, backBack, backSplitter = self.back.split( plane )
				backEnd = self.back.oppositeFrom( self.splitterVertex )

				if backFront is not None and backBack is not None and backSplitter is not None:
					# Non-trivial split of back sub-edge.
					if backFront.hasEnd( self.splitterVertex ) :
						return makeSplitEdge( self.front, backFront, self.splitterVertex ), backBack, backSplitter
					else :
						return backFront, makeSplitEdge( backBack, self.front, self.splitterVertex ), backSplitter

				elif backFront is not None and backBack is None and backSplitter is backEnd:
					# Trival split, with the whole edge in front of plane
					return self, None, backEnd

				elif backFront is None and backBack is not None and backSplitter is backEnd:
					# Trivial split, whole edge is in back of plane
					return None, self, backEnd


			# The relationship between the edge and plane is completely
			# unforeseen. Report that to the user/developer.

			raise RuntimeError( "Edge.split found unexpected relationship between split edge {} and {}".format(self,plane) )




	# Append this edge to the end of a list of edges, except if this edge and
	# the last one in that list have a common parent, "hoist" both those edges
	# to that parent rather than appending this edge in its own right. When two
	# edges hoist, I repeat the process to see if their parent has a common
	# parent with the 2nd to last edge in the list, and so forth. This method
	# returns the resulting list.

	def hoistInto( self, edgeList ) :


		# Hoisting is only possible at all if the edge list isn't empty.

		if len( edgeList ) > 0 :

			common = self.commonParent( edgeList[-1] )

			if common is not None :

				# There is a common parent. Hoist that parent (which includes
				# this new edge) into everything into the front part of the
				# list.

				return common.hoistInto( edgeList[ : -1 ] )

			else :
				return edgeList + [self]

		else :
			return edgeList + [self]




	# Extend this edge into another, returning the result as a new edge. This
	# edge and the one it's extended with must have a vertex in common. It's
	# the client's responsibility to be sure the edges really are colinear
	# though. The result is a new split edge, with this edge as the front part
	# of the split, the other one as the back, and the shared vertex as the
	# splitting vertex. If this edge and the extension don't share a vertex,
	# this method raises a ValueError exception.

	def extendWith( self, extension ) :


		# Figure out which vertex is the shared one, and therefore what new
		# edge to return, or realize that there's no shared vertex at all.

		if self.hasEnd( extension.end1 ) :
			return makeSplitEdge( self, extension, extension.end1 )

		elif self.hasEnd( extension.end2 ) :
			return makeSplitEdge( self, extension, extension.end2 )

		else :
			raise ValueError( "Edges have no common vertex in Edge.extendWith" )




	# Find a longer edge ("parent") that equals the union of this edge with
	# another. The other edge must share an endpoint with this one, and be
	# parallel to this one, so that their union can be a single contiguous
	# edge. Return the parent if there is one or I can create one, otherwise
	# return None.

	def commonParent( self, other ) :


		# Check that the edges are parallel. If they aren't, there's no way a
		# single edge can be their union. But if they are parallel, the next
		# check (that they share a point) will mean that they're collinear, and
		# so some other edge could be their union.

		if not self.isParallelTo( other ) :
			return None


		# Find the endpoint that the edges share. Return None if there isn't
		# one.

		if other.hasEnd( self.end1 ) :
			sharedEnd = self.end1
		elif other.hasEnd( self.end2 ) :
			sharedEnd = self.end2
		else :
			return None


		# See if the set of known edges has an edge that runs between the ends
		# of the two edges opposite their shared end. Return that edge if so,
		# otherwise (since I now know that the edges are parallel and share an
		# endpoint), create a new edge.

		existingParent = Edge.allEdges.find2( self.oppositeFrom( sharedEnd ), other.oppositeFrom( sharedEnd ) )

		if existingParent :
			return existingParent
		else :
			return self.extendWith( other )




	# Return the vertex at the opposite end of this edge from the given vertex.

	def oppositeFrom( self, v ) :

		if v is self.end1 :
			return self.end2
		else :
			return self.end1




	# Test whether a proposed splitting point for this edge is actually so
	# close to one of the existing ends as to make the split dangerous (i.e.,
	# likely to result in geometry to small to be accurately processed later).
	# Return True if that is the case, and False if not.

	def isSmallSplit( self, splitter, end ) :

		# "Dangerously close" to the end currently means less than half of one
		# percent of the edge's length away from the end.

		return splitter.distance(end) / self.length() < 0.005




	# Return a vector between the ends of this edge, and pointing toward edge
	# "target." That edge should be one that shares an endpoint with this edge.
	# The result is a 4-element list, representing the vector in homogeneous
	# form, compatible with the vector utility functions used in my crystal
	# aggregate programs. This method is helpful when I want a vector along an
	# edge, and want to be sure it points in a particular direction
	# (counterclockwise or clockwise) around a face. For case where direction
	# doesn't matter, see "vectorAlong."

	def vectorTo( self, target ) :


		# The vector is the difference of the endpoint common to this edge and
		# the target minus the other endpoint.

		if self.end2 is target.end1 or self.end2 is target.end2 :
			return [ self.end2.x - self.end1.x, self.end2.y - self.end1.y, self.end2.z - self.end1.z, 0 ]
		else :
			return [ self.end1.x - self.end2.x, self.end1.y - self.end2.y, self.end1.z - self.end2.z, 0 ]




	# Return a vector along an edge. The result is a 4-element list
	# representing the vector in homogeneous form and compatible with the
	# vector utility functions I use in my crystal aggregate programs. This
	# method returns a vector that points in an arbitrary direction along the
	# edge; for control over what direction the vector points, use "vectorTo."

	def vectorAlong( self ) :
		return [ self.end2.x - self.end1.x, self.end2.y - self.end1.y, self.end2.z - self.end1.z, 0.0 ]




	# Return the length of this edge.

	def length( self ) :
		return length3( self.vectorAlong() )




	# Check to see if a given vertex is one of the ends of an edge. Return True
	# if it is and False if not.

	def hasEnd( self, vertex ) :

		return self.end1 is vertex or self.end2 is vertex




	# Check to see if this edge contains a vertex anywhere, returning True if
	# so and False if not

	def containsVertex( self, vertex ) :

		# This edge contains the vertex if that vertex is one of its ends, or
		# if its front or back contains the vertex.

		if self.hasEnd( vertex ) :
			return True
		elif self.front is not None and self.front.containsVertex( vertex ) :
			return True
		elif self.back is not None and self.back.containsVertex( vertex ) :
			return True
		else :
			return False




	# Return a measure of how nearly parallel this edge is to another. The
	# measure is the ratio of the magnitude of the cross product of the vectors
	# along the edges to the product of the vectors' magnitudes. This is the
	# sine of the angle between the edges, and so will be 0 for perfectly
	# parallel edges, and positive for non-parallel edges. As the angle between
	# the edges increases, the measure becomes more positive, although not
	# linearly, until for perpendicular edges it's 1.

	def parallelism( self, other ) :


		myVector = self.vectorAlong()
		otherVector = other.vectorAlong()

		return length3( cross( myVector, otherVector ) ) / ( length3(myVector) * length3(otherVector) )




	# Determine whether this edge is parallel to another, returning True if so
	# and False if not.

	def isParallelTo( self, other ) :

		# Determine whether the edges are parallel by checking to see if the
		# parallelism measure is 0 (to within some round-off tolerance).

		return self.parallelism( other ) <= 1.0e-9




	# Write this edge to a stream, using ID numbers provided by an ID manager
	# to keep track of pieces of geometry that appear in multiple places. See
	# my project notes from August 17, 21, and 22, 2023, for more on why I want
	# to write geometry to streams, some key ideas behind how I do it, and what
	# the output format looks like.

	def write( self, stream, ids ) :

		# Start by identifying this geometry as an edge.
		stream.write( "[Edge " )

		# If the ID manager already has an ID for this edge, use it.
		if ids.contains( self ) :
			stream.write( "{}]\n".format( ids.find(self) ) )

		else :
			# Otherwise, give the edge an ID and write it in full.
			id = ids.next()
			ids.store( self, id )
			stream.write( "{} ".format(id) )

			self.end1.write( stream, ids )
			self.end2.write( stream, ids )

			safeWrite( self.front, stream, ids )
			safeWrite( self.back, stream, ids )
			safeWrite( self.splitterVertex, stream, ids )

			stream.write( "]\n" )




# An alternative way of creating edges, namely ones that are split from the
# start. So this function takes the new edge's front and back parts, and the
# vertex that separates them, and returns an edge made from those parts, with
# endpoints properly sorted out. If such an edge already exists, return it,
# otherwise make a new edge.

def makeSplitEdge( newFront, newBack, newSplitter ) :

	frontEnd = newFront.oppositeFrom( newSplitter )
	backEnd = newBack.oppositeFrom( newSplitter )

	existingEdge = Edge.allEdges.find2( frontEnd, backEnd )

	if existingEdge :
		return existingEdge

	else :
		newEdge = Edge( frontEnd, backEnd )
		newEdge.front = newFront
		newEdge.back = newBack
		newEdge.splitterVertex = newSplitter

		return newEdge




# Given a list of edges that is intended to define a polygon, check to see if
# the first and last edges in that list have a common parent. If so, patch the
# list to use that parent instead of the 2 separate edges. This returns the
# list resulting from any patching, or the original list if no patching was
# needed.

def checkEndParents( edges ) :


	# Start by checking to see if the first and last edge have a common parent.
	# If so, remove the last edge, replace the first with the parent, and
	# iterate the process until I don't find a common parent. Note that this
	# loop and the next one rely on the fact that the edge list represents a
	# closed polygon, and thus has at least 3 non-colinear, and thus not
	# sharing a parent, edges, to ensure that it won't completely empty the
	# list.

	common = edges[0].commonParent( edges[-1] )

	while common is not None :

		edges[0] = common
		edges = edges[ : -1 ]

		common = edges[0].commonParent( edges[-1] )


	# The first edge in the list is now a common parent of the original first
	# element and some suffix of the list. That parent might also have a common
	# parent with the 2nd, 3rd, etc. elements. So carry out a similar check and
	# merge loop going forward in the list.

	common = edges[0].commonParent( edges[1] )

	while common is not None :

		edges[1] = common
		edges = edges[ 1 : ]

		common = edges[0].commonParent( edges[1] )


	# All possible merging has been done, return the resulting list.

	return edges
