# A class that represents general polyhedra for my attempt to draw realistic
# amethyst aggregates as sets of clipped crystals with sizes taken from a
# realistic probability distribution. I represent a general polyhedron as a
# union of convex ones. See my design notes from 2021 for more on this project
# in general.

# Copyright (C) 2021 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2021. Created by Doug Baldwin.




class Polyhedron :
	
	
	
	
	# I represent general polyhedra as a list of their constituent convex
	# polyhedra.
	
	
	
	
	# Initialize a polyhedron with a list of the convex polyhedra that form it.
	
	def __init__( self, components ) :
		
		self.polyhedra = components
	
	
	
	
	# Determine whether this polyhedron contains a point or not. Return True
	# if so, and False if not.
	
	def contains( self, point ) :
		
		
		# This polyhedron contains the point if any of its constituent convex
		# polyhedra do.
		
		for convex in self.polyhedra :
			if convex.contains( point ) :
				return True
		
		return False
	
	
	
	
	# Clip this polyhedron so that it contains only the parts that are outside
	# of a given other polyhedron. The result is to change the polyhedron being
	# clipped.
	
	def clipTo( self, other ):
		
		
		# To clip a general polyhedron, clip each of its convex components,
		# against each convex component in the other polyhedron. Each step in
		# this clipping might produce a new set of components.
		
		oldComponents = self.polyhedra
		
		for clipper in other.polyhedra :
		
			newComponents = []
		
			for component in oldComponents :
				newComponents += component.clipTo( clipper )
		
			oldComponents = newComponents
		
		self.polyhedra = oldComponents
	
	
	
	
	# Draw this polyhedron to a renderer. In other words, tell the renderer
	# about this polyhedron's triangles; actual display on screen (or
	# elsewhere) will happen later.
	
	def draw( self, renderer ) :
		
		
		# For now, just draw each component convex polyhedron individually.
		# Eventually, polyhedra might look better if I'm careful not to draw
		# faces from component polyhedra that are actually inside the overall
		# polyhedron, or that coincide with faces I've already drawn.
		
		for component in self.polyhedra :
			component.draw( renderer )
