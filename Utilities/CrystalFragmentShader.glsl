#version 120
// A fragment shader for programs that use OpenGL to render crystals or aggregates.

// Copyright (C) 2016 by Doug Baldwin.
// This work is licensed under a Creative Commons Attribution 4.0 International License
// (https://creativecommons.org/licenses/by/4.0/)


// This shader uses a simple lighting model, consisting of 4 white light sources (some of
// which may be turned off by having 0 intensity) and ambient light. Each light source is
// infinitely far from the scene. Clients must provide some ambient light intensity and
// directions (non-0) and intensities for each light source. Intensities should range
// between 0 and 1, and directions should be unit vectors in global coordinates.

uniform float ambientIntensity;					// Ambient light intensity

const int nLights = 4;							// Number of lights
uniform vec3 lightDirections[ nLights ];		// Directions to lights
uniform float lightIntensities[ nLights ];		// Intensities of lights


// Clients tell this shader which face(s) to draw by setting the following variable to...
//   1 - Draw front faces
//   2 - Draw back faces
//   3 - Draw all faces
// Any other value causes the shader to draw no faces.

uniform int whichFaces;
const int FRONT = 1;
const int BACK = 2;
const int BOTH = 3;


// Inputs to this shader that come directly from the vertex shader. Note that the normal
// and viewer vectors are still in global coordinates.

varying vec3 normal;					// Unit normal to surface
varying vec3 viewerVector;				// Unit vector pointing towards viewer

varying vec4 fragmentColor;				// Coefficients of diffuse reflection and alpha
varying float fragmentKs;				// Coefficient of specular reflection
varying float fragmentShine;			// Shininess exponent


// This shader's main job is to carry out the lighting calculations that determine the
// color of each fragment. Note that the "color" passed from the vertex shader is actually
// coefficients of red, green, and blue reflection and an alpha value.

void main() {


	// Check to see if this fragment should be drawn at all, according to whether I'm
	// drawing all faces or only front or back faces. Note that a fragment is front-facing
	// if its normal points generally towards the viewer, and back-facing if the normal
	// points generally away from the viewer.
	
	bool front = dot( normal, viewerVector ) >= 0.0;
	
	if (    ( whichFaces == FRONT && front )
		 || ( whichFaces == BACK && !front )
		 || whichFaces == BOTH  ) {


		// If this fragment comes from the back of a surface, then use the reverse of that
		// surface's normal in lighting calculations and attenuate light reaching the
		// surface (since the visible face of the surface is inside the crystal).
	
		vec3 effectiveNormal;
		float attenuation;
	
		if ( front ) {
			effectiveNormal = normal;
			attenuation = 1.0;
		}
		else {
			effectiveNormal = -normal;
			attenuation = 1.0 - fragmentColor.a;
		}


		// Fragment color is a base color due to ambient light plus the sum of the diffuse
		// and specular contributions from each light source.
	
		vec3 baseColor = ambientIntensity * fragmentColor.rgb;
	
		for ( int i = 0; i < nLights; ++i ) {
			float cosineLightAngle = dot( effectiveNormal, lightDirections[i] );
			if ( cosineLightAngle > 0.0 ) {
				baseColor = baseColor +   lightIntensities[i]
										* attenuation
										* cosineLightAngle
										* fragmentColor.rgb;
				vec3 reflectionVector = normalize( 2.0 * cosineLightAngle * effectiveNormal - lightDirections[i] );
				float cosineViewerAngle = max( dot( reflectionVector, viewerVector ), 0.0 );
				baseColor = baseColor +   lightIntensities[i]
										* attenuation
										* pow( cosineViewerAngle, fragmentShine )
										* fragmentKs;
			}
		}

		gl_FragColor = vec4( baseColor, fragmentColor.a );
	}
	else {
		discard;
	}
}
