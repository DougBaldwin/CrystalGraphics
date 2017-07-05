# Nodes in binary space partitioning (BSP) trees, for use in drawing crystals and
# crystal aggregates. BSP trees provide a way to order polygons for quick back-to-front
# rendering, something that is important for realistic translucency. These particular BSP
# nodes store triangles, which is sufficient for crystal rendering, rather than general
# polygons. Although instances of this class represent single nodes rather than whole
# trees, clients can represent whole trees by their roots, and those trees will add nodes
# to themselves as they need to.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from VectorOps import subtract3, cross, dot3, normalize3
from MathUtilities import nearlyEqual, allSatisfy
import SymmetryOps
from SymmetryOps import clipClass, linePlaneIntersection
from pyglet.gl import GLfloat
from array import array




class BSPNode ( object ) :
	
	
	
	
	# A BSP node partitions space with a plane, namely the plane containing one or more
	# of a BSP tree's triangles. The node contains a specification for its plane, based
	# on the implicit plane equation ax + by + cz = d, a list of triangles that lie in
	# that plane, and two children, being the roots of BSP trees for the space on the
	# normal side of the plane and the space on the anti-normal side. The following
	# attributes store these things:
	#   normal - The normal to the plane, i.e., the vector <a,b,c>, represented as a
	#     3-element list.
	#   d - The d constant from the plane's implicit equation, ax + by + cz = d.
	#   triangles - The triangles that lie in this plane, represented as a flat array of
	#     vertex data. Each vertex consists of 12 floating point numbers, namely the X, Y,
	#     and Z components of its position, the X, Y, and Z components of its normal, its
	#     coefficients of red, green, and blue diffuse reflection, its alpha (opacity)
	#     value, its coefficient of specular reflection, and its specular shininess. 3
	#     consecutive vertices define a triangle, and this array is as long as it needs
	#     to be to contain all the triangles in the plane.
	#   front - The root of the BSP tree for things in front of, i.e., on the normal side
	#     of, this node's plane. May be None if there are no triangles in front of this
	#     plane.
	#   back - The root of the BSP tree for things in back of, i.e., on the anti-normal
	#     side of, this node's plane. May be None if there are no triangles behind this
	#     plane.
	
	VERTEX_SIZE = 12						# The number of floats in one vertex in the triangles array
	TRIANGLE_SIZE = 3 * VERTEX_SIZE			# The number of floats in one triangle in the triangles array
	
	
	
	
	# Initialize a BSP tree node with the 3 vertices of its triangle and its color
	# properties. The vertices should be 3-element (or 4 if in homogeneous form) lists,
	# each containing the x, y, and z coordinates of one vertex.
	
	def __init__( self, v1, v2, v3, color ) :
		
		
		# Calculate the parameters for the plane equation. Coefficients a, b, and c are
		# the components of the normal to the plane that contains the triangle, and d is
		# whatever ax + by + cz equals when (x,y,z) is a point in the triangle.
		
		edge1 = subtract3( v3, v2 )
		edge2 = subtract3( v1, v2 )
		self.normal = normalize3( cross( edge1, edge2 ) )
		
		self.d = dot3( self.normal, v1 )
		
		
		# The triangle given in the parameters is the only triangle in this node for now.
		
		self.triangles = array( "f" )
		self.addTriangle( v1, v2, v3, color )
		
		
		# This node has no children yet.
		
		self.front = None
		self.back = None
	
	
	
	
	# Insert a new triangle into the tree rooted at this node. The parameters are the
	# 3 vertices of the triangle and its color properties. The vertices should be 3-
	# element (or 4 if in homogeneous form) lists, each containing the x, y, and z
	# components of one vertex.
	
	def insert( self, v1, v2, v3, color ) :
		
		
		# This function works by classifying the vertices of the triangle relative to this
		# node's plane, i.e., determining whether the vertices are on the plane, in front
		# of it, or behind it. Exactly how to insert the triangle into the tree depends on
		# the resulting set of classifications. The following predicates detect certain
		# important kinds of classification.
		
		def on( classification ) :
			return classification == SymmetryOps.ON
		
		def onOrIn( classification ) :
			return classification == SymmetryOps.ON or classification == SymmetryOps.INSIDE
		
		def onOrOut( classification ) :
			return classification == SymmetryOps.ON or classification == SymmetryOps.OUTSIDE
		
		
		# Start by classifying the vertices.
		
		classes = [ clipClass( v1, self.normal, self.d ),
					clipClass( v2, self.normal, self.d ),
					clipClass( v3, self.normal, self.d ) ]
		
		
		# Insert the triangle, possibly splitting it across this node's plane, according
		# to the vertices' classes. But for now just say how the triangle classified.
		
		if allSatisfy( on, classes ) :
			
			# The triangle lies entirely in this node's plane, so add the triangle to those
			# associated with the node.
			
			self.addTriangle( v1, v2, v3, color )
		
		elif allSatisfy( onOrIn, classes ) :
			
			# All vertices are either on or behind this node's plane, so the whole triangle
			# goes behind the node.
			
			self.insertInBack( v1, v2, v3, color )
		
		elif allSatisfy( onOrOut, classes ) :
			
			# All vertices are on or in front of this node's plane, so the whole triangle
			# goes in front of this node.
			
			self.insertInFront( v1, v2, v3, color )
		
		elif    ( classes[0] == SymmetryOps.ON and classes[1] == SymmetryOps.INSIDE and classes[2] == SymmetryOps.OUTSIDE ) \
			 or ( classes[0] == SymmetryOps.ON and classes[1] == SymmetryOps.OUTSIDE and classes[2] == SymmetryOps.INSIDE ) :

			# This node's plane splits the triangle along a line through vertex 1.
			
			self.insertSplit2( v1, v2, v3, classes[1], color )
		
		elif    ( classes[0] == SymmetryOps.INSIDE and classes[1] == SymmetryOps.ON and classes[2] == SymmetryOps.OUTSIDE ) \
			 or ( classes[0] == SymmetryOps.OUTSIDE and classes[1] == SymmetryOps.ON and classes[2] == SymmetryOps.INSIDE ) :
			
			# This node's plane splits the triangle through vertex 2.
			
			self.insertSplit2( v2, v3, v1, classes[2], color )
		
		elif    ( classes[0] == SymmetryOps.INSIDE and classes[1] == SymmetryOps.INSIDE and classes[2] == SymmetryOps.OUTSIDE )  \
 			 or ( classes[0] == SymmetryOps.OUTSIDE and classes[1] == SymmetryOps.OUTSIDE and classes[2] == SymmetryOps.INSIDE ) :
			
			# This node's plane splits the triangle along a line between the v3-v1 and
			# v3-v2 edges.
			
			self.insertSplit3( v3, v1, v2, classes[2], color )
		
		elif    ( classes[0] == SymmetryOps.INSIDE and classes[1] == SymmetryOps.OUTSIDE and classes[2] == SymmetryOps.ON ) \
			 or ( classes[0] == SymmetryOps.OUTSIDE and classes[1] == SymmetryOps.INSIDE and classes[2] == SymmetryOps.ON ) :
			
			# This node's plane splits the triangle through vertex 3.
			
			self.insertSplit2( v3, v1, v2, classes[0], color )
		
		elif    ( classes[0] == SymmetryOps.INSIDE and classes[1] == SymmetryOps.OUTSIDE and classes[2] == SymmetryOps.INSIDE )  \
			 or ( classes[0] == SymmetryOps.OUTSIDE and classes[1] == SymmetryOps.INSIDE and classes[2] == SymmetryOps.OUTSIDE ) :
			
			# This node's plane splits the triangle through the v2-v1 and v2-v3 edges.
			
			self.insertSplit3( v2, v3, v1, classes[1], color )
		
		elif    ( classes[0] == SymmetryOps.INSIDE and classes[1] == SymmetryOps.OUTSIDE and classes[2] == SymmetryOps.OUTSIDE ) \
			 or ( classes[0] == SymmetryOps.OUTSIDE and classes[1] == SymmetryOps.INSIDE and classes[2] == SymmetryOps.INSIDE )  :

			# This node's plane splits the triangle along a line between the v1-v2 and
			# v1-v3 edges.
			
			self.insertSplit3( v1, v2, v3, classes[0], color )
		
		else :
			print "BSPNode.insert has impossible class combination", class1, ",", class2, ",", class3
	
	
	
	
	# Add a triangle to this node's list of triangles. The triangle is defined by its
	# vertices and color. Each vertex is a 3-element list (x, y, z, in that order) and
	# the color is a tuple containing red, green, and blue coefficients of diffuse
	# reflection, alpha, coefficient of specular reflection, and specular shininess. This
	# method modifies this node, but has no explicit return value.
	
	def addTriangle( self, v1, v2, v3, color ) :
		
		self.triangles.fromlist(   v1[0:3] + self.normal + list(color)
								 + v2[0:3] + self.normal + list(color)
								 + v3[0:3] + self.normal + list(color) )
	
		
		 
	
	# Return the number of triangles in the tree rooted at this node.
	
	def size( self ) :
		
		return   len( self.triangles ) / BSPNode.TRIANGLE_SIZE		\
			   + ( 0 if self.front is None else self.front.size() ) \
			   + ( 0 if self.back is None else self.back.size() )
	
	
	
	
	# Dump the vertices of the triangles in the BSP tree rooted at this node into a buffer,
	# specifically a buffer of vertex data for an OpenGL shader program. Order the vertices
	# within the buffer according to how far their triangles are from the viewer, farther
	# triangles being earlier in the buffer than closer ones. The viewer's position
	# along with the BSP tree dictates how to achieve this order. This method modifies the
	# contents of the buffer, but has no explicit return value. Clients must provide a
	# buffer big enough to hold all the vertices in the tree.
	
	def dump( self, buffer, eyePosition ) :
		
		
		# The actual work is done by a helper method that takes an additional argument
		# indicating where in the buffer to start dumping. Start at index 0.
		
		self.dumpToIndex( buffer, eyePosition, 0 )
	
	
	
	
	# Two helper methods for dumping the vertices in a BSP tree into an OpenGL buffer.
	
	# Dump vertex information starting at the given index in the buffer. Return the
	# index of the first buffer element not used.
	
	def dumpToIndex( self, buffer, eyePosition, i ) :
		
		
		# Dump a subtree to the buffer, but only if that subtree isn't empty. Return the
		# index of the next unused entry in the buffer.
		
		def dumpHalfspace( root, buffer, eyePosition, i ) :
			if root is not None :
				return root.dumpToIndex( buffer, eyePosition, i )
			else :
				return i
				
		
		# The dot product of the eye position with the plane's normal indicates which half
		# of space the viewer is in, and thus what order to draw the halves in.
		
		product = dot3( self.normal, eyePosition )
		
		
		# Specifically, the viewer is in the front halfspace if the dot product is greater
		# than this node's d value, the back halfspace if the product is less than d, and
		# on the plane if the product equals d. In the first two cases, draw things on the
		# opposite side from the viewer first, then draw things in the plane, and finally
		# draw things on the same side as the viewer. If the viewer is exactly on the
		# plane, draw things on both sides first, without concern for the order, and
		# finish by drawing things in the plane (which probably won't be visible because
		# they're being viewed edge-on).
		
		if nearlyEqual( product, self.d ) :
			
			return self.dumpTriangles( buffer,
						dumpHalfspace( self.back, buffer, eyePosition,
							dumpHalfspace( self.front, buffer, eyePosition, i ) ) )
		
		elif product > self.d :
		
			return dumpHalfspace( self.front, buffer, eyePosition,
						self.dumpTriangles( buffer,
							dumpHalfspace( self.back, buffer, eyePosition, i ) ) )
		
		else :
		
			return dumpHalfspace( self.back, buffer, eyePosition,
						self.dumpTriangles( buffer,
							dumpHalfspace( self.front, buffer, eyePosition, i ) ) )




	# Dump vertex information from this node's triangles into a buffer, starting at a
	# given index. Return the index of the first element of the buffer after the part
	# used.
	
	def dumpTriangles( self, buffer, i ) :
		
		for datum in self.triangles :
			buffer[i] = GLfloat( datum )
			i += 1
		
		return i
	
	
	

	# 3 helper methods for inserting triangles into BSP trees.
	
	# Insert a triangle, defined by its 3 vertices and color, in front of this node.
	# This expects vertices in some counterclockwise order as seen from "outside" the
	# triangle. It modifies the BSP tree rooted at this node, but has no explicit return
	# value.
	
	def insertInFront( self, v1, v2, v3, color ) :
		
		if self.front is not None :
			self.front.insert( v1, v2, v3, color )
		else :
			self.front = BSPNode( v1, v2, v3, color )
	
	
	
	
	# Insert a triangle, defined by its 3 vertices and color, in back of this node.
	# Vertices should be in some counterclockwise order as seen from "outside" the
	# triangle. This modifies the tree rooted at this node, but has no explicit return
	# value.
	
	def insertInBack( self, v1, v2, v3, color ) :
		
		if self.back is not None :
			self.back.insert( v1, v2, v3, color )
		else :
			self.back = BSPNode( v1, v2, v3, color )



	
	# Split a triangle into two halves through one of its vertices and insert both pieces
	# into the tree rooted at this node. The main arguments to this method are the 3
	# vertices, given in counterclockwise order starting with the one through which to
	# split the triangle. This method also takes the classification relative to this
	# node's plane of the first vertex after the splitting one, to help determine which
	# new triangle goes in front of the node and which goes behind it. Finally, this
	# method also takes the triangle's color as its last argument.
	
	def insertSplit2( self, splittingVertex, vertex1, vertex2, class1, color ) :
		
		try :
		
			# Find the point where the line between the inside and outside vertices intersects
			# this node's plane.
		
			newVertex = linePlaneIntersection( vertex1, vertex2, self.normal, self.d )
		
		
			# Insert a triangle defined by the splitting vertex, the intersection point, and
			# one of vertices 1 or 2 in front of this node, and the triangle defined using the
			# other of vertices 1 or 2 in back. Which triangle goes where depends on vertex
			# 1's classification.
		
			if class1 == SymmetryOps.INSIDE :
			
				# Vertex 1 is in back of this node.
			
				self.insertInBack( splittingVertex, vertex1, newVertex, color )
				self.insertInFront( splittingVertex, newVertex, vertex2, color )
		
			else :
			
				# Vertex 1 is in front of this node
			
				self.insertInFront( splittingVertex, vertex1, newVertex, color )
				self.insertInBack( splittingVertex, newVertex, vertex2, color )
		
		except ValueError as error :
			
			print "BSPNode.insertSplit2 encountered exception", error



	
	# Split a triangle along a line between two of it edges and insert the resulting
	# sub-triangles into the BSP tree rooted at this node. The main arguments to this
	# method are the vertices of the triangle to be split, starting with the one between
	# the edges that will be split and proceeding counterclockwise as seen from "outside"
	# the triangle. The other arguments are the classification of that shared vertex
	# relative to this node's plane, and the triangle's color. This method modifies the
	# tree rooted at this node, but has no explicit return value.
	
	def insertSplit3( self, sharedVertex, vertex1, vertex2, sharedClass, color ) :
		
		try :		
		
			# Find the points where this node's plane intersects the split edges.
		
			newVertex1 = linePlaneIntersection( sharedVertex, vertex1, self.normal, self.d )
			newVertex2 = linePlaneIntersection( sharedVertex, vertex2, self.normal, self.d )
			
			
			# Insert one new triangle between the shared vertex and the two new ones, and
			# two new triangles that divide up the now-quadrilateral area between the two
			# new vertices and the original vertices 1 and 2. Which side of this node each
			# of these triangles is on depends on whether the common vertex is in front or
			# in back of it.
			
			if sharedClass == SymmetryOps.INSIDE :
				
				# The common vertex is behind this node's plane.
				
				self.insertInBack( sharedVertex, newVertex1, newVertex2, color )
				self.insertInFront( newVertex1, vertex1, newVertex2, color )
				self.insertInFront( vertex1, vertex2, newVertex2, color )
			
			else :
				
				# The common vertex is in front of this node's plane.
				
				self.insertInFront( sharedVertex, newVertex1, newVertex2, color )
				self.insertInBack( newVertex1, vertex1, newVertex2, color )
				self.insertInBack( vertex1, vertex2, newVertex2, color )
		
		except ValueError as error :
			
			print "BSPNode.insertSplit3 encountered exception", error
