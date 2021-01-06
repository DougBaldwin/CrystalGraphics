# A class that represents an entire amethyst aggregate, including its rock substrate, in
# a program that generates and displays such aggregates. The overall program works by
# simulating the growth of the crystals in the aggregate, including any eventual
# collisions with each other, overlappings, etc. See my project notes from June 13 - 17,
# 2019 for more about this program and the ideas underlying it. This class provides a
# way to collect all the objects needed to represent an aggregate together, along with
# the algorithms for making the aggregate as a whole grow and decomposing it into
# triangles for drawing.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   June 2019. Created by Doug Baldwin.


from HashAreaMap import HashAreaMap
from Amethyst import Amethyst
from Substrate import Substrate
from operator import attrgetter




class AmethystAggregate :
	
	
	
	
	# Aggregates describe their crystals, substrate, etc. via the following attributes:
	#   simulationTime - This class simulates the aggregate growing over time, where time
	#     is measured in discrete steps. This attribute records the current time for this
	#     aggregate.
	#   growTime - The number of simulated time steps the aggregate should spend growing.
	#     After this many steps, the crystals in the aggregate stop expanding.
	#   substrate - The substrate on which the crystals grow.
	#   crystals - A list of the individual amethyst crystals in this aggregate.
	#   pendingCrystals - A list of specifications for crystals to be created some time
	#     in the future. Specifications leave this list and generate actual crystals in
	#     the "crystals" attribute as clients call the "createCrystals" method while
	#     simulated time advances. This list is sorted in increasing order by creation
	#     time, measured in simulation steps. Each specification is itself a list
	#     containing the crystal's x and z coordinates, azimuth and polar angles, and
	#     scheduled creation time.
	#   regions - An area map that records which components of the aggregate occupy which
	#     regions in the plane at the top of the substrate.
	#   log - A logger in which to record any interesting history of the aggregate.
	
	
	
	
	# Class-wide constants that describe the  bounds of the substrate on which to create
	# the aggregate. The X and Z bounds are also effectively the limits of the "world"
	# that the aggregate knows about.
	
	MIN_X = -1.0
	MAX_X = 1.0
	MIN_Z = -1.0
	MAX_Z = 1.0
	TOP_Y = 0.5


	
	
	# Initialize an amethyst aggregate from a list of positions and orientations for
	# crystals it should grow, the amount of simulated time it should grow for, and a
	# logger in which to record anything about the growth process that developers want to
	# preserve.
	
	def __init__( self, crystalSpecs, growTime, log ) :


		# Remember this aggregate's growing time, logger, etc.
		
		self.growTime = growTime
		self.log = log


		# Create the area map in which everything else's location will be recorded.
 
		self.regions = HashAreaMap( AmethystAggregate.MIN_X, AmethystAggregate.MAX_X, AmethystAggregate.MIN_Z, AmethystAggregate.MAX_Z )
 
 
		# Create the substrate everything else grows on.
 
		self.substrate = Substrate( AmethystAggregate.MIN_X, AmethystAggregate.MAX_X,
									0.0, AmethystAggregate.TOP_Y,
									AmethystAggregate.MIN_Z, AmethystAggregate.MAX_Z )
 
		self.regions.insert( self.substrate )
 
 
		# Crystals don't necessarily get created now, unless they have creation times of
		# 0. Rather, the specifications get stored in a list of pending crystals, sorted
		# in increasing order by creation time, and then the actual creations happen
 
		self.crystals = []
		
		self.pendingCrystals = sorted( crystalSpecs, key=attrgetter("t") )
		self.simulationTime = 0
		self.createCrystals()					# Create any crystals scheduled for the dawn of time
	
	
	
	
	# Cause the crystals in an aggregate to carry out one step of simulated growth. Each
	# such step expands each crystal slightly, and then checks to see if any crystals
	# need to stop growing in particular directions due to overlaps with neighbors. This
	# method therefore modifies the crystals in an aggregate, but has no explicit return
	# value.
	
	def grow( self ) :
		
		
		# No growth happens at all if the aggregate has been around long enough to finish
		# its growing phase.
		
		if self.simulationTime < self.growTime :
		
		
			# Crystal growth is a 2-phase process: first increase the size of every crystal,
			# and then see how, if at all, the new sizes affect overlaps between crystals.
			# The 2 phases makes checking for overlaps simpler, because after all crystals
			# have grown I can simply check each crystal to see what parts of it are engulfed
			# by other crystals, whereas if I checked as growth was happening I'd have to do
			# that check, plus checking all the neighbors of newly expanded crystals to see
			# if they had been engulfed.
		
			# Start by having each crystal grow. Growing includes telling the area map
			# about the crystal's new size.
		
			DR = 0.01							# How much to push planes outward by
		
			for c in self.crystals :
			
				oldBounds = c.xzBounds()
				c.grow( DR )
				self.regions.grow( c, oldBounds.minX, oldBounds.maxX, oldBounds.minZ, oldBounds.maxZ )
		
		
			# Update overlaps.
		
			for c in self.crystals :
				c.updateOverlaps( self.regions.neighbors(c) )
			
		
		# Increment simulated time and create any new crystals scheduled for the new time.
		
		self.simulationTime += 1
		self.createCrystals()
	
	
	
	
	# Draw an aggregate to a renderer, i.e., add the triangles forming the surface of
	# the aggregate's crystals and substrate to the renderer. Note that it's the client's
	# job to later tell the renderer to truly display those triangles on some device. This
	# method modifies the renderer, but has no explicit return value.
	
	def draw( self, renderer ) :
		
		
		# Triangulate the substrate without regard to anything that intersects it, and
		# add all the resulting triangles to the renderer.
		
		# for tri in self.substrate.coarseTriangles() :
		#	renderer.triangle( tri.v1, tri.v2, tri.v3, Substrate.COLOR )
		
		
		# Triangulate each crystal in the aggregate with attention to intersections, so
		# that only triangles on the exposed surface of the crystals get added.
		
		for crystal in self.crystals :
			for tri in crystal.fineTriangles( self.regions.neighbors( crystal ) ) :
				# print( "AmethystAggregate.draw rendering crystal triangle", tri.v1, tri.v2, tri.v3 )
				renderer.triangle( tri.v1, tri.v2, tri.v3, Amethyst.COLOR )
		
		# print( "AmethystAggregate.draw finished" )
	
	
	
	
	# Create any crystals scheduled for times at or before this aggregate's current
	# simulation time. This potentially modifies the aggregate's lists of actual and
	# pending crystals, but has no explicit return value.
	
	def createCrystals( self ) :
		
		
		# Pull everything that has a scheduled time less than or equal to the current
		# simulation time off the pending crystals list, and add the corresponding crystal
		# to the actual crystals list.
		
		while self.pendingCrystals and self.pendingCrystals[0].t <= self.simulationTime :
			
			spec = self.pendingCrystals.pop( 0 )
			newCrystal = Amethyst( spec.x, AmethystAggregate.TOP_Y, spec.z, spec.theta, spec.phi )
			
			self.regions.insert( newCrystal )
			self.crystals.append( newCrystal )
		