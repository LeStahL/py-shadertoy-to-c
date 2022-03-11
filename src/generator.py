#!/usr/bin/env python
#
# py-shadertoy-to-c
# Copyright (C) 2022 Alexander Kraus <nr4@z10.info>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse, json, os, sys, numpy, struct

# File loading and saving functionality
def loadFile(fileName):
	templateSource = ""
	with open(fileName) as file:
		templateSource = file.read()
		file.close()
	return templateSource

def saveFile(fileName, text):
	with open(fileName, "wt") as file:
		file.write(text)
		file.close()

def parseFile(shaderJson, inputFileName):
	# Load number of passes first
	nPasses = 0
	for passJson in shaderJson['renderpass']:
		if passJson['type'] in ['buffer', 'image']:
			nPasses += 1
	
	# Load the actual passes
	commonSource = ""
	passSources = [""] * nPasses
	passNames = []
	passIds = [""] * nPasses
	inputIds = [[]] * nPasses
	filterTypes = [[]] * nPasses
	wrapModes = [[]] * nPasses
	for passJson in shaderJson['renderpass']:
		if passJson['type'] == 'common':
			commonSource = passJson['code']
		elif passJson['type'] in ['buffer', 'image']:
			if passJson['type'] == 'buffer':
				bufferIndex = ord(passJson['name'][-1]) - ord('A')
			else:
				bufferIndex = -1
			passNames += [passJson['name']]
			passSources[bufferIndex] = passJson['code']
			passIds[bufferIndex] = passJson['outputs'][0]['id']
			inputId = []
			filterType = []
			wrapMode = []
			for inputJson in passJson['inputs']:
				if inputJson['type'] == 'buffer':
					inputId += [inputJson['id']]
					filterType += [inputJson['sampler']['filter']]
					wrapMode += [inputJson['sampler']['wrap']]
			inputIds[bufferIndex] = inputId
			filterTypes[bufferIndex] = filterType
			wrapModes[bufferIndex] = wrapMode

	# Determine the input indices
	inputIndices = []
	for inputIdList in inputIds:
		inputIndices += [list(map(lambda inputId: passIds.index(inputId), inputIdList))]

	return (passNames, nPasses, commonSource, passSources, inputIndices, filterTypes, wrapModes, inputFileName)

def parseDemoJson(demoJson):
	loadingBar = demoJson['loading-bar']['name']
	sceneNames = list(map(lambda shaderJson: shaderJson['name'], demoJson['shaders']))
	sceneEndTimes = list(map(lambda shaderJson: shaderJson['end'], demoJson['shaders']))
	return (loadingBar, sceneNames, sceneEndTimes)


# Command line argument parser
parser = argparse.ArgumentParser(description='Team210 scene code generator.')
parser.add_argument('-o', '--output', dest='output')
parser.add_argument('-s', '--setup', dest='setup', action='store_true')
parser.add_argument('-sh', '--shader', dest='shader', action='store_true')
parser.add_argument('-d', '--draw', dest='draw', action='store_true')
parser.add_argument('-p', '--plain', dest='plain', action='store_true')
parser.add_argument('-ph', '--plain-header', dest='plain_header', action='store_true')
parser.add_argument('-sg', '--setup-global', dest='setupGlobal', action='store_true')
parser.add_argument('-dg', '--draw-global', dest='drawGlobal', action='store_true')
parser.add_argument('-f', '--font', dest='font', action='store_true')
args, rest = parser.parse_known_args()

# Verify presence of input
if rest == []:
    print("No input present. Doing nothing. Type 'scene -h' for help.")
    exit()

# Generate plain fragment file
if args.plain:
	(passNames, nPasses, commonSource, passSources, inputIndices, filterTypes, wrapModes, inputFileName) = parseFile(json.loads(loadFile(rest[0])), rest[0])
	(shaderId, extension) = os.path.splitext(os.path.basename(inputFileName))
	
	outputDirectory = os.path.dirname(inputFileName)

	plainTemplate = loadFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shader.template.frag'))
	plainSource = plainTemplate.replace('${COMMON_SOURCE}', commonSource)
	passSource = ""
	passInvocations = ""
	for i in range(len(passSources)):
		passSource += passSources[i].replace('mainImage', 'mainImage' + str(i))
		passInvocations += "if(iPass == " + str(i) + ") mainImage" + str(i) + "(out_color, gl_FragCoord.xy);"
	plainSource = plainSource.replace('${PASS_SOURCES}', passSource)
	plainSource = plainSource.replace('${PASS_INVOCATIONS}', passInvocations)

	saveFile(os.path.join(outputDirectory, shaderId + ".frag"), plainSource)
 
