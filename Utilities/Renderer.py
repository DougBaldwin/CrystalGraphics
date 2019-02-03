# Part of a hierarchy of Python classes that render crystals or aggregates to various
# targets. This class is the root of the hierarchy, i.e., all the actual renderers
# are subclasses of it. This class isn't intended to be used directly, but it provides
# features that are necessarily common to all renderer classes, documentation of
# renderers' interface to clients, and dummy implementations of each method that
# subclasses should define. This means that if a method doesn't make sense for a
# particular subclass (e.g., the "viewer" method for a hypothetical subclass that renders
# to a 3D printer), the subclass can safely leave the method undefined and inherit the
# dummy method from this class.
#
# Renderers work extensively with points representing the vertices of crystals, and some
# may also work with vectors representing, e.g., directions. Clients may internally
# represent these points or vectors in homogeneous coordinates, and may pass homogeneous
# coordinates to a renderer. Renderers, however, must accept either homogeneous or
# non-homogeneous coordinates, in order to be interchangeable in clients. To allow this,
# homogeneous coordinates passed to renderers must have a fourth component of either 0 or
# 1, i.e., the fourth component can't be used for scaling. For the sake of
# interchangeability, renderers that need homogeneous coordinates internally must ensure
# for themselves that their points/vectors are in homogeneous form. They can, however,
# test to see if a point/vector argument is already in homogeneous form, creating a
# homogeneous replacement for it if not.

# Copyright 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from VectorOps import subtract3, cross, normalize3




class Renderer :
	
	
	
	
	# Renderers store a model that they will render when someone calls their "draw"
	# method. This model consists of a set of triangles, each defined via a call to the
	# "triangle" method. Internally, renderers store the model as a list of its vertices,
	# describing each vertex by...
	#   - Its x, y, and z coordinates
	#   - The x, y, and z components of a normal to the model at that vertex (angular
	#     models might have several different normals at the same vertex, one for each
	#     face sharing that vertex)
	#   - The red, green, and blue coefficients of specular reflection at that vertex
	#   - The opacity of the model at that vertex
	#   - The coefficient of specular reflection at that vertex
	#   - The specular shininess at that vertex.
	# The following class serves as a simple record that holds these pieces of data for a
	# single vertex.
	
	class Vertex :
	
		# Initialize a vertex from tuples defining its position, normal, and material.
		def __init__( self, position, normal, material ) :
			self.x = position[0]
			self.y = position[1]
			self.z = position[2]
			self.nx = normal[0]
			self.ny = normal[1]
			self.nz = normal[2]
			self.red = material[0]
			self.green = material[1]
			self.blue = material[2]
			self.alpha = material[3]
			self.specular = material[4]
			self.shine = material[5]
	
	
	
	
	# Initialize a renderer.
	
	def __init__( self ) :
	
		self.vertices = []				# Model starts off empty
	
	
	
	# Add a flat triangle to the set of triangles in this renderer's model. Since the
	# triangle is flat (instead of approximating a curved patch) all three vertices
	# have the same normal, which can be calculated from the triangle's edges. Thus
	# the only parameters to this method are the triangle's 3 vertices and its material
	# (which is also constant across the whole triangle). Vertices should be listed in
	# counterclockwise order as seen from outside the triangle.
	
	def triangle( self, v1, v2, v3, material ) :
		
		
		# Calculate the triangle's normal as the cross product of its edges. Since
		# vertices are in counterclockwise order, the outward-pointing normal is
		# (v3-v2) X (v1-v2).
		
		normal = normalize3( cross( subtract3( v3, v2 ), subtract3( v1, v2 ) ) )
		
		
		# Add 3 vertices for this triangle to this renderer's model
		
		self.vertices = self.vertices + [ Renderer.Vertex( v1, normal, material ),
										  Renderer.Vertex( v2, normal, material ),
										  Renderer.Vertex( v3, normal, material ) ]
	
	
	
	
	# Draw the model accumulated in this renderer. Note that for some renderers (e.g.,
	# ones that need to run an event loop to display their image),this method may not
	# return until the program is shutting down.
	
	def draw( self ) :
		pass
	
	
	
	
	# Set the viewer's position. Future drawing renders the model as seen from this
	# position, looking towards the origin.
	
	def viewer( self, x, y, z ) :
		pass
	
	
	
	
	# Generate a string that describes the version of any back-end rendering engine this
	# renderer uses.
	
	def version( self ) :
		return "no rendering engine"
