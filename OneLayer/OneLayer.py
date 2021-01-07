# The  driver for a program that generates and displays crystal aggregates consisting of a
# single layer of crystals on a rock substrate. The central idea is to try to get a
# visually plausible distribution of crystal sizes by picking those sizes from a
# probability distribution that crystals are really believed to follow, in this case a
# lognormal one. See my project notes from late December 2020 and early January 2021 for
# more about this idea.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   January 2021. Created by Doug Baldwin. Despite being part of a series of programs that
#     draw single-layer amethyst aggregates, this file doesn't substantially draw on
#     previous programs in that series.


# Just announce that the program is running without building an aggregate.

print( "OneLayer program not generating an aggregate from a lognormal distribution." )