# Generate header from plain fragment file
if args.plain_header:
	(passNames, nPasses, commonSource, passSources, inputIndices, filterTypes, wrapModes, inputFileName) = parseFile(json.loads(loadFile(rest[0])), rest[0])
	(shaderId, extension) = os.path.splitext(os.path.basename(inputFileName))
	
	outputDirectory = os.path.dirname(inputFileName)

	plainTemplate = loadFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Shader.template.frag'))
	plainSource = plainTemplate.replace('${COMMON_SOURCE}', commonSource)
	passSource = ""
	passInvocations = ""
	for i in range(len(passSources)):
		passSource += passSources[i].replace('mainImage', 'mainImage' + str(i))
		passInvocations += "if(iPass == " + str(i) + ") mainImage" + str(i) + "(out_color, gl_FragCoord.xy);"
	plainSource = plainSource.replace('${PASS_SOURCES}', passSource)
	plainSource = plainSource.replace('${PASS_INVOCATIONS}', passInvocations)

	plainSource = '// Generated using the superior demo tool of Team210.\n#pragma once\nconst char *' + shaderId + "_frag =\n" + '\n'.join(map(lambda line: '"' + line + '\\n"', plainSource.split('\n'))) + ';\n'

	saveFile(os.path.join(outputDirectory, shaderId + "_min.h"), plainSource)

# Generate setup header file
if args.setup:
	(passNames, nPasses, commonSource, passSources, inputIndices, filterTypes, wrapModes, inputFileName) = parseFile(json.loads(loadFile(rest[0])), rest[0])
	(shaderId, extension) = os.path.splitext(os.path.basename(inputFileName))
	
	outputDirectory = os.path.dirname(inputFileName)

	setupTemplate = loadFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Setup.template.h'))
	setupSource = setupTemplate.replace('${NAME}', shaderId)
	setupSource = setupSource.replace('${NPASSES}', str(nPasses))
	textureParametersAndUniforms = ""
	for i in range(nPasses):
		if len(inputIndices[i]) == 0:
			continue
		textureParametersAndUniforms += "if(pass == " + str(i) + ")\n"
		textureParametersAndUniforms += "	{\n"
		# textureParametersAndUniforms += "		glBindTexture(GL_TEXTURE_2D, buffers[" + str(i) + "].texture);\n"
		# TODO: Change these to contain the shadertoy values
		# textureParametersAndUniforms += "		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);\n"
		# textureParametersAndUniforms += "		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);\n"
		# textureParametersAndUniforms += "		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);\n"
		# textureParametersAndUniforms += "		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);\n"
		
		for j in range(len(inputIndices[i])):
			textureParametersAndUniforms += "  		((PFNGLUNIFORM1IPROC)wglGetProcAddress(\"glUniform1i\"))(" + str(3 + j) + ", " + str(inputIndices[i][j]) + ");\n"
		textureParametersAndUniforms += "	}\n"		
	setupSource = setupSource.replace("${TEXTURE_PARAMETERS_AND_UNIFORMS}", textureParametersAndUniforms)

	saveFile(os.path.join(outputDirectory, shaderId + ".h"), setupSource)

# Generate scene header file
if args.setupGlobal:
	(loadingBar, sceneNames, sceneEndTimes) = parseDemoJson(json.loads(loadFile(rest[0])))

	scenesTemplate = loadFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Scenes.template.h'))

	includeList = "#include \"" + loadingBar + ".h\"\n"
	for sceneName in sceneNames:
		includeList += '#include \"' + sceneName + '.h\"\n'
	scenesTemplate = scenesTemplate.replace('${INCLUDE_LIST}', includeList)
	scenesTemplate = scenesTemplate.replace('${DEMO_LENGTH}', str(sceneEndTimes[-1]))

	sceneList = "if (time >= 0. && lastTime < 0.)\n	{\n		load_" + sceneNames[0] + "();\n	}\n"
	for i in range(len(sceneEndTimes)-1):
		sceneList += "	else if(time >= " + str(sceneEndTimes[i]) + " && lastTime < " + str(sceneEndTimes[i]) + ")\n"
		sceneList += "	{\n"
		sceneList += "		currentSceneStartTime = " + str(sceneEndTimes[i]) + ";\n"
		sceneList += "		load_" + sceneNames[i+1] + "();\n"
		sceneList += "	}"
	scenesTemplate = scenesTemplate.replace('${SCENE_LIST}', sceneList)

	loadSceneList = ""
	for i in range(len(sceneNames)):
		sceneName = sceneNames[i]
		loadSceneList += "	setUp_" + sceneName + "();\n"
		loadSceneList += "	callback(" + str(float(i+1)/float(len(sceneNames))) + ");\n"
		loadSceneList += "	draw_" + loadingBar + "();\n"
		loadSceneList += "	SwapBuffers(demoWindow.deviceContext);\n"
	scenesTemplate = scenesTemplate.replace('${LOAD_SCENE_LIST}', loadSceneList)

	saveFile(args.output, scenesTemplate)
