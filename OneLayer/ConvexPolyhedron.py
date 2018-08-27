# This class represents convex polyhedra for a program that models and renders crystals.
# Most crystals are convex polyhedra, or at least made from them, but other things such
# as substrates that crystals grow on may also be. This class is thus a superclass on
# which I base subclasses that represent things more directly related to crystals.

# Copyright (C) 2017 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2017 -- Created by Doug Baldwin.


from VectorOps import dot3
from MathUtilities import nearlyEqual




class ConvexPolyhedron ( object ) :
	
	
	
	
	# Each convex polyhedron is defined by its vertices, its faces, and its color-related
	# material properties. I store these in the following attributes:
	#   o vertices, a set of Vertex objects.
	#   o faces, a list of lists of vertices. Each inner list represents one face of the
	#     polyhedron, giving its vertices in counterclockwise order as seen from outside
	#     the polyhedron.
	#   o color, a list containing color-related properties, namely coefficients of red,
	#     green, and blue diffuse reflection, opacity, coefficient of specular reflection
	#     for all colors, and a shininess exponent. All coefficients of reflection and
	#     opacity are real numbers between 0 and 1, while the shininess exponent is a
	#     real number between 1 and 128.
	
	
	
	
	# Initialize a convex polyhedron, given information about its color (specifically, a
	# list containing its coefficients of red, green, and blue diffuse reflection, its
	# opacity, its coefficient of specular reflection, and a shininess exponent). This
	# method also leaves the polyhedron with no faces or vertices -- they should be defined
	# later via calls to "defineFace."
	
	def __init__( self, color ) :
		
		
		# Save the color information in the appropriate atttribute, and make the faces
		# and vertices empty.
		
		self.color = color
		
		self.faces = []
		self.vertices = set()
	
	
	
	
	# Clip this polyhedron against the plane ax + by + cz = d. The a, b, and c coefficients
	# should be chosen so that the vector (a,b,c), which is normal to the plane, points to
	# the side of the plane from which to remove points of the polyhedron (i.e., the side
	# that is "outside" the clipping region defined by this plane). This method modifies
	# the polyhedron to remove all points on the normal side of the plane, and to add a
	# new face that "caps" any part of the polyhedron clipped away. However, this method
	# does not have any explicit return value.
	
	def clip( self, a, b, c, d ) :
		
		try :								# Exceptions generally mean bugs in this function, so catch them 
		
		
			# Start by going through this polyhedron's faces, building new clipped faces from
			# those that intersect the plane, preserving unchanged those that are entirely on
			# the anti-normal side of the plane, and implicitly discarding those that are
			# entirely on the normal side.
		
			clipFaces = []						# Faces adjacent to cap accumulate here
			clipVertices = set()				# Vertices of the cap accumuate here
			preserveFaces = []					# Faces in the clipped polyhedron but not adjacent to cap
			preserveVertices = set()			# Vertices of clipped polyhedron but not cap
		
			for face in self.faces :
			
			
				# Set up a list of this face's vertices after clipping. That list is empty
				# until I start looking at edges and deciding how they and the vertices at
				# their ends clip. But the nice thing about an empty list is that I know that
				# all the vertices in it so far are preserved vertices, and thus the face
				# itself is preserved (that will change later if I put a clipped vertex into
				# the face).
			
				newFace = []
				preserved = True
			
			
				# Clip each edge, represented by a current vertex and its successor in
				# counterclockwise order. Use the class of the vertices vis a vis the plane
				# to determine what to do with the edge and whether vertices are preserved,
				# clipped, or discarded. Note that within the loop I copy the next vertex
				# and its class to the current vertex and class right before updating the
				# current index in order to avoid doing work twice, but this means I have to
				# initialize the current vertex and class to vertex 0 before entering the loop.
			
				current = face[0]
				currentClass = current.clipClass( a, b, c, d )
			
				for currentV in range( len(face) ) :
			
					nextV = ( currentV + 1 ) % len(face)
					next = face[ nextV ]
					nextClass = next.clipClass( a, b, c, d )
				
					if currentClass == Vertex.INSIDE :
						
						current, preserveVertices = ensureNearEqual( current, preserveVertices )
				
						newFace.append( current )
					
						if nextClass == Vertex.OUTSIDE :
							preserved = False
							newVertex = clipPoint( current, next, a, b, c, d )
							newVertex, clipVertices = ensureNearEqual( newVertex, clipVertices )
							newFace = ensureNearEqualInList( newVertex, newFace )
				
					elif currentClass == Vertex.ON :
					
						# Vertices that lie exactly on the clipping plane will eventually
						# be vertices of the cap polygon, so treat them as clipping
						# vertices (a vertex on the clipping plane could represent a
						# a single vertex or edge on which the polyhedron touches the
						# clipping plane, but in this case there will be no cap face but
						# no harm in calling the vertex a clipping vertex). Whether a
						# vertex on the clipping plane implies that its face is a clipping
						# face depends on whether the next vertex around that face is
						# outside the clipped space or not. If it is outside, the face
						# definitely clips, but if the next vertex is inside then this
						# face doesn't clip, at least not because of this contact, and if
						# the next vertex is still on the clipping plane I don't know yet.
						
						current, clipVertices = ensureNearEqual( current, clipVertices )
						
						if nextClass == Vertex.OUTSIDE :
							preserved = False
						else :
							current, preserveVertices = ensureNearEqual( current, preserveVertices )
							newFace = ensureNearEqualInList( current, newFace )
				
					elif currentClass == Vertex.OUTSIDE :
					
						preserved = False
					
						if nextClass == Vertex.INSIDE :
							newVertex = clipPoint( current, next, a, b, c, d )
							newVertex, clipVertices = ensureNearEqual( newVertex, clipVertices )
							newFace = ensureNearEqualInList( newVertex, newFace )
				
					else :
						print "Impossible clipping class", currentClass
				
					current = next
					currentClass = nextClass
			
			
				# If there's anything in the possibly clipped face at all (there might not
				# be if all its vertices clipped away, or it clipped to a single point),
				# add its description to either the list of preserved faces or the list of
				# clipped ones, according to whether or not all of its vertices are
				# preserved. Note that if the clipped face clipped down to a line I keep
				# it as a clipped face for now, because I'll need it for building the cap
				# face, but remove it later.
			
				if len( newFace ) > 1 :
					if preserved :
						preserveFaces.append( newFace )
					else :
						clipFaces.append( newFace ) 
		
		
			# If any faces were clipped, build the cap face. But there have to be enough cap
			# vertices to at least make a triangle in order to do this.
		
			if len( clipVertices ) > 2 :
			
			
				# Start the cap at the first clip vertex in the cap's first neighbor face.
				# Then put the rest of the clip vertices in counterclockwise order around
				# the cap by finding the current one preceded by another clip vertex in
				# some neighbor, making that predecessor the current vertex, and so forth
				# until I've taken a current clip vertex from each neighbor. In doing this,
				# I rely quite a bit on the fact that with convex faces clipped against a
				# plane, every clipped face will contain exactly 2 clip vertices.
				
				currentCapVertex = filter( lambda elt : elt in clipVertices, clipFaces[0] )[0]
				capFace = []
				
				for i in range( len(clipFaces) ) :
					
					capFace.append( currentCapVertex )
					
					for neighbor in clipFaces :
					
					
						# Check to see if the current cap vertex is in this neighbor, and
						# if so whether the immediately preceding vertex in the neighbor
						# is also a cap vertex. If so, then the corresponding edge is
						# shared with the cap, and so the vertex it starts at becomes the
						# new current cap vertex.
						
						if currentCapVertex in neighbor :
						
							i = neighbor.index( currentCapVertex )
							predecessor = neighbor[ (i-1) % len(neighbor) ]
							
							if predecessor in clipVertices :
								currentCapVertex = predecessor
								break
				
				
				# Treat the cap as another clipped face for purposes of including it in
				# the clipped polyhedron.
				
				clipFaces.append( capFace )
		
		
			# Finally, the clipped polyhedron is the union of the preserved faces, the
			# non-degenerate (i.e., not lines or points) clipped faces, which now include
			# any cap face.
		
			self.faces = preserveFaces + filter( lambda face : len(face) > 2, clipFaces )
		
			self.vertices = preserveVertices | clipVertices
		
		except Exception as error :
			
			print "Probable bug in ConvexPolyhedron.clip:"
			print "\t", error
	
	
	
	
	# Tesselate this polyhedron into a set of triangles and add them to a renderer. This
	# method alters the renderer by adding to the triangles it will draw, but has no
	# explicit return value.
	
	def addToRenderer( self, renderer ) :
		
		
		# Break each face into a fan of triangles, adding each triangle to the renderer.
		
		for face in self.faces :
		
			apex = face[0].toVector()
			
			for v in range( 2, len(face) ) :
				renderer.triangle( face[v].toVector(), apex, face[v-1].toVector(), self.color )
	
	
	
	
	# Define a face of a polyhedron from a list of its vertices, in counterclockwise order
	# as seen from outside the polyhedron. I intend this method to be used by subclasses
	# that know exactly what shape their polyhedron is; there's no reason why other
	# clients would call it. This method modifies the polyhedron on which it is called,
	# but has no explicit return value.
	
	def defineFace( self, vertices ) :
	
	
		# As much as possible, build this face from vertices that are already part of
		# this polyhedron and are nearly equal to vertices requested by the client. To
		# do this, build a list of vertices to use that uses existing vertices where
		# possible, and new ones when necessary.
		
		toUse = []
		for v in vertices :
			v, self.vertices = ensureNearEqual( v, self.vertices )
			toUse.append( v )
		
		
		# Add this face to this polyhedron's list of faces.
		
		self.faces.append( toUse )




