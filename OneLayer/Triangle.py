# A record class that represents triangles as used to render surfaces of 3D objects.
# This class focuses on the geometry of triangles, so its main job is to store 3 vertices.
# Vertices are represented as lists, giving the coordinates of the vertex in space in
# either standard or homogeneous form. Vertices are named "v1," "v2," and "v3," and
# are given in counterclockwise order as seen from the "outer" side of the triangle
# ("outer" nominally being the outside of some solid the triangle is part of, but really
# meaning whatever clients want).

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin to support a program that models and renders
#	  crystal aggregates.




class Triangle :
	
	
	
	
	# Being record classes, triangles' attributes are meant for public access. They are...
	#   v1, v2, v3 - The triangle's vertices, in counterclockwise order as seen from
	#     outside the triangle. Each vertex is a 3- or 4-element list, giving the
	#     coordinates of a point in either regular or homogeneous form.
	
	
	
	
	# Initialize a triangle with its vertices.
	
	def __init__( self, v1, v2, v3 ) :
		
		self.v1 = v1
		self.v2 = v2
		self.v3 = v3
