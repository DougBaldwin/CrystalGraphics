# A class that represents planes as part of my project to generate crystal
# aggregates. At least as originally conceived, planes mainly serve to split
# polyhedra, faces, or edges. See the project notes for more on the project as
# a whole.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International
# License (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin.




from Vertex import Vertex
from VectorOps import dot3
from math import isclose




class Plane :




    # Internally I represent planes by the coefficients of their equation,
    # Ax + By + Cz = D. I store each coefficient in an attribute of the same
    # name.




    # Initialize a plane, given the coefficients from its equation.

    def __init__( self, A, B, C, D ) :

        self.A = A
        self.B = B
        self.C = C
        self.D = D




    # Test to see if a plane contains a point (represented as a Vertex object),
    # returning True if so and False otherwise.

    def containsPoint( self, point ) :

        # From the equation for a plane, this plane contains the point if the
        # the point's coordinates satisfy Ax + By + Cz = D.

        return isclose( self.A * point.x + self.B * point.y + self.C * point.z, self.D )




    # Test to see if a plane contains an edge, returning True if so and False
    # otherwise.

    def containsEdge( self, edge ) :

        # The plane contains the edge if it contains both of the edge's ends.

        return self.containsPoint( edge.end1) and self.containsPoint( edge.end2 )




    # Decide which side of this plane a vertex lies on. Return +1 if the vertex
    # is in front of the plane, i.e., on the side the normal points to. Return
    # -1 if the point is in back of the plane, and 0 if the point lies in the
    # plane.

    def whichSide( self, point ) :


        # Treat the point as a vector, and take its dot product with the
        # plane's normal. If that product is greater than the plane's D
        # coefficient, the point is in front of the plane; if less, the point
        # is in back of the plane, and if equal the point is in the plane.

        product = self.A * point.x + self.B * point.y + self.C * point.z

        if isclose( product, self.D ) :
            return 0
        elif product > self.D :
            return 1
        else :
            return -1




    # Calculate where the line segment between 2 points intersects a plane.
    # Return a Vertex object for that point, or None if the plane doesn't
    # intersect the segment.

    def intersection( self, point1, point2 ) :


        # Treating the line segment as a parametric equation that passes
        # through point1 when t = 0 and point2 when t = 1, solve for the t at
        # which x, y, and z components of points on the line satisfy this
        # plane's equation. See project notes from June 23, 2017 for the
        # derivation of the equation I use.

        divisor = self.A * ( point2.x - point1.x ) + self.B * ( point2.y - point1.y ) + self.C * ( point2.z - point1.z )

        if isclose( divisor, 0.0 ) :
            # Line segment is parallel to plane, assume no intersection.
            return None

        t = ( self.D - self.A * point1.x - self.B * point1.y - self.C * point1.z ) / divisor


        # What I return depends on the t at which the intersection occurs:
        #   - If t corresponds to either end of the line segment, return the
        #     existing vertex at that end rather than making a new one.
        #   - If t is distinctly between 0 and 1, then it corresponds to a
        #     new intersection; create a new point for that intersection.
        #   - If t is outside the interval [0,1], then there's no intersection
        #     within the segment.

        if isclose( t, 0.0 ) :
            return point1

        elif isclose( t, 1.0 ) :
            return point2

        elif 0.0 < t < 1.0 :
            return Vertex( (1.0 - t) * point1.x + t * point2.x,
                           (1.0 - t) * point1.y + t * point2.y,
                           (1.0 - t) * point1.z + t * point2.z )

        else :
            return None




    # Return a normal vector for this plane, in a form my vector utilities will
    # understand as a vector in homogeneous form.

    def normal( self ) :

        return [ self.A, self.B, self.C, 0.0 ]
