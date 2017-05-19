# Part of a hierarchy of Python classes that render crystals or crystal aggregates to
# various output devices. This class writes the crystal into STL file format for 3D printing.
# STL files represent physical objects as multiple triangles in 3D space, These triangles will
# often share 2 vertices.  for the "triangle" method it is intuitive that  triangles can be
# written directly into an STL file format, if we desire to add other shapes, we will have to
# perform triangle tessellation on them before they can be written into the STL file. 

#Author: Steven Sicari
#Last Modified: 2/7/2017

# Copyright 2017 by Steven Sicari (sms40@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/).


from Renderer import Renderer
from VectorOps import subtract3, cross, normalize3

#The STL file writer class, includes "ASCII" in name in case we need a boolean Renderer in the future

class ASCIISTLRenderer(Renderer):




	#Initialize an ASCII STL Renderer.
	
	def __init__( self, string ):
	
		#Establish title text for the STL file
		
		self.stl = "solid crystal \n"
		
		#string is what the file is stored as the string input must 
		#be "__samplefilename__.stl" or else it will not be saved as an STL file
		
		self.string = string
		
		#Initialize an empty file that the STL Renderer will write into
		
		self.result = file(self.string,'w')
		
		
		
		
	#"triangle" adds triangle components to the stl string 
		
	def triangle( self, v1, v2, v3, material ) :
	
		#store normal to triangle
		
		normal = normalize3( cross( subtract3( v3, v2 ), subtract3( v1, v2 ) ) )
		
		#input normal and 3 vertex coordinates into STL format
		
		self.stl = self.stl + "		  facet normal %f %f %f \n "%(normal[0], normal[1], normal [2])
		self.stl = self.stl + "			outer loop \n" 
		self.stl = self.stl + "			  vertex %f %f %f \n"%(v1[0], v1[1], v1[2])
		self.stl = self.stl + "			  vertex %f %f %f \n"%(v2[0], v2[1], v2[2])
		self.stl = self.stl + "			  vertex %f %f %f \n"%(v3[0], v3[1], v3[2])
		self.stl = self.stl + "			endloop \n"
		self.stl = self.stl + "		  endfacet\n"
		
		
	
		
	#draw writes the string which has been built by "triangle" into the .stl file	
		
	def draw( self ):
	
		#add a final line "endsolid" which tells the file that it has no more triangles to read in
		
		self.stl = self.stl + "		endsolid"
		
		#write the string into the STL file
		
		self.result.write(self.stl)
	
	
		
		
	def version( self ):
		return "STL writer in an ASCII format"