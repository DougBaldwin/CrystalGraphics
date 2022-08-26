# A class that represents substrates for crystal aggregates to "grow" on. These
# substrates are rectangular blocks of dull rock; clients specify the block's
# bounds in the X, Y, and Z dimensions, so substrates can be any size, but are
# always aligned with the axes.
#
# This class is part of my attempt to generate realistic amethyst aggregates by
# sampling crystal sizes from an appropriate probability distribution. See the
# project notes for more on this project.

# Copyright (C) 2022 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2022. Created by Doug Baldwin from an older version that used a simpler representation of polyhedra.
#
#   June 2021. Original created by Doug Baldwin.




from Polyhedron import Polyhedron
from Vertex import Vertex




class Substrate ( Polyhedron ) :
	
	
	
	
	# Initialize a substrate from its bounds in each of the 3 dimensions. The
	# first bound in each dimension should be the lower one.
	
	def __init__( self, lowX, highX, lowY, highY, lowZ, highZ ) :
		

		# Build a list of this substrate's vertices.

		vertices = [ Vertex( lowX, lowY, highZ ),				# 0: Left bottom front
					 Vertex( lowX, lowY, lowZ ),				# 1: Left bottom back
					 Vertex( lowX, highY, highZ ),				# 2: Left top front
					 Vertex( lowX, highY, lowZ ),				# 3: Left top back
					 Vertex( highX, lowY, highZ ),				# 4: Right bottom front
					 Vertex( highX, lowY, lowZ ),				# 5: Right bottom back
					 Vertex( highX, highY, highZ ),				# 6: Right top front
					 Vertex( highX, highY, lowZ ) ]				# 7: Right top back


		# List the indices of the vertices that define each face.

		faces = [ [0, 2, 3, 1],							# Left
				  [0, 4, 6, 2],							# Front
				  [4, 5, 7, 6],							# Right
				  [5, 1, 3, 7],							# Back
				  [2, 6, 7, 3],							# Top
				  [0, 1, 5, 4] ]						# Bottom


		# Use the vertices and faces to initialize.

		substrateColor = [0.5, 0.5, 0.52, 1.0, 0.05, 1.0]

		super().__init__( vertices, faces, substrateColor )
