#version 120
// A vertex shader for programs that use OpenGL to draw crystals or aggregates. This
// shader work with a matching fragment shader to provide Phong shaded renderings of
// translucent objects.

// Copyright (C) 2016 by Doug Baldwin.
// This work is licensed under a Creative Commons Attribution 4.0 International License
// (https://creativecommons.org/licenses/by/4.0/)




// Data clients provide about each vertex:

attribute vec3 vertexPosition;					// (x,y,z) coordinates of vertex
attribute vec3 vertexNormal;					// Normal vector
attribute vec4 vertexColor;						// Coefficients of diffuse reflection and alpha
attribute float ks;								// Coefficient of specular reflection
attribute float shine;							// Shininess exponent


// Clients provide this shader with a single matrix that does all modeling, viewing,
// and projection transformations.

uniform mat4 viewProjection;



// Finally, the vertex shader gets the viewer's position from the client.

uniform vec3 viewerPosition;


// Information passed to the fragment shader.

varying vec3 normal;					// Normal vector
varying vec4 fragmentColor;				// (R,G,B) coefficients of diffuse reflection, and alpha
varying float fragmentKs;				// Coefficient of specular reflection
varying float fragmentShine;			// Shininess exponent
varying vec3 viewerVector;				// Unit vector pointing towards viewer




// This shader transforms vertices from the global coordinate system into clipping
// coordinates. It then passes color information and normals on to the fragment shader.

void main() {

	gl_Position = viewProjection * vec4( vertexPosition, 1.0 );
	
	viewerVector = normalize( viewerPosition - vertexPosition );
	
	normal = vertexNormal;
	
	fragmentColor = vertexColor;
	fragmentKs = ks;
	fragmentShine = shine;
}
