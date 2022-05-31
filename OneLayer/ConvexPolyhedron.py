# A class that represents convex polyhedra in my effort to draw realistic
# amethyst aggregates as sets of clipped polyhedra with sizes taken from a
# realistic probability distribution. In this program, convex polyhedra are
# the building blocks from which I assemble general polyhedra. See the design
# notes from early 2021 for more.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.


from Face import Face
from EdgeDictionary import EdgeDictionary
from pdb import post_mortem
import sys




class ConvexPolyhedron :
	
	
	
	
	# I use a boundary representation for convex polyhedra, i.e., represent
	# them mainly via lists of faces, edges, and vertices. I store each of
	# these boundaries in a member variable, with another for the polyhedron's
	# color (a hextuple of red, green, and blue coefficients of diffuse
	# reflection, the alpha coefficient, a coefficient of specular reflection,
	# and a specular shininess exponent).
	
	
	
	
	# Initialize a convex polyhedron from its faces, edges, vertices, and
	# color information.
	
	def __init__( self, faces, edges, vertices, color ) :
		
		self.faces = faces
		self.edges = edges
		self.vertices = vertices
		self.color = color
	
	
	
	
	# Determine whether this polyhedron contains a point or not, returning True
	# if it does and False if not.
	
	def contains( self, point ) :
		
		
		# The point is inside the polyhedron if it's on the inner side of every
		# face.
		
		for f in self.faces :
			if f.isPointOutsideFace( point ) :
				return False
		
		return True
	
	
	
	
	# Clip this convex polyhedron against another convex polyhedron, producing
	# a list of new convex polyhedra that represent the parts of the original
	# that are outside of the other.
	
	def clipTo( self, other ) :
		
		
		# The result is a list of convex polyhedra that represent portions of
		# this one and that are outside at least one of the face planes of the
		# other. I build this result by maintaining a list of polyhedra known
		# to be outside at least one face, while splitting whatever part of
		# this polyhedron is not known to be outside some face of the other
		# against each of those faces in turn.
		
		clippee = self
		
		result = []
		
		for face in other.faces :
		
			if clippee is None :
				break
		
			outside, clippee, splittingFace = clippee.split( face.A, face.B, face.C, face.D )
				
			if outside is not None :
				result.append( outside )
		
		
		# Everything has been split and classified, the result is the list of
		# "outside" polyhedra.
		
		return result
	
	
	
	
	# Split this polyhedron against a plane defined by the equation
	# Ax + By + Cz = D. The coefficients should be chosen so that vector
	# <A,B,C> points to the "outside" of the plane (typically the outside of
	# some polyhedron the plane is a face of). This returns 2 new convex
	# polyhedra, and the face that separates them. The first polyhedron is
	# entirely outside or on the plane, the second is inside or on it. Either
	# of these may be None if no part of this polyhedron is on the
	# corresponding side of the plane. In that case the separating face will
	# also be None. When the separating face is not None, i.e., I really split
	# the polyhedron into 2 non-empty parts, the separating face is oriented as
	# a face of the outside polyhedron.
	
	def split( self, A, B, C, D ) :
		
		
		# The overall idea is to split the faces of this polyhedron into some
		# that lie entirely inside the plane and some that lie entirely
		# outside, then create two new "cap" faces where the plane splits the
		# original polyhedron. I collect edges for the cap faces in
		# dictionaries that are keyed by the vertices at the clockwise ends of
		# the edges (as seen from outside the caps), then use that information
		# to construct the complete faces at the end.
		
		insideFaces = []
		outsideFaces = []
		
		insideCapEdges = EdgeDictionary()
		outsideCapEdges = EdgeDictionary()
		
		for face in self.faces :
	
			outsideFace, insideFace, splittingEdge = face.split( A, B, C, D )
		
			if outsideFace is not None :
				outsideFaces.append( outsideFace )
		
			if insideFace is not None :
				insideFaces.append( insideFace )
		
			if splittingEdge is not None :
			
				try :
					insideCapEdges.add( splittingEdge.vertex2, splittingEdge )
				except KeyError as error :
					print( "ConvexPolyhedron.split unable to add edge to inside cap." )
					print( "\tSplitting {}".format( face ) )
					print( "\tBy plane {}x + {}y + {}z = {}".format( A, B, C, D ) )
					print( "\t{}".format( error ) )
					print( "\tEdge = {}".format( splittingEdge ) )
					print( "\tEdge dictionary = {}".format( insideCapEdges ) )
					sys.exit( 1 )
					
				try :
					outsideCapEdges.add( splittingEdge.vertex1, splittingEdge )
				except KeyError as error :
					print( "ConvexPolyhedron.split unable to add edge to outside cap." )
					print( "\tSplitting {}".format( face ) )
					print( "\tBy plane {}x + {}y + {}z = {}".format( A, B, C, D ) )
					print( "\t{}".format( error ) )
					print( "\tEdge = {}".format( splittingEdge ) )
					print( "\tEdge dictionary = {}".format( outsideCapEdges ) )
					sys.exit( 1 )
	
	
		# Build cap faces, if they exist.
		
		try :
			outsideCap, outsideFaces = addCapFace( outsideFaces, outsideCapEdges )
		except KeyError as error :
			print( "ConvexPolyhedron.split failed to assemble outside cap face:" )
			print( "\tSplitting {}".format( face ) )
			print( "\tBy plane {}x + {}y + {}z = {}".format( A, B, C, D ) )
			print( "\t{}".format( error ) )
			print( "\tEdge dictionary = {}".format( outsideCapEdges ) )
			sys.exit( 1 )
			
		try :
			insideCap, insideFaces = addCapFace( insideFaces, insideCapEdges )
		except KeyError as error :
			print( "ConvexPolyhedron.split failed to assemble inside cap face:" )
			print( "\tSplitting {}".format( face ) )
			print( "\tBy plane {}x + {}y + {}z = {}".format( A, B, C, D ) )
			print( "\t{}".format( error ) )
			print( "\tEdge dictionary = {}".format( insideCapEdges ) )
			sys.exit( 1 )
	
	
		# Reconstruct actual polyhedra from the faces I collected.
	
		inside = makePolyhedronFromFaces( insideFaces, self.color ) if len(insideFaces) >= 4 else None	
		outside = makePolyhedronFromFaces( outsideFaces, self.color ) if len(outsideFaces) >= 4 else None
	
		return outside, inside, outsideCap

	

	
	# Draw this polyhedron to a renderer, i.e., tell the renderer about each of
	# this polyhedron's triangles. The renderer might not actually display the
	# triangles until later.
	
	def draw( self, renderer ) :
		
		
		# Draw the polyhedron by drawing each of its faces separately.
		
		for f in self.faces :
			f.draw( renderer, self.color )
	
	
	
	
	# Build a string containing a next-level-of-detail description of this
	# polyhedron. Being a "next-level" description means that the description
	# identifies the polyhedron and then shows its faces, edges, vertices, and
	# color, but without showing their internal details.
	
	def dumpStr( self ) :
		
		return "<{}: Faces = {}; Edges = {}, Vertices = {}, Color = {}>".format( self, self.faces, self.edges, self.vertices, self.color )