# This class represents vertices of polyhedra. Vertices mainly serve as objects that
# collect information about a vertex (e.g., its x, y, and z coordinates) and that can be
# shared by other data structures such as faces of polyhedra. I consider vertices to be
# records, so clients can directly access their x, y, and z components.

class Vertex :
	
	
	
	
	# I represent vertices by their x, y, and z coordinates, in correspondingly named
	# variables.
	
	
	
	
	# Initialize a vertex from its x, y, and z coordinates.
	
	def __init__( self, x, y, z ) :
		
		
		# Initialization just requires copying the x, y, and z values to the corresponding
		# attributes.
		
		self.x = x
		self.y = y
		self.z = z
	
	
	
	
	# Return this vertex as a homogeneous coordinate vector of the sort manipulated by the
	# "VectorOps" module (i.e., a list of components).
	
	def toVector( self ) :
		
		return [ self.x, self.y, self.z, 1 ] 
	
	
	
	
	# Determine whether this vertex is "equivalent" to another. Vertices are equivalent
	# if they represent the same point, up to a small tolerance for round-off. This
	# returns True if the vertices are equivalent, and False if they aren't.
	
	def equivalent( self, other ) :
		
		
		# The vertices represent (almost) the same point if their x, y, and z components
		# are (almost) equal.
		
		return nearlyEqual( self.x, other.x ) and nearlyEqual( self.y, other.y ) and nearlyEqual( self.z, other.z )
	
	
	
	
	# Classify this vertex according to which side of a plane it's on. I describe the
	# plane by the coefficients of its implicit equation, ax + by + cz = d. Possible
	# classifications are -1, meaning that the point is on the side of the plane
	# opposite the normal, 0, meaning that the point is on the plane, or 1, meaning that
	# the point is on the normal side of the plane. I store these constants in variables
	# INSIDE, ON, and OUTSIDE respectively, to make them easier to remember.
	
	INSIDE = -1
	ON = 0
	OUTSIDE = 1
	
	def clipClass( self, a, b, c, d ) :
		
		
		# The vertex is on the normal side if ax + by + cz > d, on the anti-normal side
		# if ax + by + cz < d, and on the plane if ax + by + cz = d. Note that
		# ax + by + cz is the dot product of vectors (a,b,c) and (x,y,z).
		
		dotProd = dot3( [a,b,c], [self.x,self.y,self.z] )
		
		return Vertex.ON if nearlyEqual( dotProd, d ) \
			   else Vertex.INSIDE if dotProd < d \
			   else Vertex.OUTSIDE




