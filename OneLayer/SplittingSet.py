# A class that keeps track of what will eventually be the edges of a polygon
# that splits a polyhedron in two. The class's basic purpose is to accept edges
# incrementally as they are discovered, stitching them together into lists of
# consecutive edges around the polygon, until there's just one list that can be
# given back to the client.

# Copyright (C) 2024 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2024. Created by Doug Baldwin.


from PythonUtilities import reverseSeq




class SplittingSet :




    # Sets of splitting edges may, as they evolve, contain multiple lists of
    # consecutive edges around a splitting polygon. Over time, these lists
    # merge until there is only one, which is a closed loop of edges (at least
    # that's how things work in theory, if clients use this class as intended).
    # I store the lists in dictionary "edgeLists," keyed by the vertices at the
    # beginning and end of the list (so each list appears twice in the
    # dictionary). To make it easy to find starting and ending vertices, I
    # actually store each edge list as a 3-tuple of the form (start edges end)
    # where "start" is the starting vertex for the list, "edges" is the actual
    # list of edges, and "end" is the ending vertex for the list. Finally, if I
    # ever form a closed loop of edges, I also store its tuple under the
    # special key "CLOSED" (the only time a key is a string instead of a
    # vertex).

    CLOSED_KEY = "CLOSED"




    # Initialize a set of splitting edges to be empty.

    def __init__( self ) :

        # All I have to do is make the dictionary of lists of edges empty.
        self.edgeLists = {}




    # Insert a new edge into this splitting set.

    def insert( self, edge ) :


        # Treat the new edge as a one-element list, and try to join it at its
        # first end with something already in the set. If that juntion is a
        # closed loop, then I'm done, otherwise go on to try joining at the
        # second end.

        newList = self.join( (edge.end1, [edge], edge.end2), edge.end1 )

        if newList[0] is newList[2] :
            self.edgeLists[ SplittingSet.CLOSED_KEY ] = newList
            return


        # See if the list resulting from the first join can also join with
        # something already in this set, but this time at the second end of the
        # new edge.

        newList = self.join( newList, edge.end2 )

        if newList[0] is newList[2] :
            self.edgeLists[ SplittingSet.CLOSED_KEY ] = newList

        else :
            self.edgeLists[ newList[0] ] = newList
            self.edgeLists[ newList[2] ] = newList




    # Try to join a given list of edges with something already in this
    # splitting set at a given vertex. That vertex should be one of the
    # endpoints of the new list. The new list should be represented as a
    # 3-tuple, and should not already be in the set. The result will be a copy
    # of the original list if it doesn't join with anything, or the result of
    # appending the new list to the appropriate end of something it does join
    # with. In all cases, the result is also represented as a 3-tuple, and no
    # part of it is still in this splitting set.

    def join( self, newList, vertex ) :


        # Components of the result, which may be modified depending on exactly
        # how the new list and any partner match. Initially I assume there
        # won't be a match and so the result is just the new list.

        startVertex = newList[0]
        edges = newList[1]
        endVertex = newList[2]


        # If the new list does join up with a partner, figure out exactly what
        # the combination looks like.

        partner = self.edgeLists.get( vertex )

        if partner is not None :

            # I'm going to have a result that incorporates this partner list,
            # so no longer need it in the set.
            del self.edgeLists[ partner[0] ]
            del self.edgeLists[ partner[2] ]

            # Based on which end of the new list matches which end of the
            # partner, figure out what the components of the result are.
            if newList[0] is partner[0] :
                startVertex = newList[2]
                edges = reverseSeq( newList[1] ) + partner[1]
                endVertex = partner[2]

            elif newList[0] is partner[2] :
                startVertex = partner[0]
                edges = partner[1] + newList[1]
                endVertex = newList[2]

            elif newList[2] is partner[0] :
                startVertex = newList[0]
                edges = newList[1] + partner[1]
                endVertex = partner[2]

            elif newList[2] is partner[2] :
                startVertex = partner[0]
                edges = partner[1] + reverseSeq( newList[1] )
                endVertex = newList[0]

            else :
                raise ValueError( "SplittingSet.join made junction but not at end of new list" )


        # All done, the parts of the result have all been identified, so put
        # them together and return.

        return ( startVertex, edges, endVertex )





    # Return the only list of edges in this set, raising a ValueError exception
    # if the set doesn't consist of exactly one list.

    def list( self ) :

        try :
            record = self.edgeLists[ SplittingSet.CLOSED_KEY ]
            return record[1]

        except KeyError :
            raise ValueError( "SplittingSet.list doesn't have exactly one closed list" )
