# This program is a tool for testing probability distributions for my crystal
# graphics project. In particular, this program will plot a probability
# distribution, using (for now) a distribution and parameters wired into the
# code.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.


from LogNormalDistribution import LogNormalDistribution
from UniformDistribution import UniformDistribution
import pyglet
from pyglet.gl import *
from math import exp




# A utility function that calculates coordinates in units of pixels, from a
# coordinate in world units. The conversion factor depends on the minimum and
# maximum world coordinates in the dimension at hand, and the pixel size of the
# window in that dimension. I use this calculation when finding coordinates for
# labels I put on the plot's axes.

def pixelCoordinate( worldCoord, worldMin, worldMax, pixelSize ) :
	return int( pixelSize * ( worldCoord - worldMin ) / ( worldMax - worldMin ) )




# A utility function that calculates the length of the tickmarks on the axes,
# given the lowest and highest values the plot attains along the perpendicular
# axis.

def tickLength( low, high ) :
	return ( high - low ) / 30.0;




# Start by building lists of (X,pdf(X)) coordinates from the distribution.
# Keep track of the largest pdf value seen while doing so.

sigma = 1.0
distribution = LogNormalDistribution( sigma )

# distribution = UniformDistribution( 0.0, 2.0 )

lowX = -10.0
highX = 10.0
deltaX = ( highX - lowX ) / 200.0

maxPDF = 0.0

points = []

x = lowX
while x <= highX :
	
	pdf = distribution.pdf( x )
	
	points += [ x, pdf ]
	
	if pdf > maxPDF :
		maxPDF = pdf
	
	x += deltaX

nPoints = len( points ) // 2


# Create a window in which to plot the pdf values against the x values.

windowWidth = 512
windowHeight = 512

window = pyglet.window.Window( windowWidth, windowHeight )


# Define colors for the curve and axes in the plot.

curveColor = [ 0, 0, 255 ]
axisColor = [ 128, 128, 128 ]
labelColor = axisColor + [ 255 ]


# Figure out world coordinate bounds for a plot big enough to show the curve.

lowXBound = -0.05 if lowX >= 0.0 else 1.05 * lowX
highXBound = 1.05 * highX

if maxPDF > 0.0 :
	lowYBound = -0.05 * maxPDF
	highYBound = 1.05 * maxPDF
else :
	lowYBound = -0.05
	highYBound = 0.05


# Define lines that will represent axes in the plot. Each axis has a tick at
# its maximum value.

axisLines = [ lowXBound, 0.0, highXBound, 0.0,					# Line segments for axes
		 	  0.0, lowYBound, 0.0, highYBound,
		 	  highX, 0.0, highX, -tickLength(lowYBound,highYBound),
		 	  -tickLength(lowXBound,highXBound), maxPDF, 0.0, maxPDF ]

nAxisPoints = len( axisLines ) // 2


# Define labels for the ticks at the ends of the axes.

labelFormat = "{:.1f}"
labelSize = 10

yLabelX = pixelCoordinate( 0.0, lowXBound, highXBound, windowWidth ) + 2
yLabelY = pixelCoordinate( maxPDF, lowYBound, highYBound, windowHeight )
yLabel = pyglet.text.Label( labelFormat.format(maxPDF), font_size=labelSize, color=labelColor, x=yLabelX, y=yLabelY )

xLabelX = pixelCoordinate( highX, lowXBound, highXBound, windowWidth ) - 2
xLabelY = pixelCoordinate( 0, lowYBound, highYBound, windowHeight ) + 1
xLabel = pyglet.text.Label( labelFormat.format(highX), font_size=labelSize, color=labelColor, x=xLabelX, y=xLabelY, anchor_x='center' )


# The window's "on_draw" callback does the actual plotting.

@window.event
def on_draw() :

	glClearColor( 0.9, 0.9, 0.9, 1.0 )
	glClear( GL_COLOR_BUFFER_BIT )
	
	xLabel.draw()
	yLabel.draw()
	
	glMatrixMode( GL_PROJECTION )
	glLoadIdentity()
	glOrtho( lowXBound, highXBound, lowYBound, highYBound, -1.0, 1.0 )
	
	pyglet.graphics.draw( nPoints, GL_LINE_STRIP, ( "v2f", points ), ( "c3B", curveColor * nPoints ) )
	pyglet.graphics.draw( nAxisPoints, GL_LINES, ( "v2f", axisLines ), ( "c3B", axisColor * nAxisPoints ) )


# Print auxiliary information about the plot.

xMax = exp( -(sigma**2) )
theoreticalMaxPDF = distribution.pdf( xMax )

print( "Theoretical maximum PDF is {} at X = {}".format( theoreticalMaxPDF, xMax ) )
	

# Let the user admire the plot for as long as they want.

pyglet.app.run()
