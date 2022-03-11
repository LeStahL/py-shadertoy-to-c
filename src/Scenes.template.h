// Generated using the superior demo tool of Team210.

#pragma once

${INCLUDE_LIST}

float currentSceneStartTime = 0.;
float demoLength = ${DEMO_LENGTH};

void selectCurrentScene(float time, float lastTime)
{
	${SCENE_LIST}
}

void setupAllScenes(void (*callback)(float progress))
{
	${LOAD_SCENE_LIST}
}
