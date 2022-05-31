# Python definitions that help clients work with OpenGL via Pyglet.		

# Copyright (C) 2016 by Doug Baldwin.
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (https://creativecommons.org/licenses/by/4.0/)


from pyglet.gl import *
from ctypes import POINTER, pointer, create_string_buffer





# A class that represents exceptions encountered while working with OpenGL. This class
# exists so that GL-related errors can be signalled by instances of it, but it provides
# no functionality beyond what it inherits.

class GLError ( Exception ) :
	pass




# Read the source code of a shader from a file, given the file name relative to the
# current directory. This function returns the shader source code, as a single string,
# or raises an IOError exception if it can't find the requested file.

def readShader( fileName ) :

	sourceFile = open( fileName )
	code = sourceFile.read()
	sourceFile.close()
	
	return code




# Compile a shader, and return the resulting shader ID. The arguments are a string
# containing the shader's source code and the type of shader being compiled (either
# GL_VERTEX_SHADER or GL_FRAGMENT_SHADER). If anything goes wrong while compiling the
# shader, this raises a GLError exception containing a string that describes the
# problem.

def compileShader( source, type ) :
	
	
	# Attaching source code to a shader requires a pointer to a pointer to the beginning
	# of the first string of that code. In this case it's a pointer to a pointer to the
	# first character of a C string containing the "source" parameter.
	
	sourceCString = pythonStringToGLString( source )
	sourcePtr = (POINTER(GLchar))( sourceCString )
	sourcePtrPtr = pointer( sourcePtr )
	
	
	# I'll also need a null pointer in place of a pointer to an array of integer lengths of
	# source lines.
	
	NULL = (POINTER(GLint))()
	
	
	# With all the above pointers, I can actually compile the source code into a shader.
	
	id = glCreateShader( type )
	glShaderSource( id, 1, sourcePtrPtr, NULL )
	glCompileShader( id )
	
	
	# Raise an exception if compilation failed, otherwise return the shader's ID.
	
	abortOnShaderError( id, SHADER )
	return id




# Check for errors in compiling a shader or linking a shader program. Parameters to this
# function are the ID of the shader or program, and a flag whose value is the constant
# SHADER if checking compilation status for a shader or PROGRAM if checking link status
# for a program. This function raises a GLError exception containing the error string as
# its only argument if it detects an error, otherwise it returns normally (so calling
# this function is really a conditional abort-if-error control flow operation).

SHADER = 1
PROGRAM = 2

def abortOnShaderError( id, type ) :
	
	
	# Check overall status to see if there's an error.
	
	successFlag = GLint( 0 )
	successPtr = pointer( successFlag )
	
	if type == SHADER :
		glGetShaderiv( id, GL_COMPILE_STATUS, successPtr )
	else :
		glGetProgramiv( id, GL_LINK_STATUS, successPtr )
	
	if not successFlag.value :
		
		
		# There is an error, so get its description.
		
		msgLength = GLint( 0 )
		lengthPtr = pointer( msgLength )
		
		if type == SHADER :
			glGetShaderiv( id, GL_INFO_LOG_LENGTH, lengthPtr )
		else :
			glGetProgramiv( id, GL_INFO_LOG_LENGTH, lengthPtr )
		
		errorMessage = create_string_buffer( msgLength.value )
		errorMessagePtr = ( POINTER(GLchar) )( errorMessage )
		NULL = (POINTER(GLint))()
		
		if type == SHADER :
			glGetShaderInfoLog( id, msgLength, NULL, errorMessagePtr )
		else :
			glGetProgramInfoLog( id, msgLength, NULL, errorMessagePtr )
		
		raise GLError( errorMessage.value )




# Find and return the shader location associated with a uniform variable. Arguments to
# this function are the ID for a shader program, and a Python string containing the name
# of the desired variable.

def getUniformLocation( program, variable ) :
	
	
	# Build a C string from the variable name, and use it to get the location.
	
	cName = pythonStringToGLString( variable )
	cNamePtr = ( POINTER(GLchar) )( cName )
	
	return glGetUniformLocation( program, cNamePtr )




# Find and return the index bound to a specified generic attribute in a specified shader
# program.

def getAttributeIndex( programID, attributeName ) :
	
	
	# Build a C string from the attribute name, and give it to OpenGL to find the index.
	
	cName = pythonStringToGLString( attributeName )
	cNamePtr = ( POINTER(GLchar) )( cName )
	
	return glGetAttribLocation( programID, cNamePtr )




# Convert a raw C string (i.e., a pointer to a null-terminated array of bytes) to a
# Python string.

def CStringToPython( bytes ) :
	
	
	# Step through the bytes, converting each to a character and appending it to the
	# result, until the null end-of-string marker.
	
	pythonString = ""
	c = 0
	while bytes[c] != 0 :
		pythonString = pythonString + chr( bytes[c] )
		c = c + 1
	
	return pythonString




# Convert a Python string to a whatever sort of C string OpenGL wants, i.e., a null-
# terminated array of GLchar values. At the moment (February 2019, working with OpenGL
# 2.1), this seems to mean an array of single bytes. Clients should be able to use this
# function on any string made up of symbols from the first 256 Unicode codepoints.

def pythonStringToGLString( chars ) :
	
	# Encode the Python string of Unicode characters into a Python byte sequence, and
	# then turn that into a C string. I use ISO-8859-1 to encode unicode into bytes
	# because it can encode all of the first 256 unicode codepoints into bytes (unlike,
	# say, UTF-8, which would encode 128 codepoints as single bytes and use multiple
	# bytes for the rest).
	
	return create_string_buffer( chars.encode("ISO-8859-1") )
