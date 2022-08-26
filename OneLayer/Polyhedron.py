# Classes that represent general polyhedra for my attempt to draw realistic
# amethyst aggregates as sets of clipped crystals with sizes taken from a
# realistic probability distribution. I represent a general polyhedron as a
# binary tree of simpler ones. Interior nodes are pairs of polyhedra that meet
# at a common face to create a larger polyhedron, or, equivalently, single
# polyhedra split into two simpler ones by that face. Leaves are convex. The
# visible shapes of both interior nodes and leaves are described by a list of
# the polyhedron's faces.See my design notes for more on this design and the
# crystals project in general.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin, from an original that didn't represent
#     polyhedra as trees.
#
#   June 2021. Original class created by Doug Baldwin.


from Face import Face
from Polygon import Polygon
from Edge import Edge, checkEndParents
from Vertex import Vertex
from EdgeDictionary import EdgeDictionary




# A class that represents unsplit, convex polyhedra.

class Polyhedron :




	# Internally, I represent a polyhedron by the following attributes:
	#   - faces. A list of this polyhedron's faces.
	#   - color. This polyhedron's color.
	#   - front. If this polyhedron is split, the child on the "front" side of
	#     the split. Otherwise None.
	#   - back. If this polyhedron is split, the child on the "back" side of
	#     the split; otherwise None.




	# Initialize an unsplit polyhedron. I define the polyhedron with a list of
	# its vertices, a list of its faces, and its color. Each face is a list of
	# indices to the face's vertices, in some counterclockwise order (so the
	# "list of faces" argument is a list of lists of integers). The faces must
	# describe a convex polyhedron, or be an empty list, in which case this
	# constructor creates an empty polyhedron. Note that the external
	# representation of polyhedra is deliberately very different from the
	# internal one, on the grounds that I want clients to have as simple a view
	# of polyhedra as possible, while the more complicated representation, and
	# particularly its hierarchical nature, is hidden inside this and related
	# classes.

	def __init__( self, vertices, faces, color ):


		# Build the list of faces by stepping through the faces given by the
		# client, creating the polygon implied by each, being careful to reuse
		# edges wherever possible. I follow the order of vertices given by the
		# client, so each face has a positive orientation for its polygon. None
		# of the faces I create are splitter faces.

		self.faces = []
		polyhedronEdges = EdgeDictionary()

		for face in faces :

			prevVertex = vertices[ face[0] ]
			polygonEdges = []

			for i in face[1:] + [face[0]] :

				curVertex = vertices[ i ]
				curEdge = polyhedronEdges.find2( prevVertex, curVertex )

				if curEdge is None:
					curEdge = Edge( prevVertex, curVertex )
					polyhedronEdges.insert( curEdge )

				polygonEdges.append( curEdge )

				prevVertex = curVertex

			faceShape = Polygon( polygonEdges )
			self.faces.append( Face( False, 1, faceShape, color ) )


		# Save this polyhedron's color.

		self.color = color


		# Since this polyhedron isn't split, it has no front or back sub-
		# polyhedra.

		self.front = None
		self.back = None


	
	
	# Determine whether this polyhedron contains a point or not. Return True
	# if so, and False if not.
	
	def contains( self, point ) :


		# If this polyhedron is split, then it contains the point if any of its
		# parts do. An unsplit polyhedron must be convex, and so contains a
		# point if the point is on the "back" side of all the polyhedron's face
		# planes.

		if self.back is not None and self.front is not None :
			return self.back.contains( point ) or self.front.contains( point )

		else :

			pt = Vertex( point[0], point[1], point[2] )

			for f in self.faces :
				if f.plane().whichSide( pt ) > 0 :
					# The point is in front of this face, so polyhedron can't
					# contain it.
					return False

			# The point was on or behind every face; the polyhedron does
			# contain the point.
			return True

	
	
	
	# Clip this polyhedron so that it contains only the parts that are outside
	# of a given other polyhedron. Modify the polyhedron in place.
	
	def clipTo( self, other ):
		
		
		# If the other polyhedron is split, clip this one against one side,
		# then against the other, thus leaving just the parts outside both. Do
		# this in a way that admits the possibility that a "split" polyhedron
		# might have only one real part though.

		if other.front is not None :
			self.clipTo( other.front )

		if other.back is not None :
			self.clipTo( other.back )


		# If the other polyhedron is definitely not split, clip this one
		# against each of its planes.

		if other.front is None and other.back is None :

			self.clipToPlanes( [f.plane() for f in other.faces] )




	# Clip this polyhedron with each plane in a list, keeping those parts that
	# are in front of at least one of the planes. This method changes the
	# polyhedron, but has no explicit return value.

	def clipToPlanes( self, planes ) :


		# Each plane might split this polyhedron (or parts of it from earlier
		# splits) into a part behind the plane and a part in front. Parts in
		# front don't need any more clipping, but parts in back need to be
		# split by further planes. So the general algorithm in this method has
		# a list of polyhedra that still need to be split, and splits each one
		# against the planes one by one. Any polyhedra identified as in front
		# of any plane are discarded from further processing; polyhedra
		# identified as behind a plane are saved for splitting against the next
		# plane. This process continues until either there are no more
		# polyhedra to split, or no more planes to split with. At the end, any
		# polyhedra that still need splitting are in back of all the planes,
		# and so are made empty to indicate that they have clipped completely
		# away.

		toSplit = [ self ]

		while len( planes ) > 0 and len( toSplit ) > 0 :

			nextToSplit = []
			currentPlane = planes.pop()

			for p in toSplit :
				frontPolyhedra, backPolyhedra, splitterPolygons = p.split( currentPlane )
				nextToSplit += backPolyhedra

			toSplit = nextToSplit


		# All the splitting is done, now I have to make anything still waiting
		# to split empty.

		for p in toSplit :
			p.makeEmpty()


		# Finally, remove any empty descendants of this polyhedron from it.
		# Removal amounts to finding places where a polyhedron in the splitting
		# tree has one or more empty descendants and replacing such polyhedra
		# with a descendant -- ideally a non-empty one, but if the replacement
		# is also empty the condition will be detected further up the tree, and
		# fixed if possible. Note that if the root of the tree is empty, it
		# remains that way.

		self.simplify()




	# Split this polyhedron with a plane. This method modifies the polyhedron,
	# and returns 3 lists: one of sub-polyhedra in front of the plane (i.e., on
	# the side its normal points towards), one of sub-polyhedra in back of the
	# plane, and one of polygons that separate those parts. Those polygons can
	# (and already do) form faces of newly split parts with the positively
	# oriented faces belonging to the front polyhedra and negatively oriented
	# ones to back polyhedra.

	def split( self, plane ) :


		# If this polyhedron is unsplit, split each of its faces with the plane
		# and assemble front and back polyhedra, and a splitting polygon, from
		# the results of those splits.

		if self.front is None and self.back is None :

			frontFaces = []
			backFaces = []
			splitterEdges = EdgeDictionary()

			for f in self.faces :

				newFront, newBack, newSplitter = f.split( plane )

				if newFront is not None :
					frontFaces.append( newFront )

				if newBack is not None :
					backFaces.append( newBack )

				if newSplitter is not None :
					splitterEdges.insert( newSplitter )


			# Figure out what the splitting results mean. There are several
			# possibilities, including...
			#   - All the faces from splitting are in front of the plane. The
			#     whole polyhedron is in front of the plane and there was no
			#     split at all.
			#   - All the faces are in back of the plane. Similar to above, but
			#     the polyhedron is in back of the plane.
			#   - Some faces are in front of the plane and some in back. To Do.

			if len(frontFaces) > 0 and len(backFaces) <= 1 :

				# Polyhedron is in front of plane, possibly with 1 face in it.
				return [self], [], []

			elif len(frontFaces) <= 1 and len(backFaces) > 0 :

				# Polyhedron in back of plane, except for maybe 1 face in it.
				return [], [self], []

			else :

				# There was a nontrivial split. Since this polyhedron was
				# originally unsplit, it's convex. That in turn means that
				# splitting it by a plane produces 2 new convex parts. The
				# faces for one of them are all the front faces from the split,
				# plus a separator face; the faces for the other are all the
				# back faces plus the separator (well, technically there are 2
				# separator faces with the same edges but opposite
				# orientations).

				# The first thing I need to do is assemble a polygon for the
				# separator face(s). Do this by listing the splitter edges in
				# any order based on shared vertices.

				polygonEdges = []

				currentEdge = splitterEdges.element()			# Edge to add to polygon edges
				prevEdge = None									# Previous edge, added for debugging
				currentVertex = currentEdge.end1				# The vertex I found the current edge from
				firstEdge = None

				while currentEdge is not firstEdge :

					if prevEdge is currentEdge :
						print( "Polyhedron.split is in an infinite loop" )

					if firstEdge is None:
						firstEdge = currentEdge

					polygonEdges = currentEdge.hoistInto( polygonEdges )

					nextVertex = currentEdge.oppositeFrom( currentVertex )
					prevEdge = currentEdge
					for e in splitterEdges.find1( nextVertex ) :
						if e is not currentEdge :
							currentEdge = e
							currentVertex = nextVertex
							break

				splitterPolygon = Polygon( checkEndParents( polygonEdges ) )


				# Make separator faces for the front and back polyhedra from
				# the polygon. Since faces should be oriented with their
				# normals pointing out of their polyhedron, and since the
				# "front" faces from the split are defined by being on the
				# side of the splitting plane that its normal points towards,
				# the separator face for the front polyhedron is oriented so
				# its normal faces in the opposite direction from the splitting
				# plane's, and the separator for the back polyhedron is
				# oriented oppositely.

				towardFront = plane.normal()
				backOrientation = splitterPolygon.getOrientation( towardFront )

				frontSeparator = Face( True, -backOrientation, splitterPolygon, self.color )
				backSeparator = Face( True, backOrientation, splitterPolygon, self.color )


				# Make the actual split.

				self.front = Polyhedron( [], [], self.color )				# Empty polyhedron with this one's color
				self.back = Polyhedron( [], [], self.color )

				self.front.faces = frontFaces + [ frontSeparator ]
				self.back.faces = backFaces + [ backSeparator ]

				if self.front.isEmpty() or self.back.isEmpty() :
					print( "Polyhedron.split unexpectedly produced an empty part." )

				return [self.front], [self.back], [splitterPolygon]


		else :

			# This polyhedron is split, so split its parts recursively. But do
			# it in a way that can handle a "split" polyhedron in which some
			# part is missing.

			fronts = []
			backs = []
			splitters = []

			if self.front is not None :
				newFronts, newBacks, newSplitters = self.front.split( plane )
				fronts += newFronts
				backs += newBacks
				splitters += newSplitters

			if self.back is not None :
				newFronts, newBacks, newSplitters = self.back.split( plane )
				fronts += newFronts
				backs += newBacks
				splitters += newSplitters

			return fronts, backs, splitters




	# Simplify this polyhedron by removing any empty polyhedra from its
	# splitting tree. Specifically, find places where a polyhedron in the
	# tree has one or more empty descendants and replace such polyhedra
	# with a descendant -- ideally a non-empty one, but if the replacement
	# is also empty the condition will be detected further up the tree, and
	# fixed if possible. But note that if the root of the tree is empty, it
	# stays empty. This method modifies the polyhedron that executes it, but
	# has no explicit return value.

	def simplify( self ) :


		# First, recursively simplify the front and back parts, if any.

		if self.front is not None :
			self.front.simplify()

		if self.back is not None :
			self.back.simplify()


		# Now see if this polyhedron can be replaced with one of its parts. If
		# the back is empty, unconditionally replace with the front, which will
		# make this polyhedron empty if the front also is. If the back isn't
		# empty but the front is, replace this polyhedron with the back.

		if self.front is not None and self.back is not None :

			if self.back.isEmpty() :
				self.setTo( self.front )

			elif self.front.isEmpty() :
				self.setTo( self.back )




	# Change this polyhedron to be equal to a given other one. This works by
	# shallowly copying the data in the other polyhedron into this one. This
	# method changes the polyhedron executing it, but has no explicit return
	# value.

	def setTo( self, other ) :

		self.faces = other.faces
		self.color = other.color
		self.front = other.front
		self.back = other.back




	# Check to see if this polyhedron is empty, returning True if so and False
	# if not. A polyhedron is defined to be empty if it has fewer than 4 faces.

	def isEmpty( self ) :

		return len( self.faces ) < 4




	# Make this polyhedron empty.

	def makeEmpty( self ) :

		self.faces = []




	# Draw this polyhedron to a renderer. In other words, tell the renderer
	# about this polyhedron's triangles; actual display on screen (or
	# elsewhere) will happen later.
	
	def draw( self, renderer ) :
		
		
		# If this polyhedron is unsplit, draw each of its faces. Otherwise draw
		# its front and back parts.

		if self.front is None and self.back is None :

			for f in self.faces :
				f.draw( renderer )

		else :

			# Even though it shouldn't happen, allow for the possibility that
			# only one part of the split polyhedron actually exists.

			if self.front is not None :
				self.front.draw( renderer )

			if self.back is not None :
				self.back.draw( renderer )
