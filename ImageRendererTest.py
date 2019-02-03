# This program is an artificial test of a Python "image renderer" class that is hides the
# complexity of drawing images represented as pixel arrays with Pyglet. This program
# simply draws a set of red-green-blue color bars.

# Copyright (C) 2016 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from ImageRenderer import ImageRenderer




# The main program.

renderer = ImageRenderer()


# Create the color bars. Start with a yellow bar across the top of the image, with
# vertical red (at the left side), green (center), and blue (right) bars below it. This
# pattern allows me to see whether the image is oriented correctly top-to-bottom and
# left-to-right.

bars = [ [ [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0] ],		\
		 [ [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0] ],		\
		 [ [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0], [1,1,0] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ],		\
		 [ [1,0,0], [1,0,0], [1,0,0], [0,1,0], [0,1,0], [0,1,0], [0,0,1], [0,0,1], [0,0,1] ] ]

renderer.image( bars )


# View the color bars.

renderer.draw()