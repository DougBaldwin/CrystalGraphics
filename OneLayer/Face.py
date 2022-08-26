# A class that represents faces of polyhedra in my attempt to generate
# realistic amethyst aggregates as sets of clipped polyhedra, with sizes taken
# from an appropriate probability distribution. Faces are really just wrappers
# with which polyhedra keep track of their polygonal boundaries. In particular,
# a face stores a polygon, and information about its orientation in a
# particular polyhedron, whether it was produced by clipping/splitting another
# polyhedron, and its color. For more information about this class
# and project, see my crystal aggregates project notes.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International
# License (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin, based on a previous simpler version.
#
#   June 2021. Original version created by Doug Baldwin.




from VectorOps import dot3




class Face :




	# Internally, I represent a face via the following attributes:
	#   - polygon, a Polygon object that specifies the shape of this face.
	#   - orientation, the order in which edges of the polygon should be
	#     visited in order to traverse it in a counterclockwise direction as
	#     seen from outside the polyhedron.
	#   - isSplitter, a Boolean value, True if this face is the result of
	#     splitting some polyhedron and False otherwise.
	#   - color, a list or 6-tuple containing coefficients of red, green, and
	#     blue specular reflection, opacity, coefficient of specular
	#     reflection, and shininess.

	
	
	
	# Initialize a face, given information about whether it comes from
	# splitting, its orientation, its polygon, and its color. These arguments
	# encode information about the polygon exactly the way the corresponding
	# attributes do.
	
	def __init__( self, isSplitter, orientation, polygon, color ) :

		# Just save the arguments in the corresponding attributes.

		self.isSplitter = isSplitter
		self.orientation = orientation
		self.polygon = polygon
		self.color = color




	# Split this face with a plane. Return three things, namely a new face in
	# front of the plane (i.e., on the side the normal points to), a new face
	# in back, and the edge that separates those parts. Any of these could also
	# be None, if the plane doesn't really split the face. Note that because
	# faces aren't hierarchical, the face executing this method doesn't change,
	# although its polygon typically does.

	def split( self, plane ) :


		# The main thing to do is to split the face's polygon.

		frontPolygon, backPolygon, splitterEdge = self.polygon.split( plane )


		# Build new faces from each front and back polygon. Those faces take
		# their color and whether they're splitters from this one; the only
		# trick is to get their orientations right. In particular, each should
		# be oriented so that the normals to their planes point in the same
		# direction as the normal to this face's plane.

		direction = self.polygon.getNormal( self.orientation )

		frontFace = Face( self.isSplitter, frontPolygon.getOrientation(direction), frontPolygon, self.color ) if frontPolygon is not None else None
		backFace = Face( self.isSplitter, backPolygon.getOrientation(direction), backPolygon, self.color ) if backPolygon is not None else None

		return frontFace, backFace, splitterEdge




	# Return the plane that this face lies in.

	def plane( self ) :

		# A face's plane is just the plane its polygon lies in, but oriented
		# according to the face's orientation.

		return self.polygon.plane( self.orientation )




	# Draw this face to a renderer. This really just tells the renderer about
	# the triangles composing this face; actual drawing happens whenever the
	# renderer thinks it should.

	def draw( self, renderer ) :


		# Only non-splitting faces have anything to draw, but that's just their
		# polygon, drawn as seen from outside the polyhedron that contains this
		# face, and in the face's color.

		if not self.isSplitter :
			self.polygon.draw( renderer, self.orientation, self.color )