# Given a list of faces for a split convex polyhedron, and an edge dictionary
# of edges for a cap face for that split, create an actual Face object for the
# cap, and add it to the face list. The dictionary has the edges of the cap as
# its values, with vertices at the clockwise ends of the edges as keys. This
# returns both the new face object and the updated face list, in that order.
# If the edge list doesn't have enough edges in it to make a face, return None
# as the cap face and don't change the face list.

def addCapFace( faceList, edgeDict ) :
	
	if edgeDict.size() >= 3 :
		
		
		# There are enough edges to make a face. To do so, pick an arbitrary
		# edge to start at, its counterclockwise end is the clockwise end of
		# the next edge, and so forth until I get back to the vertex I started
		# with (or at least one close to it).
		
		startVertex = edgeDict.keys()[ 0 ]
		currentEdge = edgeDict.find( startVertex )
		edges = [ currentEdge ]
		
		currentVertex = currentEdge.oppositeEnd( startVertex )
		
		while not currentVertex.isCloseTo( startVertex ) :
			currentEdge = edgeDict.find( currentVertex )
			edges.append( currentEdge )
			currentVertex = currentEdge.oppositeEnd( currentVertex )
		
		newFace = Face( edges )
		faceList.append( newFace )
		
		return newFace, faceList
	
	else :
		
		
		# Not enough edges to make a face.
		
		return None, faceList




# Given a list of faces that completely describe some convex polyhedron, create
# the corresponding "ConvexPolyhedron" object. Note that clients must also
# provide the color for the new polyhedron.

def makePolyhedronFromFaces( faceList, color ) :
	
	
	# All I really need to do is make lists of unique edges and vertices
	# referenced by the faces, and then use them and the color to create the
	# new polyhedron.
	
	edges = set()
	vertices = set()
	
	for f in faceList :
		edges |= set( f.edges )
		vertices |= set( f.vertices )
	
	return ConvexPolyhedron( faceList, list(edges), list(vertices), color )
