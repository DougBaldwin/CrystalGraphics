# Model and render a twinned amethyst crystal.

#Authors: Amelia Mindich and Steven Sicari
#Last Edited: 3/12/2017
# Extended June 21, 2019 by Doug Baldwin to use "-r" command-line option to specify a
#   renderer.

# Copyright 2016 by Steven Sicari and Amelia Mindich (sms40@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/).

from StaticScreenRenderer import StaticScreenRenderer
from RotatingScreenRenderer import RotatingScreenRenderer
from STLRenderer import ASCIISTLRenderer
from VectorOps import scale4H, subtract4, add4
from SymmetryOps import transform4
from math import pi, sin, cos, sqrt
from argparse import ArgumentParser
import sys





# Basic parameters for the crystals.

a = 10
c = 15

material = ( 0.58, 0.3, 0.8, 0.68, 0.85, 50.0 )

topPrismC = 10
topPyramidC = topPrismC + c


# Based on the user's request, create the appropriate renderer to draw the crystal.

parser = ArgumentParser()
parser.add_argument( "-r", action="store", default="rotate", choices=["rotate","static","3d"],
					 help="Specify rendering to a rotating view, static view, or 3d printer file" )

arguments = parser.parse_args()

viewerX = 0.0							# Initial x coordinate for viewer
viewerY = topPyramidC - 15.0			# Initial viewer y coordinate
viewerZ = a + 50.0						# Initial z

if arguments.r == "rotate" :
	renderer = RotatingScreenRenderer( viewerY, sqrt( viewerY**2 + viewerZ**2 ) )

elif arguments.r == "static" :
	renderer =  StaticScreenRenderer()
	renderer.viewer( viewerX, viewerY, viewerZ )


elif arguments.r == "3d" :
	renderer = ASCIISTLRenderer( 'Twin.stl' )

else :
	print( "Renderer '" + arguments.r + "' must be one of 'rotate', 'static', or '3d'" )
	sys.exit( 1 )


# Identify the rendering libraries being used.

print( "Renderer version:", renderer.version() )


# Build the crystals.

topPyramidVertex = [ 0, topPyramidC, 0, 1 ]


topPrismVertices = []
#vertices which will be on the y = 0 plane
joinPrismVertices = []
#normal to top prism vertices
normalToTPV = []

theta = pi / 3						

#generate top prism vertices and a set of normals

for i in range( 6 ) :
	angle = i * theta
	x = a * sin( angle )
	z = a * cos( angle )
	topPrismVertices.append( [ x, topPrismC, z, 1 ] )
	normalToTPV.append( [x, topPrismC - 5, z, 1] )
	


totalPyramidA = [topPyramidVertex] + topPrismVertices  
thetaA = 2*pi - 0.785398

#rotate them about the y axis

CoordinateSysA = [ [cos(thetaA), sin(thetaA), 0, -5], [-sin(thetaA), cos(thetaA), 0, 0], [0,0,1,0], [0,0,0,1] ]
AmethystA = transform4(totalPyramidA, CoordinateSysA )
normalA = transform4(normalToTPV, CoordinateSysA)

#Define the positions of AmethystA based the rotated axis

topPyramidVertexA = AmethystA[0]  
topPrismVerticesA = [ AmethystA[1], AmethystA[2], AmethystA[3], AmethystA[4], AmethystA[5], AmethystA[6] ]

#scale the normal vertices such that they are on the x = 0 plane
#this set of joinprismvertices is replacing "bottomPrismVertices"

for i in range( 6 ):

	AddingVec = subtract4(normalA[i], topPrismVerticesA[i])
	ScaledAddingVec = scale4H(AddingVec, (-topPrismVerticesA[i][0]/AddingVec[0]))
	point = add4(topPrismVerticesA[i], ScaledAddingVec) 
	joinPrismVertices.append(point)


#Generate the Amethyst twin. 

totalPyramidB = [topPyramidVertex] + topPrismVertices 
thetaB = 0.785398

CoordinateSysB = [ [cos(thetaB), sin(thetaB), 0, 5], [-sin(thetaB), cos(thetaB), 0, 0], [0,0,1,0], [0,0,0,1] ]
AmethystB = transform4(totalPyramidB, CoordinateSysB)

	

topPyramidVertexB = AmethystB[0] 
topPrismVerticesB = [ AmethystB[1], AmethystB[2], AmethystB[3], AmethystB[4], AmethystB[5], AmethystB[6] ]

#render one half of the twin

for i in range( 6 ) :
	nextI = ( i + 1 ) % 6
	renderer.triangle( topPyramidVertexA, topPrismVerticesA[i], topPrismVerticesA[nextI], material )
	renderer.triangle( topPrismVerticesA[i], joinPrismVertices[i], topPrismVerticesA[nextI], material )
	renderer.triangle( topPrismVerticesA[nextI], joinPrismVertices[i], joinPrismVertices[nextI], material )
	
#re-order JoinPrismVertices such that it lines up with the other half of the twin	
	
joinPrismVertices = [joinPrismVertices[0], joinPrismVertices[5], joinPrismVertices[4], joinPrismVertices[3], joinPrismVertices[2], joinPrismVertices[1]]
	
#Render the other half	
	
for i in range( 6 ) :
	nextI = ( i + 1 ) % 6
	renderer.triangle( topPyramidVertexB, topPrismVerticesB[i], topPrismVerticesB[nextI], material )
	renderer.triangle( topPrismVerticesB[i], joinPrismVertices[i], topPrismVerticesB[nextI], material )
	renderer.triangle( topPrismVerticesB[nextI], joinPrismVertices[i], joinPrismVertices[nextI], material )
	

	
		
renderer.draw()
