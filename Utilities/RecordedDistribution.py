# A probability "distribution" that replays numbers from a list recorded
# earlier. These distributions are useful in programs that ordinarily work with
# random numbers drawn from certain distributions, but that want to provide an
# option of using a predetermined set of numbers, for instance to replay some
# previous run.

# Copyright (C) 2024 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2024. Created by Doug Baldwin.


from ProbabilityDistribution import ProbabilityDistribution




class RecordedDistribution( ProbabilityDistribution ) :




    # Recorded distributions consider as whitespace most of the characters
    # Python does, but not end-of-line characters.

    SPACES = " \t"




    # Initialize a recorded "distribution" by reading the sequence of numbers
    # it should return from a file. The file should be a text file, each line
    # of which is either a space-separated list of numbers, a comment whose
    # first non-whitespace character is a '#', or blank. This constructor reads
    # from the current file position past any blank lines and comments until it
    # comes to a line of numbers, reads those numbers and any subsequent ones
    # until it comes to a blank line or a comment. This convention of reading
    # from the current position through one group of numbers means that a
    # single file can contain several distributions, useful for "replays" of
    # programs that draw random numbers from multiple distributions. Note that
    # for now, trying to read past the end of a file will silently produce an
    # empty distribution. Someday I might want to raise an exception instead.

    def __init__( self, distributionFile ) :


        # Read past blank lines and comments.

        line = distributionFile.readline()
        while self.isSeparatorLine( line ) :
            line = distributionFile.readline()


        # Now I should have a line of numbers to save for this distribution to
        # eventually return.

        self.samples = []

        while line != "" and not self.isSeparatorLine( line ) :

            for digits in line.split() :
                self.samples.append( float(digits) )

            line = distributionFile.readline()




    # Return the next sample from this "distribution."

    def sample( self ) :


        # Rotate the list of samples one place, putting the value that should
        # be returned at the end of the list.

        self.samples = self.samples[ 1 : ] + [ self.samples[0] ]
        return self.samples[ -1 ]




    # Recorded "distributions" are completely deterministic, and so don't
    # really have PDFs. But since every distribution needs to handle requests
    # for PDF values, say they're always 0.

    def pdf( self, x ) :
        return 0.0




    # A utility method that checks to see if a string from a file represents
    # a line that should be treated as separating distributions or not. This
    # returns True if the line is a separator and False if not.

    def isSeparatorLine( self, line ) :


        # A separator is a non-empty line that's either all whitespace, or a
        # comment after any leading whitespace.

        strippedLine = line.lstrip( RecordedDistribution.SPACES )
        return strippedLine != "" and ( strippedLine == "\n" or strippedLine[0] == "#" )
