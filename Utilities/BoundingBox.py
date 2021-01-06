# This class represents bounding boxes for a program that models and renders crystals.
# For every crystal modeled, there exists a bounding box surrounding it that represents
# its size.

# Copyright (C) 2018, 2019 by Jimmy Jasinski (jjj4@geneseo.edu) and Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   September 2018 -- Original version created by Jimmy Jasinski.
#
#   February 2019 -- Comments and such extended, code simplified and made more Python
#     3-ish, and tests extended, by Doug Baldwin.


from MathUtilities import nearlyEqual




class BoundingBox :


    # A bounding box is defined by its bounds in the x, y and z directions. Empty bounding
    # boxes have at least one pair of bounds that are both 0. Bounds are stored as member
    # variables posX, negX,..., negZ and posZ.
    
    
    
    #  Initialize a bounding box from its bounds.

    def __init__( self, negXBound, posXBound, negYBound, posYBound, negZBound, posZBound ) :

        # Store the parameters in the corresponding member variables.

        self.negX = negXBound
        self.posX = posXBound
        self.negY = negYBound
        self.posY = posYBound
        self.negZ = negZBound
        self.posZ = posZBound




    # Compare two bounding box's maximum distances in the x, y and z directions in order 
    # to see if they overlap/intersect. Returns a new bounding box that describes the
    # intersection. Note that this might be an empty bounding box if the original two
    # bounding boxes don't overlap.

    def intersect( self, otherBox ) : 

        # Checks if there is an overlap in the x-direction by comparing the bounding boxes.
        # If there is not, the intersection's negX and posX bounds are given a value of 0.

        if ( self.posX <= otherBox.negX or otherBox.posX <= self.negX ) :
            newNegX = 0 
            newPosX = 0
        else :
            newNegX = max( self.negX, otherBox.negX )
            newPosX = min( self.posX, otherBox.posX )

        # Checks if there is an overlap in the y-direction. 

        if ( self.posY <= otherBox.negY or otherBox.posY <= self.negY ) :
            newNegY = 0
            newPosY = 0
        else :
            newNegY = max( self.negY, otherBox.negY )
            newPosY = min( self.posY, otherBox.posY )

        # Checks if there is an overlap in the z-direction.

        if ( self.posZ <= otherBox.negZ or otherBox.posZ <= self.negZ ) :
            newNegZ = 0
            newPosZ = 0
        else :
            newNegZ = max( self.negZ, otherBox.negZ )
            newPosZ = min( self.posZ, otherBox.posZ )
            

        # Create new bounding box representing the overlap.

        return BoundingBox( newNegX, newPosX, newNegY, newPosY, newNegZ, newPosZ )




    # Determines if a bounding box is empty, and returns true or false. A bounding 
    # box is empty if it does not have bounds in at least one direction.

    def isEmpty( self ) :

        if nearlyEqual( self.negX, 0 ) and nearlyEqual( self.posX, 0 ) :
            return True
        elif nearlyEqual( self.negY, 0 ) and nearlyEqual( self.posY, 0 ) :
            return True
        elif nearlyEqual( self.negZ, 0 ) and nearlyEqual( self.posZ, 0 ) :
            return True
        else :
            return False



    # Generate a string representation of this bounding box.

    def __str__( self ) :
    	template =  "Bounding box with bounds: Neg x = {}, Pos x = {}, Neg y = {}, Pos y = {}, Neg z = {}, Pos z = {}."
    	return template.format( self.negX, self.posX, self.negY, self.posY, self.negZ, self.posZ )




# Unit tests. Run this file as a stand-alone program to execute these tests. They won't
# run if you import the file as a module into some other program.

if __name__ == "__main__" :

	
	# Initialize some bounding boxes and find their intersections.
	
	a = BoundingBox( -1, 1, -1, 1, -1, 1)
	b = BoundingBox( 0, 2, -1, 5, 0, 2, )
	c = a.intersect(b)
	print( "Intersection of..." )
	print( a )
	print( b )
	print( "...is" )
	print( c )


	e = BoundingBox( -1, 1, -1, 1, -1, 1)
	f = BoundingBox( 5, 6, -3, -1, 2, 4)
	g = e.intersect(f)
	print()
	print( "Intersection of..." )
	print( e )
	print( f )
	print( "...is" )
	print( g )
	
	
	h = BoundingBox( 0, 2, 0, 3, 0, 4 )
	i = BoundingBox( -1, 1, 5, 6, 2, 6 )
	j = h.intersect( i )
	print()
	print( "Intersection of..." )
	print( h )
	print( i )
	print( "...is" )
	print( j )
	
	
	
	# Check that bounding boxes that should test as empty do, and ones that shouldn't
	# don't.
	
	k = BoundingBox( 0, 0, 0, 0, 0, 0 )
	print()
	print( "Deliberately empty bounding box is empty?", k.isEmpty() )
	print( "Empty intersection is empty?", g.isEmpty() )
	print( "Box empty in some but not all dimensions is empty?", j.isEmpty() )
	print( "Non-empty intersection is empty?", c.isEmpty() )
