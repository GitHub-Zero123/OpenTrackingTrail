// __multiversion__
// This signals the loading code to prepend either #version 100 or #version 300 es as apropriate.
precision highp float;


#include "uniformExtraVectorConstants.h"
#include "fragmentVersionCentroidUV.h"
#include "uniformEntityConstants.h"
#include "uniformPerFrameConstants.h"


#include "uniformShaderConstants.h"
#include "util.h"

LAYOUT_BINDING(0) uniform sampler2D TEXTURE_0;
LAYOUT_BINDING(1) uniform sampler2D TEXTURE_1;

varying vec4 light;
varying vec4 fogColor;


void main()
{

	float last_progress = float(int(EXTRA_VECTOR1.w))*0.01f;

	float target_progress = EXTRA_VECTOR1.w-float(int(EXTRA_VECTOR1.w));

	vec4 color = texture2D(TEXTURE_0, vec2(1.f-uv.x, mix(last_progress, target_progress, uv.y)));

	if (color.a <= 0.f){
		discard;
	}

	highp vec4 start_color = vec4(floor(EXTRA_VECTOR2.w*0.1f)*0.01f, floor(fract(EXTRA_VECTOR2.w*0.1f)*100.f)*0.01f, fract(fract(EXTRA_VECTOR2.w*0.1f)*100.f), floor(EXTRA_VECTOR4.w)*0.01f);

	highp vec4 end_color = vec4(floor(EXTRA_VECTOR3.w*0.1f)*0.01f, floor(fract(EXTRA_VECTOR3.w*0.1f)*100.f)*0.01f, fract(fract(EXTRA_VECTOR3.w*0.1f)*100.f), fract(EXTRA_VECTOR4.w));
	
	color.rgb *= mix(end_color.rgb, start_color.rgb, mix(last_progress, target_progress, uv.y));

	#ifdef BLOOM
		color.a = 0.05f;
	#else
		color.a *= mix(end_color.a, start_color.a, mix(last_progress, target_progress, uv.y));
	#endif
	
	gl_FragColor = color;
}
