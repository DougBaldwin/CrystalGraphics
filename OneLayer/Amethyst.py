# A class that represents amethyst crystals in a program that generates and displays
# aggregates of such crystals. These crystals are a kind of convex polyhedron, from which
# they get most of their geometrical and mathematical behavior; this class mainly provides
# a way to initialize amethyst-shaped polyhedra and a color for them.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2019. Created by Doug Baldwin.


from ConvexPolyhedron import ConvexPolyhedron
from Plane import Plane
from VectorOps import orthogonalize3, normalize3, cross
from math import sin, cos, sqrt, pi




class Amethyst ( ConvexPolyhedron ) :
	
	
	
	
	# A color, consisting of red, green, and blue coefficients of diffuse reflection,
	# alpha, specuakt coefficient of reflection, and specular shininess, to use when
	# drawing amethysts
	
	COLOR = [ 0.7, 0.55, 0.98, 0.7, 0.9, 100.0 ]
	
	
	
	
	# I define amethyst polyhedra in a "local" coordinate frame, i.e., a coordinate frame
	# whose origin is at the center of the amethyst and whose axes align with certain
	# crystallographic axes. Once I construct such a polyhedron, I can generate specific
	# amethyst instances by transforming its planes to the global coordinate frame. The
	# following list provides the planes that bound the canonical local-coordinate
	# amethyst. Note that this is a very small amethyst, i.e., one ready to grow into part
	# of an aggregate. My project notes from July 3, 2019 contain derivations for some of
	# the formulas used to calculate these numbers.
	
	N_FACES = 6															# Number of faces around an amethyst
	RADIUS = 0.05														# Faces are this far from the y axis
	HEIGHT = 5.0 * RADIUS												# Top and bottom pyramids start this far from the xz plane
	BODY_D = cos(pi/6) * RADIUS											# D coefficient for planes in the crystal's body
	PYR_D = cos(pi/6) * ( RADIUS + HEIGHT / 1.1 )						# D coefficient for planes in top or bottom pyramids
	PYR_Y = sqrt(3.0) / 2.2												# Y component of normals to pyramid planes
	
	PLANES = [ Plane( cos(pi/6),    PYR_Y,  sin(pi/6),    PYR_D ),		# Top pyramid, starting just CW of x axis and proceeding CW
			   Plane( 0.0,          PYR_Y,  1.0,          PYR_D ),
			   Plane( cos(5*pi/6),  PYR_Y,  sin(5*pi/6),  PYR_D ),
			   Plane( cos(7*pi/6),  PYR_Y,  sin(7*pi/6),  PYR_D ),
			   Plane( 0.0,          PYR_Y,  -1.0,         PYR_D ),
			   Plane( cos(11*pi/6), PYR_Y,  sin(11*pi/6), PYR_D ),
			   Plane( cos(pi/6),    0.0,  sin(pi/6),    BODY_D ),		# Body, following same conventions as top pyramid
			   Plane( 0.0,          0.0,  1.0,          BODY_D ),
			   Plane( cos(5*pi/6),  0.0,  sin(5*pi/6),  BODY_D ),
			   Plane( cos(7*pi/6),  0.0,  sin(7*pi/6),  BODY_D ),
			   Plane( 0.0,          0.0,  -1.0,         BODY_D ),
			   Plane( cos(11*pi/6), 0.0,  sin(11*pi/6), BODY_D ),
			   Plane( cos(pi/6),    -PYR_Y,  sin(pi/6),    PYR_D ),		# Bottom pyramid
			   Plane( 0.0,          -PYR_Y,  1.0,          PYR_D ),
			   Plane( cos(5*pi/6),  -PYR_Y,  sin(5*pi/6),  PYR_D ),
			   Plane( cos(7*pi/6),  -PYR_Y,  sin(7*pi/6),  PYR_D ),
			   Plane( 0.0,          -PYR_Y,  -1.0,         PYR_D ),
			   Plane( cos(11*pi/6), -PYR_Y,  sin(11*pi/6), PYR_D ) ]
	
	
	
	
	# Initialize an amethyst from the x, y, and z coordinates of its center, its azimuth
	# angle (theta), and its polar angle (phi).
	
	def __init__( self, x, y, z, theta, phi ) :
		
	
		# Utility functions that calculate indices for planes' neighbors in the canonical
		# plane list.
	
		def cw( i ) :													# Plane clockwise of plane i in same layer
			return i + 1 if i % Amethyst.N_FACES != Amethyst.N_FACES - 1 else i - Amethyst.N_FACES + 1
		
		def ccw( i ) :													# Plane counterclockwise of i in same layer
			return i - 1 if i % Amethyst.N_FACES != 0 else i + Amethyst.N_FACES - 1
		
		def above( i ) :												# Plane next to i in layer geometrically above; i >= 6
			return i - Amethyst.N_FACES
		
		def below( i ) :												# Plane next to i in layer below; i < 12
			return i + Amethyst.N_FACES
		
		
		# Since I define the basic amethyst shape with a set of canonical planes, start by
		# creating a transformation from the canonical amethyst to the specific instance
		# defined by x, y, z, theta, and phi. This transformation is easiest to transform
		# planes with if I describe it as a 3-by-3 change-of-basis matrix and a separate
		# translation vector. For the change of basis matrix, I figure out where this
		# amethyst's local axes are in the global coordinate system; a matrix with those
		# vectors as its columns will then convert local coordinates to global.
		
		localY = normalize3( [ sin(phi) * cos(theta), cos(phi), sin(phi) * sin(theta) ] )
		localX = normalize3( orthogonalize3( [ cos(theta), 0, sin(theta) ], localY ) )
		localZ = normalize3( cross( localX, localY ) )
		
		localToGlobal = [ [ localX[0],  localY[0],  localZ[0] ],
						  [ localX[1],  localY[1],  localZ[1] ],
						  [ localX[2],  localY[2],  localZ[2] ] ]
		
		translation = [ x, y, z ]
		
		
		# Use that transformation to transform the canonical planes into the ones that
		# bound this instance. Note that the "transform" method for planes expects the
		# transpose of the inverse of the original-to-transformed transformation matrix;
		# since my local-to-global matrix above is orthonormal, its inverse is its
		# transpose, and therefore the transpose of the inverse is the matrix I already
		# have.
		
		instancePlanes = [ p.transform( localToGlobal, translation ) for p in Amethyst.PLANES ]
		
		
		# Give the instance planes neighbors. Since instance planes are grouped into top
		# pyramid, body, and bottom pyramid blocks, there are patterns to the neighbors:
		# Every plane neighbors the ones before and after it in its block, and the one(s)
		# above and/or below it in adjacent blocks. I can mostly use these patterns to
		# assign neighbors, although there are slight differences between blocks and at
		# block boundaries.
		
		for i in range( len(instancePlanes) ) :
			
			if i < Amethyst.N_FACES :											# Top pyramid planes
				instancePlanes[i].addNeighbors( [ instancePlanes[ ccw(i) ],
												  instancePlanes[ cw(i) ],
												  instancePlanes[ below(i) ] ] )
												  
			elif Amethyst.N_FACES <= i < 2 * Amethyst.N_FACES :					# Body planes
				instancePlanes[i].addNeighbors( [ instancePlanes[ above(i) ],
												  instancePlanes[ cw(i) ], 
												  instancePlanes[ below(i) ],
												  instancePlanes[ ccw(i) ] ] )
												  
			else :																# Bottom pyramid planes
				instancePlanes[i].addNeighbors( [ instancePlanes[ cw(i) ],
												  instancePlanes[ ccw(i) ],
												  instancePlanes[ above(i) ] ] )
		
		
		# Finally, use those planes to initialize the amethyst as a convex polyhedron.
		
		super().__init__( instancePlanes )
