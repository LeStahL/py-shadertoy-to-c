// Generated using the superior demo tool of Team210.

#pragma once

#include "${NAME}_min.h"

GLint program_${NAME};

// Compile the shader program.
// Call this before the demo (when the progress bar is shown).
void setUp_${NAME}()
{
	program_${NAME} = ((PFNGLCREATESHADERPROGRAMVPROC)wglGetProcAddress("glCreateShaderProgramv"))(GL_FRAGMENT_SHADER, 1, &${NAME}_frag);
}

// Set up for each pass. Sets the uniforms and texture modes correctly.
// Call this everytime you want to draw this pass after your drew another.
void load_${NAME}_pass(int pass)
{
	${TEXTURE_PARAMETERS_AND_UNIFORMS}
}

// Call this in the main loop to draw this shader.
void draw_${NAME}()
{
	for(int i=0; i<nPasses-1; ++i)
	{
		load_${NAME}_pass(i);
		((PFNGLBINDFRAMEBUFFERPROC)wglGetProcAddress("glBindFramebuffer"))(GL_FRAMEBUFFER, buffers[i].frameBuffer);
		((PFNGLUNIFORM1IPROC)wglGetProcAddress("glUniform1i"))(7, i);
		glRecti(-1, -1, +1, +1);
	}

	load_${NAME}_pass(nPasses-1);
	((PFNGLBINDFRAMEBUFFERPROC)wglGetProcAddress("glBindFramebuffer"))(GL_FRAMEBUFFER, 0);
	((PFNGLUNIFORM1IPROC)wglGetProcAddress("glUniform1i"))(7, nPasses - 1);
	glRecti(-1, -1, +1, +1);
}

// Use program and set nPasses correctly.
// Call this once when the scene is changing.
void load_${NAME}()
{
	((PFNGLUSEPROGRAMPROC)wglGetProcAddress("glUseProgram"))(program_${NAME});
	nPasses = ${NPASSES};
	drawCurrentEffect = &draw_${NAME};
}
