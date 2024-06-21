# A class that represents polygons for programs that generate and render
# crystal aggregates. In this context, polygons are possibly tree-structured
# regions in a plane bounded by a closed sequence of edges (line segments).
# Leaves in the "tree structure" are convex polygons. Internal nodes are pairs
# of polygons with a common edge. Although this representation can in principle
# represent concave polygons, this class is part of a set of classes for
# representing polyhedra, and in that context every polygon is a face of some
# convex polyhedron, and so is itself convex. See my notes for the crystal
# aggregates project for more on this class and the project it's part of.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin.




from Vertex import Vertex
from Edge import Edge, checkEndParents
from Plane import Plane
from GeometryUtilities import safeWrite, listWrite
from VectorOps import cross, scale3, dot3




class Polygon :




    # I represent polygons by the following attributes:
    #   - edges, a list of the polygon's edges. These edges are consecutive as
    #     one moves around the polygon, but their order is otherwise
    #     unconstrained.
    #   - front, the "front" sub-polygon if there is one, and None otherwise.
    #   - back, the "back" sub-polygon if there is one, and None otherwise.
    #   - splitterEdge, the edge that separates from front and back sub-
    #     polygons, or None if this polygon isn't split.




    # Initialize an unsplit polygon from a list of its edges. The edges in the
    # list must be consecutive as one moves around the polygon, but that can be
    # in either clockwise or counterclockwise order (clients have to keep track
    # of polygon orientation if it matters to them). Because this is an unsplit
    # polygon, the edges must also define a convex shape.

    def __init__( self, edges ) :

        # Initializing this polygon just requires remembering the edge list and
        # noting that there are no front or back sub-polygons.

        self.edges = edges

        self.front = None
        self.back = None
        self.splitterEdge = None


        # For debugging, check to see if any consecutive edges are parallel.

        nEdges = len( self.edges )
        for i in range( nEdges ) :
            next = ( i + 1 ) % nEdges
            if self.edges[i].isParallelTo( self.edges[next] ) :
                raise RuntimeError( "Polygon edges {} and {} are parallel".format( self.edges[i], self.edges[next] ) )




    # Split a polygon with a plane. This method modifies the polygon to reflect
    # its resulting split structure, and also returns three results: the
    # polygon from this one that is in front of the plane (i.e., on the side
    # its normal points towards), the polygon in back of the plane, and the
    # edge that separates those polygons. Any or all of these may be None,
    # e.g., if the polygon lies entirely on one side of the plane. Note that
    # I'm relying on polygons being convex to ensure that there will be at most
    # one of each of these results.

    def split( self, plane ) :


        # Start by seeing if this polygon lies in the plane. In that case I
        # don't care whether it's split or not.

        if all( [ plane.containsEdge(e) for e in self.edges ] ) :
            # Signal that the polygon lies in the plane by returning it as both
            # in front and in back, but with no splitter edge.
            return self, self, None


        elif self.front is None and self.back is None :

            # If this polygon isn't split, walk through its edges, splitting each
            # with the plane and keeping track of which edges or parts lie on each
            # side of it in order to make new polygons.

            frontEdges = []
            backEdges = []
            inEdges = []
            splitterVertices = []

            for e in self.edges :

                frontPart, backPart, splitter = e.split( plane )

                if frontPart is not None :
                    if frontPart is backPart :
                        # Front and back edges are the same, i.e., this edge
                        # lies in the plane
                        inEdges.append( frontPart )
                    else :
                        frontEdges.append( frontPart )

                if backPart is not None and backPart is not frontPart :
                    # Case where front and back are the same has already been
                    # handled, so I'm only interested in non-empty back parts
                    # that are distinct from the front here.
                    backEdges.append( backPart )

                if splitter is not None and splitter not in splitterVertices :
                    # A splitter vertex can show up twice if the plane passes
                    # exactly through it. In that case, I only want to record
                    # it once.
                    splitterVertices.append( splitter )


            # Figure out how to build the resulting polygons and split this
            # one. Cases to consider are...
            #  - If all of the edges ended up in front of the plane, then no
            #    split happened and this polygon is the front result.
            #  - If all of the edges ended up in back of the plane, there's
            #    similarly no split and this polygon is the back result.
            #  - If all but one edge ended up in front of the plane and the
            #    other in back or in it, and the splitting vertices are the
            #    ends of that odd edge, then the polygon really lies in front
            #    of the plane with one edge in it; this polygon is the front
            #    result, but call the odd edge a splitting edge.
            #  - Similarly if all but one edge is in back of the plane and one
            #    in front or in, and with splitting vertices equal to its ends,
            #    the polygon is really in back of the plane with the odd edge
            #    as a splitting edge.
            #  - If some edges are in front of the plane and some in back,
            #    the polygon splits non-trivially into 2 parts.
            #  - Otherwise ??? (Might want to catch the case where one edge
            #    is in the plane and all others either in front or in back?)

            if len(frontEdges) >= 2 and len(backEdges) >= 2 and len(splitterVertices) == 2 :

                # Non-trivial split. Since this polygon was originally unsplit,
                # it must be convex. Therefore it splits along one edge,
                # defined by 2 splitter vertices, into 2 sub-polygons. Make a
                # splitter edge from the splitter vertices, then insert that
                # edge into both the front and back edges to create the edge
                # lists for these new polygons.

                splitterEdge = Edge( splitterVertices[0], splitterVertices[1] )

                frontEdges = insertEdge( splitterEdge, frontEdges )
                backEdges = insertEdge( splitterEdge, backEdges )

                if nearCollinear( splitterEdge, frontEdges ) or nearCollinear( splitterEdge, backEdges ) :
                    print( "Polygon.split would make splitter edge {} nearly collinear with neighbor(s) in subpolygons".format( splitterEdge ) )

                self.splitterEdge = splitterEdge
                self.front = Polygon( frontEdges )
                self.back = Polygon( backEdges )

                return self.front, self.back, self.splitterEdge

            elif len(frontEdges) >= 3 and len(backEdges) == 0 :
                # Case where the whole polygon is in front of the plane.
                return self, None, None

            elif len(backEdges) >= 3 and len(frontEdges) == 0 :
                # Case where the whole polygon is in back of the plane.
                return None, self, None

            elif self.touchesPlane( frontEdges, backEdges, splitterVertices ) :
                # The polygon is really in front of the plane, but one edge rests in it.
                return self, None, backEdges[0]

            elif self.touchesPlane( frontEdges, inEdges, splitterVertices ) :
                # Once again, polygon is in front of the plane with one edge in it.
                return self, None, inEdges[0]

            elif self.touchesPlane( backEdges, frontEdges, splitterVertices):
                # The polygon is really in back of the plane, with one edge resting in it.
                return None, self, frontEdges[0]

            elif self.touchesPlane( backEdges, inEdges, splitterVertices ) :
                # Another case where the polygon is in back of the plane with one edge in it.
                return None, self, inEdges[0]

            else :

                raise ValueError( "First split of polygon doesn't match any known split rule." )
                return None, None, None


        else :

            # This polygon is already split, so the plane interacts with it in
            # one of the following ways:
            #   - The polygon is entirely in front of the plane
            #   - The polygon is entirely in back of the plane
            #   - The plane exactly duplicates the polygon's existing split
            #   - The plane splits the front sub-polygon
            #   - The plane splits the back sub-polygon
            #   - The plane splits both the front and the back sub-polygons.

            if plane.containsEdge( self.splitterEdge ) :
                # The plane splits the polygon the way it's already split. The
                # only question is which way this plane's normal points
                # relative to the points in the front and back parts.
                frontSide = self.front.whichSide( plane )
                if frontSide > 0 :
                    return self.front, self.back, self.splitterEdge
                else :
                    return self.back, self.front, self.splitterEdge

            else :

                # Split the front and back, and use the results to decide which
                # of the remaining polygon-plane relationships hold.

                frontFront, frontBack, frontSplitter = self.front.split( plane )
                backFront, backBack, backSplitter = self.back.split( plane )

                if frontFront is self.front and frontBack is None and backFront is self.back and backBack is None :
                    # The whole polygon is in front of the plane, but might
                    # have an edge lying in it.
                    return self, None, planeEdge( frontSplitter, backSplitter )

                elif frontFront is None and frontBack is self.front and backFront is None and backBack is self.back :
                    # The whole polygon is in back of the plane, but might have
                    # an edge in it.
                    return None, self, planeEdge( frontSplitter, backSplitter )

                elif frontFront is self.front and frontBack is None and frontSplitter is None and backFront is not None and backBack is not None and backSplitter is not None :
                    # Plane non-trivially splits back, while front is in front
                    # of plane.
                    return makeSplitPolygon( self.front, backFront, self.splitterEdge ), backBack, backSplitter

                elif frontFront is None and frontBack is self.front and frontSplitter is None and backFront is not None and backBack is not None and backSplitter is not None :
                    # Plane non-trivially splits back and front is in back of
                    # plane.
                    return backFront, makeSplitPolygon( backBack, self.front, self.splitterEdge), backSplitter

                elif frontFront is not None and frontBack is not None and frontSplitter is not None and backFront is self.back and backBack is None and backSplitter is None :
                    # Plane non-trivially splits front and back is in front of
                    # plane.
                    return makeSplitPolygon( frontFront, self.back, self.splitterEdge ), frontBack, frontSplitter

                elif frontFront is not None and frontBack is not None and frontSplitter is not None and backFront is None and backBack is self.back and backSplitter is None :
                    # Plane splits front and back is in back of plane.
                    return frontFront, makeSplitPolygon( frontBack, self.back, self.splitterEdge ), frontSplitter

                elif     frontFront is not None and frontBack is not None and frontSplitter is not None \
                     and backFront is not None and backBack is not None and backSplitter is not None :

                    # Plane splits both front and back of existing polygon, so
                    # I need to combine front-front and back-front to form the
                    # front of a new split polygon, and similarly for the back.
                    return makeSplitPolygon( frontFront, backFront, frontFront.sharedEdge(backFront) ), \
                           makeSplitPolygon( frontBack, backBack, frontBack.sharedEdge(backBack) ), \
                           frontSplitter.commonParent( backSplitter )

                else :

                    # I haven't figured out what the splitting results mean
                    # yet. Display them and return dummy results.

                    print( "Polygon.split splitting already-split polygon {0} with front {0.front} and back {0.back}".format( self ) )
                    print( "\tby plane {0.A:.3}x + {0.B:.3}y + {0.C:.3}z = {0.D:.3}".format( plane ) )
                    print( "\tfront splits to front-front {} and front-back {} separated by {}".format( frontFront, frontBack, frontSplitter ) )
                    print( "\tback splits to back-front {} and back-back {} separated by {}".format( backFront, backBack, backSplitter ) )

                    return None, None, None


                # Old cases that are dead code for now.

                # The only remaining interactions now are that the polygon is
                # entirely in front of the plane or entirely in back. See if
                # any edge lies in the plane, and if one does treat the plane
                # as trivially splitting the polygon. Otherwise the polygon is
                # cleanly all in front or all in back of the plane.

                trivialSplitter = None

                for e in self.edges :
                    if plane.containsEdge( e ) :
                        trivialSplitter = e
                        break

                if self.whichSide( plane ) > 0 :
                    # Entirely in front.
                    return self, None, trivialSplitter
                else :
                    return None, self, trivialSplitter

                # End of old cases.




    # A predicate for the "split" method that looks at its results and decides
    # whether they indicate that this polygon is really on one side or the
    # other of a plane, but with one edge in the plane. The criterion for this
    # is that all but one of the edges from this polygon ended up on one side
    # of the plane, one edge ended up on the other, and that edge's endpoints
    # are the ones identified as splitting vertices. Return True if this
    # polygon does seem to touch the plane as described, and False if not.

    def touchesPlane( self, onSideEdges, offSideEdges, splitterVertices ) :

        return      len( onSideEdges ) == len( self.edges ) - 1 \
                and len( offSideEdges ) == 1 \
                and len( splitterVertices ) == 2 \
                and offSideEdges[0].hasEnd( splitterVertices[0] ) \
                and offSideEdges[0].hasEnd( splitterVertices[1] )




    # Given that this polygon lies entirely on one side or the other of a
    # plane, figure out which side that is. Return a positive number if the
    # polygon is on the side the plane's normal points towards, and a negative
    # number if the polygon is on the opposite side. May return 0 if the
    # precondition that the polygon is entirely on one side of the plane seems
    # not to hold.

    def whichSide( self, plane ) :


        # Approximate the polygon's centroid by averaging the endpoints of its
        # first edge and the edge halfway around the polygon. Since the polygon
        # is suppose to be convex, this is a point somewhere near its center,
        # so assume the whole polygon is on whichever side of the plane that
        # point is.

        def mean4( a, b, c, d ) :
            return ( a + b + c + d ) / 4.0

        halfway = len( self.edges ) // 2

        pt1 = self.edges[0].end1
        pt2 = self.edges[0].end2
        pt3 = self.edges[halfway].end1
        pt4 = self.edges[halfway].end2

        centroid = Vertex( mean4( pt1.x, pt2.x, pt3.x, pt4.x ),
                           mean4( pt1.y, pt2.y, pt3.y, pt4.y ),
                           mean4( pt1.z, pt2.z, pt3.z, pt4.z ) )

        return plane.whichSide( centroid )




    # Return a plane that this polygon lies in. Clients provide a direction (+1
    # or -1, interpreted as an increment between indices of consecutive
    # vertices) in which to traverse the polygon's vertices, with the idea
    # being that the "outside" side of the returned plane, i.e., the side its
    # normal points toward, is the one from which that traversal looks
    # counterclockwise.

    def plane( self, orientation ) :


        # The plane is defined by the equation Ax + By + Cz = D, where A, B,
    	# and C are the components of the normal. Calculate D by evaluating
        # Ax + By + Cz at any convenient vertex of the polygon.

        normal = self.getNormal( orientation )
        D = dot3( normal, self.edges[0].end1.coordinates() )

        return Plane( normal[0], normal[1], normal[2], D )




    # Figure out the orientation that this polygon should have in order to
    # make the normal to its plane point in the same direction as a
    # reference vector. Return either +1 or -1 for the orientation.

    def getOrientation( self, reference ) :


        # I can check whether an orientation is right according to whether it gives
        # a normal to the polygon that points in the same direction as the
        # reference, i.e., has a positive dot product with the reference. So try
        # orientation +1, and if that doesn't pass the check, use -1.

        return 1 if dot3( self.getNormal(1), reference ) > 0.0 else -1




    # Find the normal vector to this polygon's plane. Clients provide a
    # direction (+1 or -1, interpreted as an increment between indices of
    # consecutive vertices) in which to traverse the polygon's vertices, with
    # the idea being that the "outside" side of the plane, i.e., the side its
    # normal points toward, is the one from which that traversal looks
    # counterclockwise.

    def getNormal( self, orientation ) :


        # Start by assuming that the requested orientation is positive, so
        # that the desired normal is the cross product of the vector along edge
        # 0 in the direction of edge 1 crossed into the vector along edge 1 in
        # the direction of edge 2. (If this assumption is wrong, I can fix it
        # by negating the cross product.)

        normal = cross( self.edges[0].vectorTo( self.edges[1] ), self.edges[1].vectorTo( self.edges[2] ) )


        # Check whether I was right about the orientation, fixing the normal if
        # not.

        if orientation < 0 :
            normal = scale3( normal, -1.0 )


        # Now I have the normal that I want to return.

        return normal




    # Find the edge that this polygon shares with another one. Return that
    # edge, or raise a ValueError exception if there isn't a shared edge.

    def sharedEdge( self, other ) :


        # Step through this polygon's edges until I find one that's in the
        # other polygon's edge list. As soon as I find such an edge, return it.
        # If I get all the way through this polygon's edges without finding a
        # match, raise the exception.

        for e in self.edges :
            if e in other.edges :
                return e

        raise ValueError( "No shared edge found by Polygon.sharedEdge" )




    # Draw this polygon to a renderer, using a given orientation to determine
    # what order to draw vertices in, and a given color.

    def draw( self, renderer, orientation, color ) :

        if self.front is not None and self.back is not None :

            # If this is a split polygon, just draw the front and back parts
            # recursively.

            self.front.draw( renderer, orientation, color )
            self.back.draw( renderer, orientation, color )

        else :

            # If not split, send vertices to the renderer in the order implied
            # by the orientation argument, assuming that will define triangles
            # in counterclockwise order. Start doing this by figuring out which
            # end of the edge list to start at and which to end at.

            if orientation > 0 :
                # Positive orientation means I'm going from 0 to the end.
                start = 0
                end = len( self.edges ) - 1
            else :
                start = len( self.edges ) - 1
                end = 0


            # The starting edge provides one vertex that all triangles share,
            # and one that will be the first in a walk around the edges. Figure
            # out which vertex is which.

            common = self.edges[start].end1
            current = self.edges[start].end2

            nextIndex = start + orientation

            if self.edges[nextIndex].hasEnd( common ) :
                common = self.edges[start].end2
                current = self.edges[start].end1


            # Draw the actual triangles of this polygon by going through all
            # the edges from index "nextIndex" to but not including "end,"
            # drawing triangles from the common vertex to the endpoints of each
            # edge.

            while nextIndex != end :

                next = self.edges[nextIndex].oppositeFrom( current )
                renderer.triangle( common.coordinates(), current.coordinates(), next.coordinates(), color )

                current = next
                nextIndex += orientation




    # Write a machine-readable description of this polygon to a stream.
    # Geometric objects in the output have ID numbers, which are managed by
    # an ID manager provided by the caller. See my project notes from August
    # 17, 21, and 22, 2023 for more on why I want to be able to write objects
    # to streams, how I do it, and the format of the resulting files.

    def write( self, stream, ids ) :

        # Output always starts by identifying this geometry as a polygon.
        stream.write( "[Polygon " )

        # If this polygon is already known to the ID manager, just write its ID
        # number and I'm done.
        if ( ids.contains( self ) ) :
            stream.write( "{}]\n".format( ids.find(self) ) )

        else :
            # Otherwise, give this polygon an ID and write it to the stream in
            # detail.

            id = ids.next()
            ids.store( self, id )
            stream.write( "{} ".format(id) )

            listWrite( self.edges, stream, ids )
            safeWrite( self.front, stream, ids )
            safeWrite( self.back, stream, ids )
            safeWrite( self.splitterEdge, stream, ids )

            stream.write( "]\n" )




