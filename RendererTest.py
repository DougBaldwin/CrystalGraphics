# This program is an artificial test of a Python "renderer" class that is supposed to
# hide the complexity of drawing crystals and crystal aggregates with Pyglet. The program
# simply draws a handful of triangles and views them in simple ways intended to make it
# easy to tell whether the renderer is doing what it should, and if not, to figure out
# why.

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from SimpleScreenRenderer import SimpleScreenRenderer




# The main program.

renderer = SimpleScreenRenderer()


# Create a pair of triangles that should display upward-angled sides when rendered in
# proper perspective, with a dark triangle showing through from behind them.

leftColor = [ 1.0, 0.0, 0.0, 0.3, 0.5, 1.0 ]
rightColor = [ 0.0, 0.0, 1.0, 0.3, 0.5, 1.0 ]
backColor = [ 0.0, 0.7, 0.0, 1.0, 0.5, 1.0 ]

bottomCenter = [ 0.0, -0.5, 0.0 ]
topCenter = [ 0.0, 0.5, 0.0 ]
leftCorner = [ -0.5, -0.5, -0.75 ]
rightCorner = [ 0.5, -0.5, -0.75 ]
backTopLeft = [ -0.7, 0.3, -0.8 ]
backBottomLeft = [ -0.7, -0.3, -0.8 ]
backRight = [ 0.7, 0.0, -0.8 ]

renderer.triangle( backTopLeft, backRight, backBottomLeft, backColor )
renderer.triangle( bottomCenter, topCenter, leftCorner, leftColor )
renderer.triangle( bottomCenter, rightCorner, topCenter, rightColor )


# View those triangles.

renderer.viewer( 0.0, 0.0, 2.0 )
renderer.draw()