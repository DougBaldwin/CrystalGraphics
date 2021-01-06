# A class that represents convex polyhedra that can expand or contract perpendicular to
# their faces. These polyhedra are primarily defined as the volume on the "inner" side
# of every member of a set of planes, although they can also report their vertices to
# clients. They are aware that they might intersect other convex polyhedra, and can
# generate triangle meshes that cover just their exposed surfaces when such intersections
# are taken into account.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin to support a program that works with crystal
#     aggregates.


from Triangle import Triangle
from LinearOps import solve
from Rectangle import Rectangle
from math import inf




class ConvexPolyhedron :
	
	
	
	
	# Convex polyhedra are fundamentally defined by the planes that enclose them, but to
	# support efficient computation with polyhedra, polyhedra also store explicit
	# representations of their faces, which they derive when needed. I call deriving this
	# information "developing" the polyhedron (as in developing a picture on film). The
	# complete list of attributes of convex polyhedra is thus...
	#   planes - The list of planes that enclose this polyhedron.
	#   isDeveloped - A Boolean value that indicates whether the face information is
	#     currently consistent with the list of planes (if True) or might not be (if False).
	#   faces - The list of the polyhedron's faces. This list is only valid if the
	#     polyhedron is developed.
	
	
	
	
	# A record class that I use internally to represent a face of a polyhedron. Each face
	# has the following the attributes
	#   vertices - A list of the vertices of this face, in some counterclockwise order as
	#     seen from outside the face. Each vertex is simply a list of x, y, and z
	#     coordinates.
	#   plane -  The plane this face is embedded in.
	
	class Face :
		
		
		# Initialize a face from its list of vertices and plane.
		
		def __init__( self, vertices, plane ) :
			self.vertices = vertices
			self.plane = plane
	
	
	
	
	
	
	# Initialize a convex polyhedron from a list of the planes that enclose it.
	
	def __init__( self, planes ) :
		
		
		# The given planes become this polyhedron's bounds.
		
		self.planes = planes
		
		
		# This polyhedron hasn't been developed, so give other attributes values
		# consistent with that state.
		
		self.isDeveloped = False
		self.faces = []
	
	
	
	
	# Determine whether a convex polyhedron contains a point, considering points on the
	# polyhedron's surface to be contained in it. The point is represented as a list of x,
	# y, and z coordinates. This method returns True if the polyhedron contains the point
	# and False if it doesn't.
	
	def containsPoint( self, point ) :
		
		
		# The polyhedron contains the point if the point is on or inside every one of the
		# polyhedron's planes.
		
		return all( [ p.pointOnOrInside( point ) for p in self.planes ] )
	
	
	
	
	# Expand a convex polyhedron by "dr" units perpendicular to every unfrozen plane in
	# the polyhedron. This modifies the polyhedron, but has no explicit return value.
	
	def grow( self, dr ) :
		
		for p in self.planes :
			p.grow( dr )
		
		self.isDeveloped = False
	
	
	
	
	# See if a convex polyhedron overlaps any of its neighbors; if overlaps are extensive
	# enough, freeze any planes in this polyedron whose faces are now completely contained
	# in a neighbor. This updates the polyhedron and its planes, but has no explicit
	# return value.
	
	def updateOverlaps( self, neighbors ) :
		
		
		# Go through the faces of the polyhedron (which requires the polyhedron to be
		# developed), checking each to see if all of its vertices are contained within
		# any one of the neighbors. If so, freeze the plane containing that face. But if
		# no neighbor contains all the face's vertices, make sure the corresponding plane
		# is not frozen (sometimes a previously frozen face can be stretched by unfrozen
		# neighbors growing until the frozen face is no longer completely inside a
		# neighbor).
		
		self.develop()
		
		for f in self.faces :
			
			foundContainingNeighbor = False
			
			for n in neighbors :
				if all( [ n.containsPoint(v) for v in f.vertices ] ) :
					foundContainingNeighbor = True
					break
			
			if foundContainingNeighbor :
				f.plane.makeFrozen( True )
			else :
				f.plane.makeFrozen( False )

	

	
	# Generate a list of triangles that cover the surface of this polyhedron, without
	# concern for whether parts of those triangles are overlapped by other polyhedra
	# and thus not on the exposed surface of this one.
	
	def coarseTriangles( self ) :
		
		
		# The basic idea for listing the triangles of this polyhedron is to step through
		# each of its faces, generating a fan of triangles for each. In order to step
		# through the faces, the polyhedron first has to be developed.
		
		triangles = []
		
		self.develop()
		
		for f in self.faces :
			triangles += self.coarseTriangulateFace( f )
		
		return triangles
	
	
	
	
	# Generate a list of triangles that cover only the exposed surface of this polyhedron.
	# More precisely, the triangles found by this function cover the surface of the
	# polyhedron except for those parts inside any of a list of neighbor polyhedra.
	
	def fineTriangles( self, neighbors ) :
		
		
		# For now, mostly use a coarse triangulation, but exclude faces in frozen planes
		# (on the theory that such faces are enclosed in some other object).
		
		self.develop()
		
		triangles = []
				
		for f in self.faces :
			
			if not f.plane.isFrozen() :
				triangles += self.coarseTriangulateFace( f )
		
		return triangles




	# Return a bounding rectangle for this polyhedron in the x and z dimensions.
	
	def xzBounds( self ) :
		
		
		# Make sure this polyhedron has up-to-date face information, then find the largest
		# and smallest x and z values for any vertex in any face.
		
		self.develop()
		
		minX = inf
		maxX = -inf
		minZ = inf
		maxZ = -inf
		
		for f in self.faces :
			for v in f.vertices :
			
				if v[0] < minX :
					minX = v[0]
				
				if v[0] > maxX :
					maxX = v[0]
				
				if v[2] < minZ :
					minZ = v[2]
				
				if v[2] > maxZ :
					maxZ = v[2]
		
		return Rectangle( minX, maxX, minZ, maxZ )
	
	
	
	
	# Ensure that a convex polyhedron is developed, i.e., that all its vertices and faces
	# are calculated from its current planes. This method modifies the polyhedron that
	# runs it, but has no explicit return value.
	
	def develop( self ) :
		
		
		# A utility function that tries to find the vertex at which 3 of a polyhedron's
		# planes intersect. If there is a unique such vertex, this function appends it
		# to a list of vertices and returns the resulting list. Otherwise (which should
		# never be the case in a well-defined polyhedron) this function reports the error
		# and returns the original vertex list. This function receives information about
		# the planes to intersect as a system of linear equations (a list of 3 equations,
		# each containing 4 coefficients for an equation of the form Ax+By+Cz=D, whose
		# supposedly unique solution is the intersection point.
		
		def checkVertex( equations, vertexList ) :
		
			vertex = solve( equations )
			
			if len( vertex ) == 1 :
				return vertexList + [ vertex[0] ]
			else :
				# This should never execute, if it does it means 3 of this ployhedron's
				# planes failed to intersect in a single point.
				print( "Unexpected solution to intersection of planes in ConvexPolyhedron.develop:", vertex )
				print( "\tfrom equations", equations )
				return vertexList
		
		
		
		# Start of the main develop function: if this polyhedron is already developed,
		# there's nothing to do. But otherwise calculate the vertices of each face.
		
		if not self.isDeveloped :
			
			self.faces = []
			
			
			# Each plane gives rise to a face.
			
			for p in self.planes :
				
				currentFace = ConvexPolyhedron.Face( [], p )
				currentEqn = p.coefficients()
				
				
				# The vertices of that face are the points where its plane intersects
				# each pair of consecutive neighbors.
				
				neighbors = p.getNeighbors()
				prevNeighbor = neighbors[0]
				prevEqn = prevNeighbor.coefficients()
				
				for nextNeighbor in neighbors[1:] :
					
					nextEqn = nextNeighbor.coefficients()
					currentFace.vertices = checkVertex( [ currentEqn, prevEqn, nextEqn ], currentFace.vertices )
					prevEqn = nextEqn
				
				
				# I've now enumerated all the vertices except the one where this plane
				# and its last and first vertices intersect.
				
				currentFace.vertices = checkVertex( [ currentEqn, prevEqn, neighbors[0].coefficients() ], currentFace.vertices )
				
				
				# Finished with this face, add it to the polyhedron's list of faces.
				
				self.faces.append( currentFace )
			
			
			# Finished enumerating the vertices of all faces. This polyhedron is now
			# developed.
			
			self.isDeveloped = True




	# A utility method that returns a list of triangles covering a face of a polyhedron,
	# without concern for whether parts of that face are inside other polyhedra.
			
	def coarseTriangulateFace( self, face ) :
		
		triangles = []
		
		apex = face.vertices[0]
		previous = face.vertices[1]
			
		for next in face.vertices[2:] :
			triangles.append(  Triangle( apex, previous, next ) )
			previous = next
		
		return triangles