# Insert an edge into a list of edges in such a way that the list becomes a
# closed loop of edges, i.e., a list that could define a polygon. Return the
# resulting list. If there's nowhere to insert the new edge that creates a
# closed loop, raise a ValueError exception.

def insertEdge( newEdge, edgeList ) :


    # Treating the list as circular, go through each position in it looking for
    # one where either end of the new edge appears, with the other end in the
    # next position.

    for i in range( len(edgeList) ) :

        next = ( i + 1 ) % len(edgeList)

        if    ( edgeList[i].hasEnd( newEdge.end1 ) and edgeList[next].hasEnd( newEdge.end2 ) ) \
           or ( edgeList[i].hasEnd( newEdge.end2 ) and edgeList[next].hasEnd( newEdge.end1 ) ) :
            return edgeList[ : i+1 ] + [newEdge] + edgeList[ i+1 : ]


    # If I made it through the preceeding search without returning, there must
    # not be anywhere I can insert the new edge.

    raise ValueError( "No insertion point" )




# Determine whether an edge is collinear (to within some tolerance) with one of
# its neighbors in a list of edges proposed for making a polygon. Return True
# if so, and False if not.

def nearCollinear( e, edges ) :


    # Find the edge in question and its neighbors.

    pos = edges.index( e )
    previous = (pos - 1) % len(edges)
    next = (pos + 1) % len(edges)


    # Check collinearity.

    collinearityBound = 0.03                   # Parallelism measures less than this count as collinear

    return    edges[previous].parallelism( e ) < collinearityBound \
           or e.parallelism( edges[next] ) < collinearityBound




