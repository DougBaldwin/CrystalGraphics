# A collection (probably very small) of functions that do common things in
# Python for which there isn't already a library function.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   August 2022. Created by Doug Baldwin, motivated by a need for some way to
#     draw an arbitrary element out of a set.




# Return an arbitrary element from an Iterable, typically but not necessarily
# a set. Raise a StopIteration exception if the argument is empty.

def pickElement( sequence ) :

    return next( iter(sequence) )




# Return the reversal of a sequence, without changing the sequence itself (the
# opposite of list.reverse(), which modifies the list and doesn't return
# anything).

def reverseSeq( sequence ) :

    return sequence[ : : -1 ]
