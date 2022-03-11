// Generated using the superior demo tool of Team210.

#version 450

layout (location=0) uniform float iTime;
layout (location=1) uniform vec2 iResolution;
layout (location=2) uniform int iFrame;
layout (location=3) uniform sampler2D iChannel0;
layout (location=4) uniform sampler2D iChannel1;
layout (location=5) uniform sampler2D iChannel2;
layout (location=6) uniform sampler2D iChannel3;
layout (location=7) uniform int iPass;
layout (location=8) uniform float iGlobalTime;
layout (location=9) uniform float iTimeDelta;

out vec4 out_color;

${COMMON_SOURCE}

${PASS_SOURCES}

void main()
{
	${PASS_INVOCATIONS}
}