# Generate a vertex corresponding to the point at which the line segment between two other
# vertices intersects a plane. The two vertices are given as Vertex objects corresponding
# to the beginning and end of the segment; the plane is defined by the coefficients of its
# implicit equation, ax + by + cz = d. This function returns a new Vertex object containing
# the intersection point, or raises a ValueError if the line is parallel to the plane.
# This function is a utility function that calculates where an edge of a polyhedron clips
# against a plane for the ConvexPolyhedron.clip method.

def clipPoint( start, finish, a, b, c, d ) :
	
	
	# Describe the line between the two vertices parametrically, and solve for the t value
	# at which the line intersects the plane. I have a derivation of this equation in my
	# project notes for June 23, 2017. The first thing I need to evaluate that equation is
	# the change in distance from the plane between the segment's starting point and
	# ending point.
	
	deltaX = finish.x - start.x
	deltaY = finish.y - start.y
	deltaZ = finish.z - start.z

	delta =   a * deltaX + b * deltaY + c * deltaZ
	
	if nearlyEqual( delta, 0 ) :					# Check that line isn't parallel to plane
		raise ValueError( "Intersection between parallel line and plane" )
	
	t = ( d - a * start.x - b * start.y - c * start.z ) / delta
	
	
	# Use the t value to find an actual point where the line segment intersects the plane.
	
	return Vertex( start.x + t * deltaX, start.y + t * deltaY, start.z + t * deltaZ )




# Find the vertices in a set of vertices that are nearly equal, up to possible round-off,
# to a given vertex.

def findNearEquals( vertex, vertexSet ) :

	return filter( lambda v : vertex.equivalent(v), vertexSet )




# Ensure that a set of vertices contains one nearly equal to a given vertex, preferably
# by finding such a vertex already in the set, or by adding the given one to the set if
# need be. This function returns two values, namely the vertex that is nearly equal to the
# given one, and the possibly modified set of vertices.

def ensureNearEqual( newVertex, vertexSet ) :
	
	equivalent = findNearEquals( newVertex, vertexSet )
	
	if len( equivalent ) == 0 :
		vertexSet.add( newVertex )
		return ( newVertex, vertexSet )
	else :
		return ( equivalent[0], vertexSet )




# Ensure that a list of vertices contains one nearly equal to a given vertex. Ideally the
# list already contains such a vertex, but if not this function appends it to the list. In
# both cases, this function returns the list, guaranteed to contain something nearly equal
# to the vertex.

def ensureNearEqualInList( newVertex, vertexList ) :
	
	if noNearEqual( newVertex, vertexList ) :
		vertexList.append( newVertex )
	
	return vertexList




# Decide whether an iterable of vertices lacks a vertex equal, up to possible round-off,
# to a given vertex. Return True if so, or False otherwise. This is basically a utility
# function to help decide whether a vertex that should be in a set or list needs to be
# added to it.

def noNearEqual( newVertex, vertexSet ) :
	
	return len( findNearEquals( newVertex, vertexSet ) ) == 0
