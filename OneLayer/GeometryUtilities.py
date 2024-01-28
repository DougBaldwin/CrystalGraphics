# A collection of utility functions that work with geometric objects from my
# single-layer crystal aggregate program. These functions work with multiple,
# or even all, kinds of geometry, and so don't belong in any particular
# geometry class.

# Copyright (C) 2023 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International
# License (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   August 2023 -- Created by Doug Baldwin.




# Functions that help me write geometry objects into streams, as described in
# my August 17, 21, and 22, 2023 project notes.

# Check that an object actually exists before trying to write it to a stream.
# If the object is None, write that to the stream.

def safeWrite( obj, stream, ids ) :

    if obj is not None :
        obj.write( stream, ids )
    else :
        stream.write( "None " )




# Write a list of geometry objects to a stream. Assume that all of the elements
# of the list are actual geometric objects.

def listWrite( elements, stream, ids ) :

    stream.write( "[List " )

    for e in elements:
        e.write( stream, ids )

    stream.write( "] " )
