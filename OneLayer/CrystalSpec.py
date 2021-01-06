# A record class that provides specifications for crystals to be created by a program
# that simulates the growth of a crystal aggregate. In particular, programs that can use
# these specifications need to know the position and orientation of each crystal on a
# plane, and a simulated time at which to create that crystal. See my crystals project
# notes from June 2019 for a description and design for such a program.

# Copyright (C) 2019 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2019. Created by Doug Baldwin.




class CrystalSpec :
	
	
	
	
	# As a record class, CrystalSpecs' attributes are intended for clients to access
	# directly. Thos attributes are...
	#   x - The x coordinate at which to create this crystal.
	#   z - The z (or any other dimension clients like perpendicular to x) coordinate at
	#     which to create this crystal.
	#   theta - The azimuth angle with which to create this crystal.
	#   phi - The polar angle with which to create this crystal.
	#   t - The time at which to create this crystal.
	
	
	
	
	# Initialize a crystal specification from its x and z position, azimuth and polar
	# angles, and creation time.
	
	def __init__( self, x, z, azimuth, polar, time ) :
		
		self.x = x
		self.z = z
		self.theta = azimuth
		self.phi = polar
		self.t = time