# Given that some polygon lies entirely in front or in back of some plane,
# figure out from the splitter edges reported by attempts to split the polygon
# with the plane whether one of those splitters, or possibly a common parent of
# them, lies in the plane. Return the edge that is in the plane, or None if
# there isn't one.

def planeEdge( frontSplitter, backSplitter ) :


    # Since the splitters come from attempts to split the polygon in question
    # with the plane in question, they already reflect an analysis of how the
    # polygon and plane interact. All this function has to do is see which if
    # either of them exist.

    if frontSplitter is None :
        return backSplitter

    elif backSplitter is None :
        return frontSplitter

    else :
        common = frontSplitter.commonParent( backSplitter )
        if common is not None :
            return common
        else :
            raise ValueError( "Splitters don't fit any pattern known to planeEdge" )




# An alternative way of creating a polygon, namely by making it already split.
# Clients provide front and back polygons, and a splitter edge, for the split;
# this function figures out from there how to build the polygon, which it
# returns.

def makeSplitPolygon( newFront, newBack, newSplitter ) :


    # Get the back polygon's edge list, making sure that it's oriented
    # consistently with the front polygon.

    backEdges = newBack.edges.copy()

    if dot3( newFront.getNormal(1), newBack.getNormal(1) ) < 0.0 :
        backEdges.reverse()


    # Build a list of edges for the new polygon -- the edges from the front
    # polygon, with the splitter edge replaced by splicing in all edges
    # (except the splitter) of the back.

    frontI = newFront.edges.index( newSplitter )
    backI = backEdges.index( newSplitter )

    newEdges = []
    for e in newFront.edges[ : frontI ] + backEdges[ backI+1 : ] + backEdges[ : backI ] + newFront.edges[ frontI+1 : ] :
        newEdges = e.hoistInto( newEdges )

    newEdges = checkEndParents( newEdges )


    # Build the result from the list of edges, and the given information about
    # the split.

    newPolygon = Polygon( newEdges )

    newPolygon.front = newFront
    newPolygon.back = newBack
    newPolygon.splitterEdge = newSplitter

    return newPolygon
