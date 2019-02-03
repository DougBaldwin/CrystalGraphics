# This class represents amethyst crystals for use in a program that generates and
# renders crystal aggregates consisting of a single layer of crystal on top of a
# substrate. These crystals adaptively compute their sizes so that they butt up against
# their neighbors in the aggregate. Other geometric information comes from "mindat.org,"
# particularly its "Quartz no. 7" data and visualization. See file "OneLayer.py" for more
# information about the larger program this class is part of.

# Copyright (C) 2017, 2018 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2018 -- Version that does adaptive sizing created by Doug Baldwin, working from
#     an original that simply gave crystals random sizes.
#
#   May 2017 -- Original version created by Doug Baldwin.


from ConvexPolyhedron import ConvexPolyhedron, Vertex
from Triangle import Triangle
from VectorOps import dot3, cross, orthogonalize3, normalize3, transpose, matrixMultiply
from SymmetryOps import transform4
from MathUtilities import nearlyEqual, infinity
from math import sqrt, sin, cos, pi




class Amethyst( ConvexPolyhedron ) :
	
	
	
	
	# Internally, I represent an amethyst by the following members:
	#   - x, y, z: The global x, y, and z coordinates of the nominal center of the amethyst.
	#   - theta, phi:  The azimuth and polar angles that give this amethyst's orientation
	#     (azimuth -- theta -- is measured counterclockwise from the x axis, as seen when
	#     looking down the y axis, and polar angle -- phi -- is measured down from the y
	#     axis; both angles are in radians).
	#   - localToGlobal: a transformation matrix that transforms points or vectors in a
	#     coordinate frame local to the amethyst (y axis aligns with crystallographi c
	#     axis, x and z axes more or less arbitrary) to points or vectors in the global
	#     coordinate frame.
	#   - clippingPlanes: a list of planes to clip this amethyst against in order to make
	#     it butt up against its neighbors when drawn. Each plane is represented by a
	#     4-element list [a,b,c,d] of coefficients for a plane equation ax + by + cz = d.
	#     The a, b, and c coefficients should be chosen so that vector <a,b,c>, the normal
	#     to the clipping plane, points out of the amethyst.
	
	
	# All amethysts share a list of vertices that describe the top pyramid of a canonical
	# amethyst in the local coordinate frame. This pyramid has a hexagonal base that
	# extends 1 unit along the crystallographic a axes. The apex of the pyramid is 1.1
	# units (because the ratio of c units to a units for quartz is 1.1 : 1) above the base.
	# The first 6 vertices in this list form the base of the pyramid, in clockwise order
	# as seen from above, and the last one is the apex. These vertices' main use is to
	# compute amethysts' "footprints," i.e., a projection onto the xz plane that captures
	# orientation but not size information; I define the canonical vertices here rather
	# than in the "getFootprint" function to void regenerating them every time someone
	# asks for a footprint. I also define a variable that stores the index of the apex in
	# the list of canonical vertices, for easy reference elsewhere. Note that vertices are
	# in homogeneous form.
	
	canonicalVertices = [ [  1.0,          0.0,  0.0,          1.0 ],
						  [  cos(pi/3),    0.0,  sin(pi/3),    1.0 ],
						  [  cos(2*pi/3),  0.0,  sin(2*pi/3),  1.0 ],
						  [ -1.0,          0.0,  0.0,          1.0 ],
						  [  cos(4*pi/3),  0.0,  sin(4*pi/3),  1.0 ],
						  [  cos(5*pi/3),  0.0,  sin(5*pi/3),  1.0 ],
						  [  0.0,          1.1,  0.0,          1.0 ] ]
	
	canonicalApexIndex = 6
	
	
	
	
	# Initialize an amethyst crystal from the position of its center and the orientation
	# of its crystallographic c axis relative to the global coordinate frame (given as an
	# azimuthal angle theta and a polar angle phi).
	
	def __init__( self, x, y, z, theta, phi ) :
		
		
		# Start by initializing the superclass with the color of amethysts.
		
		super().__init__( [ 0.7, 0.55, 0.98, 0.7, 0.9, 100.0 ] )
		
		
		# Store the parameters in the corresponding member variables.
		
		self.x = x
		self.y = y
		self.z = z
		self.theta = theta
		self.phi = phi
		
		
		# Build and store the local-to-global coordinate transformation. Create unit
		# vectors along the global c and a1 crystallographic axes, based on the azimuth
		# and polar angles, then create a unit-length global z axis orthogonal to both.
		# These vectors define the first 3 columns of the transformation matrix (a axis
		# corresponding to x, c to y, and z to z); the fourth column is the amethyst's
		# position.
		
		c = [ sin(phi) * cos(theta), cos(phi), sin(phi) * sin(theta) ]
		a1 = normalize3( orthogonalize3( [ cos(theta), 0, sin(theta) ], c ) )
		localZ = normalize3( cross( a1, c ) )
		
		self.localToGlobal = [ [ a1[0],  c[0],  localZ[0],  x   ],
						       [ a1[1],  c[1],  localZ[1],  y   ],
						       [ a1[2],  c[2],  localZ[2],  z   ],
						       [ 0.0,    0.0,   0.0,        1.0 ] ]
		
		
		# Every amethyst starts with no clipping planes.
		
		self.clippingPlanes = []
	
	
	
	
	# Get the position of this amethyst in 3D space, represented as a 3D point.
	
	def getPosition( self ) :
		return [ self.x, self.y, self.z ]
	
	
	
	
	# Return a list of triangles that define this amethyst's footprint, or projection, on
	# the xz plane.
	
	def getFootprint( self ) :
		
		
		# Transform the vertices of the canonical amethyst to global coordinates using
		# this particular amethyst's transformation. Project the resulting points to the
		# xz plane for later use in finding the "footprint" triangles.
		
		globalCanonicalVertices = transform4( self.canonicalVertices, self.localToGlobal )
		
		footprintVertices = [ [v[0],v[2]] for v in globalCanonicalVertices ]
		
		
		# Step through the footprint vertices that come from the base of the canonical
		# amethyst, building a triangle from the center of this amethyst and each pair of
		# base vertices. But note that amethyst might be tilted so far that the apex of
		# the crystal might project to a point farther from the center than any base
		# vertex. The geometry of how I rotate amethysts is such that the apex always
		# projects onto the same line from the center as the 1st base vertex (that vertex
		# is on the local x axis, and I rotate amethysts down towards that axis), so if
		# the apex does project farther than the base vertices, it will specifically
		# project farther than the 1st base vertex, and I can get the correct footprint by
		# replacing the projection of the 1st base vertex with the projection of the apex
		# in those cases.
		
		footprint = []
		
		previousVertex = footprintVertices[ self.canonicalApexIndex - 1 ]
		
		for currentIndex in range(self.canonicalApexIndex) :
			
			if     currentIndex == 0 \
			   and self.xzRadius( footprintVertices[self.canonicalApexIndex] ) > self.xzRadius( footprintVertices[currentIndex] ):	
				currentVertex = footprintVertices[ self.canonicalApexIndex ]
			else:
				currentVertex = footprintVertices[ currentIndex ]
				
			footprint.append( Triangle( [self.x,self.z], previousVertex, currentVertex ) )
			
			previousVertex = currentVertex
		
		
		# All the footprint triangles have been assembled, return them.
		
		return footprint
	
	
	
	
	# Ensure that an amethyst has a certain clipping plane. I define the plane by the
	# coefficients of an equation ax + by + cz = d; clients should choose these
	# coefficients so that the vector <a,b,c> points out of the amethyst. This method
	# modifies the amethyst, but otherwise has no return value. But note that if the
	# amethyst already has a clipping plane equal to the requested one, I don't add a
	# second copy of it.
	
	def addClippingPlane( self, a, b, c, d ) :
		
		
		# Check the existing clipping planes to see if one is nearly equal to the new one.
		# If so, just return without adding the new one. For now, this is a literal test
		# for equality of coefficients, it doesn't try to recognize planes that are equal
		# because their coefficients are scalar multiples of each other, etc.
		
		for plane in self.clippingPlanes :
			if nearlyEqual(plane[0],a) and nearlyEqual(plane[1],b) and nearlyEqual(plane[2],c) and nearlyEqual(plane[3],d) :
				return
		
		
		# No existing plane equals the new one, so add the new one:
		
		self.clippingPlanes.append( [ a, b, c, d ] )
	
	
	
	
	# Build an amethyst, i.e., give it actual faces and vertices. This involves several
	# steps, namely using the amethyst's clipping planes to figure out how big it can be
	# along its a and c axes, and then using that size information to define the global
	# coordinate faces and vertices.
	#   Precondition: Clipping planes for neighbor crystals have been defined.
	
	def build( self ) :
		
		
		# Figure out a maximum extent for this amethyst in the a direction and a minimum
		# in the c direction. Step through each clipping plane, transforming it to the
		# local coordinate frame and calculating its a and c distances. Keep track of
		# the maximum a and minimum c as I do so. See the project notes from June 19
		# through 22, 2018 for derivations and rationale behind the equations used here,
		# along with revised understanding of how to apply those results discussed July 2
		# through 9.
		
		# In order to transform planes' normals, I will need the transpose of the inverse
		# of the 3-by-3 transformation matrix from global coordinates to local
		# (conveniently, that inverse is the local-to-global transformation already stored
		# in this amethyst, so I just have to pick out its upper left 3-by-3 submatrix and
		# transpose).
		
		mInverse = [ [ self.localToGlobal[r][c] for c in range(0,3) ] for r in range(0,3) ]		# Inverse of 3x3 global-to-local
		globalDisplacement = [ - self.localToGlobal[r][3] for r in range(0,3) ]					# Displacement for global-to-local
		normalsToLocal = transpose( mInverse  )													# Global-to-local for normals
		
		maxADistance = 0
		minCDistance = infinity()
		
		
		# Now I can step through the clipping planes...
		
		for plane in self.clippingPlanes :
						
			
			# Calculate the coefficients for the local plane equation.
			
			globalNormal = [ plane[0:3] ]
			localNormal = matrixMultiply( normalsToLocal, transpose( globalNormal ) )
			
			A = localNormal[0][0]
			B = localNormal[1][0]
			C = localNormal[2][0]
			D = plane[3] + dot3( plane[0:3], globalDisplacement )
			
			
			# Update the maximum a distance.
			
			if nearlyEqual( A, 0.0 ) :
				maxADistance = max( maxADistance, abs(C) )
			else :
				x = A * D / ( A**2 + C**2 )
				z = C * x / A
				maxADistance = max( maxADistance, sqrt( x**2 + z**2 ) )
			
			
			# Update the minimum positive c distance.
			
			if not nearlyEqual( B, 0.0 ) :
				cDistance = D / B
				if cDistance > 0 and cDistance < minCDistance :
					minCDistance = cDistance
		
		
		# I now have a maximum distance from the amethyst to any neighbor in the directions
		# of the a axes and a minimum distance in the direction of the c axis. There are
		# 2 ways these distances could influence the size of the amethyst: it could grow
		# in the a direction until stopped by a neighbor, with the c size growing
		# without constraint, or it could grow in the c direction until stopped by a
		# neighbor, while growing unconstrained in the a direction. To decide which
		# happens, I scale the allowed c distances to account for the fact that units of
		# growth in the c direction aren't the same size as units in the a direction and
		# then grow to whichever of a or scaled c is smaller.
		
		cToARatio = 1.1
		
		if minCDistance / cToARatio < maxADistance :
			cExtent = minCDistance
			aExtent  = cExtent / cToARatio
		else :
			aExtent = maxADistance
			cExtent = aExtent * cToARatio
		
		
		# The actual crystal is a hexagonal prism with pyramidal ends. Build a list of
		# vertices for this shape in homogeneous local coordinates, starting with the
		# apexes of the top and bottom pyramids and then adding in top and bottom vertices
		# of the hexagonal body.
		
		topApexY = cExtent + aExtent * cToARatio
		
		vertices = [ [ 0, topApexY, 0, 1 ],
					 [ 0, -topApexY, 0, 1 ] ]

		angleStep = pi / 3
		for i in range( 6 ) :
			angle = i * angleStep
			vertexX = aExtent * cos( angle )
			vertexZ = aExtent * sin( angle )
			vertices += [ [vertexX, cExtent, vertexZ, 1], [vertexX, -cExtent, vertexZ, 1] ]

		
		# Now transform the vertices to the global coordinate frame.
		
		globalVertices = [ Vertex( v[0], v[1], v[2] ) for v in transform4( vertices, self.localToGlobal ) ]
				

		# Use the transformed vertices to define the faces of the crystal. Define them
		# in groups of 3, one group for each side of the prism. Each group contains a
		# triangle from the top pyramid, a rectangle from the side of the prism, and a
		# triangle from the bottom pyramid.

		for i in range( 6 ) :
			nextI = ( i + 1 ) % 6
			thisTop = globalVertices[ self.topIndex(i) ]				# Top corner of prism at current angle
			thisBottom = globalVertices[ self.bottomIndex(i) ]			# Bottom corner of prism at current angle
			nextTop = globalVertices[ self.topIndex(nextI) ]			# Top corner at next angle
			nextBottom = globalVertices[ self.bottomIndex(nextI) ]		# Bottom corner at next angle
			self.defineFace( [ globalVertices[0], nextTop, thisTop ] )
			self.defineFace( [ thisTop, nextTop, nextBottom, thisBottom ] )
			self.defineFace( [ thisBottom, nextBottom, globalVertices[1] ] )
		
		
		# Finally, clip the amethyst to each of its clipping planes.
		
		for plane in self.clippingPlanes :
			self.clip( plane[0], plane[1], plane[2], plane[3] )
	
	
	
	
	# Write this amethyst's state to a logger. At the moment, the "state" I feel it's
	# worth logging is the amethyst's position and orientation. This method returns the
	# ID that the logger assigned to the amethyst's log record.
	
	def log( self, logger ) :
		
		template = "Amethyst at ({0}, {1}, {2}) with azimuth {3} and polar angle {4}"
		return logger.addRecord( template.format( self.x, self.y, self.z, self.theta, self.phi ) )




	# A utility method that finds the radial distance from the (x,z) center of this
	# amethyst to a point in the xz plane.
	
	def xzRadius( self, point ) :
		
		return sqrt( ( point[0] - self.x ) ** 2 + ( point[1] - self.z ) ** 2 )




	# Utility methods that compute indices into the list of vertices created in the
	# "build" method. Specifically, these methods compute indices to the vertices at the
	# top and bottom of the prism at the i-th angle around the prism. The calculation is
	# based on the idea that the first 2 vertices in the list are the apexes of the
	# pyramids, and the remaining vertices are pairs from the prism, with a top vertex
	# first in each pair and the corresponding bottom vertex second.
	
	def topIndex( self, i ) :
		return 2 + 2 * i
	
	def bottomIndex( self, i ) :
		return 3 + 2 * i

