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
from math import isclose, fabs, fsum, sqrt
from sys import float_info




class Plane :




    # Internally I represent planes by the coefficients of their equation,
    # Ax + By + Cz = D. I store each coefficient in an attribute of the same
    # name. I normalize planes when I create them so that the normal vector
    # <A,B,C> is a unit vector.


    # To control round-off in plane calculations (and ultimately other
    # calculations that depend on them), I make 2 more or less arbitrary
    # decisions: any point less than half a micron away from a plane can be
    # considered to be in that plane, and any sufficiently small number at all
    # can be considered to be 0.

    planeTolerance = 0.00005
    zeroTolerance = 1e-10




    # Initialize a plane, given the coefficients from its equation.

    def __init__( self, A, B, C, D ) :

        magnitude = sqrt( A*A + B*B + C*C )

        self.A = A / magnitude
        self.B = B / magnitude
        self.C = C / magnitude
        self.D = D / magnitude




    # Test to see if a plane contains a point (represented as a Vertex object),
    # returning True if so and False otherwise.

    def containsPoint( self, point ) :

        # From the equation for a plane, this plane contains the point if the
        # the point's coordinates satisfy Ax + By + Cz = D, to within the
        # tolerance for being in a plane.

        return isclose( self.planeZero( point.x, point.y, point.z ), 0.0, abs_tol = Plane.planeTolerance )




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

        planeNumber = self.planeZero( point.x, point.y, point.z )

        if isclose( planeNumber, 0.0, abs_tol = Plane.planeTolerance ) :
            return 0
        elif planeNumber > 0.0 :
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

        divisor = self.planeNumber( point2.x - point1.x, point2.y - point1.y, point2.z - point1.z )

        if isclose( divisor, 0.0, abs_tol = Plane.zeroTolerance ) :
            # Line segment is parallel to plane, assume no intersection.
            return None

        numerator = -self.planeZero( point1.x, point1.y, point1.z )
        t = numerator / divisor


        # What I return depends on the t at which the intersection occurs:
        #   - If t corresponds to either end of the line segment, return the
        #     existing vertex at that end rather than making a new one.
        #   - If t is distinctly between 0 and 1, then it corresponds to a
        #     new intersection; create a new point for that intersection.
        #   - If t is outside the interval [0,1], then there's no intersection
        #     within the segment.

        if isclose( t, 0.0, abs_tol = Plane.planeTolerance ) :
            return point1

        elif isclose( t, 1.0, abs_tol = Plane.planeTolerance ) :
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




    # Calculate Ax + By + Cz, i.e., the "plane number" for this plane and the
    # x, y, and z values provided by the client. Do not include terms whose
    # coefficient in the plane is what I consider to be 0.

    def planeNumber( self, x, y, z ) :

        terms = []

        def pushTerm( coeff, component ) :
            if fabs(coeff) > Plane.zeroTolerance :
                terms.append( coeff * component )

        pushTerm( self.A, x )
        pushTerm( self.B, y )
        pushTerm( self.C, z )

        return fsum( terms )




    # Calculate Ax + By + Cz - D for this plane and the x, y, and z values
    # given as arguments. Do the calculation as accurately as possible. This
    # can be useful to clients who want to know whether point (x,y,z) is on one
    # side or the other of the plane, or in it.

    def planeZero( self, x, y, z ) :

        terms = []                          # A list of values to add

        def pushTerm( coeff, value ) :      # Append a value to the list, if the corresponding plane coefficient is non-zero
            if fabs(coeff) > Plane.zeroTolerance :
                terms.append( value )

        pushTerm( self.A, self.A * x )
        pushTerm( self.B, self.B * y )
        pushTerm( self.C, self.C * z )
        pushTerm( self.D, -self.D )

        return fsum( terms )




    # Write a machine-readable description of this plane to a text stream
    # provided by the caller. Geometric objects written to this stream have ID
    # numbers, which I track with an ID manager that's also provided by the
    # caller. See project notes from August 17, 21, and 22, 2023 for more
    # information on the format for writing objects and the motivation for it.

    def write( self, stream, ids ) :

        # Identify this geometry as a plane, regardless of whether it's
        # already in the dictionary.
        stream.write( "[Plane " )

        # If the plane already has an ID number, just write it and I'm done.
        if ids.contains( self ) :
            stream.write( "{}]".format( ids.find(self) ) )

        else :
            # Generate an ID for this plane, and write the full description.
            id = ids.next()
            ids.store( self, id )
            stream.write( "{} {} {} {} {}]".format( id, self.A, self.B, self.C, self.D ) )

        # Anything more that gets written to this stream starts on a new line.
        stream.write( "\n" )
