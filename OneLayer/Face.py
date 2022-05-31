# A class that represents faces of convex polyhedra in my attempt to generate
# realistic amethyst aggregates as sets of clipped polyhedra, with sizes taken
# from an appropriate probability distribution. For more information about
# this project, see my crystal aggregates project notes from 2021.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International
# License (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.




from Edge import Edge
from VectorOps import cross, dot3, checkScalarMultiple




class Face :
	
	
	
	
	# I represent faces as the list of their edges, a list of their vertices,
	# and an equation for the plane in which they lie. Key member variables in
	# this representation are...
	#   o edges - The list of this face's edges, in counterlockwise order as
	#		see from outside the polyhedron.
	#   o vertices - The list of this face's vertices, also in counterclockwise
	#		order, starting with the furthest clockwise end of the first edge.
	#   o A, B, C, D - Coefficients of the plane equation Ax + By + Cz = D. I
	#		calculate these coefficients in such as way that vector <A,B,C> is
	#		an outward-pointing normal to the plane.
	
	
	
	
	# Initialize a face, given a list of the edges around it. The list should
	# give the edges in counterclockwise order as seen from outside the
	# polyhedron.
	
	def __init__( self, edges ) :
		
		self.edges = edges
		
		
		# Calculate the coefficients of outward normal <A,B,C>. To do this,
		# find the vertex that's common to the first two edges, then find
		# vectors from that vertex to the other end of each edge. The cross
		# product of the vector for the first edge (the counterclockwise one of
		# the pair) into the vector for the second (the clockwise one) will
		# then be an outward pointing normal. At least for now, I don't care
		# how long this vector is. Notice that while I'm figuring out which
		# vertex is common to the first 2 edges, I can also figure out which
		# vertex to start listing this face's vertices from for the "vertices"
		# member variable.
		
		if edges[0].vertex1 is edges[1].vertex1 :
			ccwVector = vectorFromVertices( edges[0].vertex1, edges[0].vertex2 )
			cwVector = vectorFromVertices( edges[1].vertex1, edges[1].vertex2 )
			startVertex = edges[0].vertex2
			
		elif edges[0].vertex1 is edges[1].vertex2 :
			ccwVector = vectorFromVertices( edges[0].vertex1, edges[0].vertex2 )
			cwVector = vectorFromVertices( edges[1].vertex2, edges[1].vertex1 )
			startVertex = edges[0].vertex2
		
		elif edges[0].vertex2 is edges[1].vertex1 :
			ccwVector = vectorFromVertices( edges[0].vertex2, edges[0].vertex1 )
			cwVector = vectorFromVertices( edges[1].vertex1, edges[1].vertex2 )
			startVertex = edges[0].vertex1
		
		else :
			ccwVector = vectorFromVertices( edges[0].vertex2, edges[0].vertex1 )
			cwVector = vectorFromVertices( edges[1].vertex2, edges[1].vertex1 )
			startVertex = edges[0].vertex1
		
		normal = cross( cwVector, ccwVector )
		
		
		# Store the components of the normal vector as 3 of the coefficients
		# for the plane equation, then plug the coordinates of any vertex into
		# that equation to find D.
		
		self.A = normal[0]
		self.B = normal[1]
		self.C = normal[2]
		
		vertex = edges[0].vertex1
		
		self.D = self.A * vertex.x + self.B * vertex.y + self.C * vertex.z
		
		
		# Build the list of vertices, starting with whichever vertex from the
		# first edge wasn't shared with the second edge.
		
		self.vertices = [ startVertex ]
		
		for e in edges[ : -1 ] :
			nextVertex = e.vertex1 if e.vertex1 is not startVertex else e.vertex2
			self.vertices.append( nextVertex )
			startVertex = nextVertex
	
	
	
	# Produce a human-readable string representation of this face. I make this
	# representation comprehensive, in that it includes the edges, vertices,
	# and normal separately, even though there's a lot of redundancy between
	# them.
	
	def __str__( self ) :
		
		rep = "<Face " + hex( hash(self) ) + " = "
		
		rep += "Edges = "
		for e in self.edges :
			rep += str( e ) + " "
		
		rep += "Vertices = "
		for v in self.vertices :
			rep += str( v ) + " "
		
		numberFormat = "{:.7g}"
		rep += "Normal = <" + numberFormat.format( self.A ) \
							+ ", " + numberFormat.format( self.B ) \
							+ ", " + numberFormat.format( self.C ) + ">>"
		
		return rep
	
	
	
	
	# Draw this face to a renderer, i.e., put all the face's triangles into the
	# renderer. Since faces don't a priori have colors, the client also says
	# what color to draw the face with.
	
	def draw( self, renderer, color ) :
		
		
		# Since this face comes from a convex polyhedron, it is convex itself,
		# and therefore I can draw it as a fan of triangles from any vertex. So
		# use the first saved vertex as the common one for the fan, and step
		# through the other vertices to generate the triangles.
		
		for i in range( 2, len(self.vertices) ) :
		
			renderer.triangle( [ self.vertices[0].x, self.vertices[0].y, self.vertices[0].z ],
							   [ self.vertices[i-1].x, self.vertices[i-1].y, self.vertices[i-1].z ],
							   [ self.vertices[i].x, self.vertices[i].y, self.vertices[i].z ],
							   color )
	
	
	
	
	# Split this face by a plane with equation Ax + By + Cz = D, returning two
	# new faces and an edge that lies in the plane and separates the new faces.
	# The first of the returned faces lies on the outside of the plane (except
	# for the edge that's in the plane), and the second lies inside the plane.
	# The splitting edge is always oriented so that its first vertex is the one
	# at which a counterclockwise walk around the face goes from inside the
	# plane to outside. If the plane doesn't actually split the face, including
	# the case where the face lies in the splitting plane, the appropriate
	# returned face and the separating edge will be None.
	
	def split( self, A, B, C, D ) :


		# See if the face lies in the plane. If so, it's entirely "inside" if
		# its normal points in the same direction as the plane's, and entirely
		# "outside" if not.
		
		coefficient, areMultiples = checkScalarMultiple( [ self.A, self.B, self.C, self.D ],
														 [ A, B, C, D ] )
		
		if areMultiples :
			
			if coefficient > 0.0 :
				return None, self, None
			
			else :
				return self, None, None
			
		
		# The face doesn't lie in the splitting plane. Go through the edges,
		# seeing which if any of them are split by the plane. By keeping track
		# of the edges that are on each side of the plane, and where any split
		# edges are split and whether they go from inside to outside the plane
		# or vice versa on a counterclockwise walk around the face, I can
		# construct the separating edge and new faces after I finish this loop.
		
		outsideEdges = []
		insideEdges = []
		
		inToOut = None
		outToIn = None
		
		for i in range( len(self.edges) ) :
		
			e = self.edges[ i ]
		
			outsideEdge, insideEdge, splitPoint = e.split( A, B, C, D )
			
			if outsideEdge is not None :
				outsideEdges.append( outsideEdge )
			
			if insideEdge is not None :
				insideEdges.append( insideEdge )
			
			if splitPoint is not None :
			
				cwVertex = self.clockwiseEnd( i )
				
				if cwVertex.sideOfPlane( A, B, C, D ) < 0 :
					# This edge goes from the inner side of the plane to the
					# outer as one moves counterclockwise around this face.
					inToOut = splitPoint
				else :
					outToIn = splitPoint
		
		
		# If there are endpoints for a splitting edge, create it.
		
		if inToOut is not None and outToIn is not None :
			
			splittingEdge = Edge( inToOut, outToIn )
			
			insertAfter( splittingEdge, outsideEdges, outToIn )
			insertAfter( splittingEdge, insideEdges, inToOut )
		
		else :
			splittingEdge = None
		
		
		# Build the inside and outside parts of this face, at least if they
		# have enough edges to make faces.
		
		outsideFace = Face( outsideEdges ) if len(outsideEdges) >= 3 else None
		insideFace = Face( insideEdges ) if len(insideEdges) >= 3 else None
		
		
		# All done.
		
		return outsideFace, insideFace, splittingEdge
	
	
	
	
	# Find the clockwise vertex of this face's i-th edge. I define "clockwise"
	# relative to the order the face lists its edges, which should be the order
	# they're encountered in some counterclockwise walk around the face, as
	# seen from outside it.
	
	def clockwiseEnd( self, i ) :
		
		
		# The clockwise end of edge i is the vertex shared with the previous
		# edge.
		
		thisEdge = self.edges[ i ]
		prevEdge = self.edges[ (i-1) % len(self.edges) ]
		
		if thisEdge.vertex1 == prevEdge.vertex1 or thisEdge.vertex1 == prevEdge.vertex2 :
			return thisEdge.vertex1
		else :
			return thisEdge.vertex2
	
	
	
	
	# Test whether a point, represented as a list of its x, y, and z
	# coordinates, is on the "outside" side of this face, returning True if so
	# and False otherwise.
	
	def isPointOutsideFace( self, pt ) :
		
		
		# The point is outside the face if the dot product between face's
		# normal and the vector from the origin to the point is greater than
		# the face's "D" parameter.
		
		return dot3( [self.A, self.B, self.C], pt ) > self.D
	
	
	
	
	# Generate a string containing a next-level-of-detail description of this
	# face, i.e., a description of the face in terms of its edges, vertices,
	# and plane equation, but without any detail inside those things.
	
	def dumpStr( self ) :
		
		return "<{}: {}x + {}y + {}z = {}, Edges = {}, Vertices = {}>".format( self, self.A, self.B, self.C, self.D, self.edges, self.vertices )
	
	
	
	
# A utility function that computes a vector from one vertex of a face to
# another.

def vectorFromVertices( startVertex, endVertex ) :
	
	return [ endVertex.x - startVertex.x,
			 endVertex.y - startVertex.y,
			 endVertex.z - startVertex.z ]




# A utility function that inserts a new edge into a list of edges, after the
# edge that has a given unique ending vertex. This function changes the list,
# but has no explicit return value.

def insertAfter( newEdge, edgeList, endVertex ) :
	
	
	# Find the position after which to insert the new edge.
	
	i = 0
	while edgeList[i].vertex1 is not endVertex and edgeList[i].vertex2 is not endVertex :
		i += 1
	
	
	# Insert the new edge into the list after position i.
	
	edgeList.insert( i+1, newEdge )
