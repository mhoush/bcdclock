#!/usr/bin/env python

import ctypes
from random import randint
import os
import sdl2
import sdl2.sdlttf
import sys
import time


# global configuration

# window size
width = 1280
height = 540

# background color
bgcolor = (50, 50, 50)

# updates per second (higher = more responsive, lower = less processing)
ups = 10


def randomColor():
	"""Returns a random RGB color that's not too dark and not too bright."""
	return((randint(40, 200), randint(40, 200), randint(40, 200)))


def clearScreen(renderer, color):
	"""Clears the renderer with the specified background color."""
	sdl2.SDL_SetRenderDrawColor(renderer, color[0], color[1], color[2], sdl2.SDL_ALPHA_OPAQUE)
	sdl2.SDL_RenderClear(renderer)


def drawBox(renderer, color, x, y, w, h):
	"""Draws a box (rectangle) to the renderer with the specified color,
coordinates, and size."""
	rect = sdl2.SDL_Rect(x, y, w, h)
	sdl2.SDL_SetRenderDrawColor(renderer, color[0], color[1], color[2], sdl2.SDL_ALPHA_OPAQUE)
	sdl2.SDL_RenderFillRect(renderer, rect)
	sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, sdl2.SDL_ALPHA_OPAQUE)
	sdl2.SDL_RenderDrawRect(renderer, rect)


def drawPanel(renderer, color, row, col):
	"""Draws one panel of the clock face to the renderer with the specified
color at the specified row and column using drawBox()."""
	x = (width // 6) * col
	y = (height // 4) * row
	w = (width // 6)
	h = (height // 4)
	drawBox(renderer, color, x + 1, y + 1, w - 2, h - 2)


def drawText(renderer, font, ofont, time):
	"""Draws the decimal text version of the time on top of the BCD panels in
white with a black outline."""
	fgsurface = sdl2.sdlttf.TTF_RenderText_Blended(font, str.encode(time), sdl2.SDL_Color(255, 255, 255))
	bgsurface = sdl2.sdlttf.TTF_RenderText_Blended(ofont, str.encode(time), sdl2.SDL_Color(0, 0, 0))

	# get the width and height of the rendered text (differs by font used)
	w = ctypes.c_int()
	h = ctypes.c_int()
	sdl2.sdlttf.TTF_SizeText(font, str.encode(time), w, h)

	# offset the outline text and blit it with the main text
	offsetrect = sdl2.SDL_Rect(-2, -2, w.value, h.value)
	sdl2.SDL_BlitSurface(fgsurface, offsetrect, bgsurface, None)

	# create a texture from the blitted surface
	texttexture = sdl2.SDL_CreateTextureFromSurface(renderer, bgsurface)

	# free the no-longer-needed surfaces
	sdl2.SDL_FreeSurface(bgsurface)
	sdl2.SDL_FreeSurface(fgsurface)

	# create a rectangle for the new texture (centered) and render it to the renderer
	textrect = sdl2.SDL_Rect(width // 2 - w.value // 2, height // 2 - h.value // 2, w.value, h.value)
	sdl2.SDL_RenderCopy(renderer, texttexture, None, textrect)


def toBCD(digit):
	"""Returns a BCD (binary coded decimal) representation of the specified
digit in list form with the most significant bit first. For example:

	toBCD('7') returns [ '0', '1', '1', '1' ]."""
	return([x for x in bin(int(digit))[2:].rjust(4, '0')])


def timeToMatrix(timestring):
	"""Returns a 2D matrix of panels for the BCD display of the clock face.
values of '1' are active (on) panels, values of '0' are off. For example:

	timeToMatrix('12:34:56 PM') returns the following:

	[['0', '0', '0', '0', '0', '0'],
	 ['0', '0', '0', '1', '1', '1'],
	 ['0', '1', '1', '0', '0', '1'],
	 ['1', '0', '1', '0', '1', '0']]
"""
	matrix = []
	for digit in [x for x in timestring if x not in ': APM']:
		matrix.append(toBCD(digit))

	flipped = []
	for row in range(0, 4):
		newrow = []
		for col in range(0, 6):
			newrow.append(matrix[col][row])
		flipped.append(newrow)

	return(flipped)


def selectFont(fontlist, fontindex, size):
	"""Returns a tuple containing the font and outline font at the specified
index in the fontlist."""
	curfont = str.encode("fonts/" + fontlist[fontindex])
	print("Selected font %d: %s" % (fontindex, fontlist[fontindex]))
	font = sdl2.sdlttf.TTF_OpenFont(curfont, size)
	ofont = sdl2.sdlttf.TTF_OpenFont(curfont, size)
	sdl2.sdlttf.TTF_SetFontOutline(ofont, 2)
	return (font, ofont)


def setFullscreen(window, fullscreen):
	"""Sets the window to fullscreen or windowed mode depending on the boolean
'fullscreen' flag and returns the new window dimensions as a tuple."""
	if fullscreen:
		# hide the cursor
		sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
		# set the window to fullscreen mode and get its new dimensions
		sdl2.SDL_SetWindowFullscreen(window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
		w = ctypes.c_int()
		h = ctypes.c_int()
		sdl2.SDL_GetWindowSize(window, w, h)
		width = w.value
		height = h.value
	else:
		# show the cursor
		sdl2.SDL_ShowCursor(sdl2.SDL_ENABLE)
		# set the window to windowed mode and go back to the original dimensions
		sdl2.SDL_SetWindowFullscreen(window, 0)
		width = origwidth
		height = origheight

	# return the new dimensions
	return (width, height)


def run():
	"""The main program loop."""

	# mark these as global variables
	global width, height, origwidth, origheight

	# load fonts from the "fonts" folder
	fontlist = []
	for _, _, files in os.walk("fonts"):
		for font in files:
			fontlist.append(font)
	print("Found %d fonts." % len(fontlist))

	# toggles for 24-hour and timezone modes
	mode24 = True
	modelocal = True

	# initialize sdl
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

	# initialize sdl_ttf
	sdl2.sdlttf.TTF_Init()

	# set the default font size and select the first font in the list
	fontsize = 128
	fontindex = 0
	(font, ofont) = selectFont(fontlist, fontindex, fontsize)

	# create the main program window
	window = sdl2.SDL_CreateWindow(b'BCD Clock', sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED, width, height, sdl2.SDL_WINDOW_SHOWN)

	# create the renderer onto which everything is drawn
	renderer = sdl2.SDL_CreateRenderer(window, -1, 0)

	# pick a random color for the foreground (panels)
	fgcolor = randomColor()

	# preserve original window dimensions
	origwidth = width
	origheight = height

	# start in windowed mode
	fullscreen = False

	# start the main processing loop which repeats until the program is exited
	running = True
	while running:

		# determine the time format based on the mode, 24- or 12-hour
		if mode24:
			formatstr = "%H:%M:%S"
		else:
			formatstr = "%I:%M:%S %p"

		# determine whether to display local timezone or GMT
		if modelocal:
			timefunc = time.localtime
		else:
			timefunc = time.gmtime

		# get the current time
		current_time = time.strftime(formatstr, timefunc())

		# clear the screen
		clearScreen(renderer, bgcolor)

		# poll events and react to a few things such as a quit signal (closing
		# the window) or key presses to change modes or text font
		event = sdl2.SDL_Event()
		while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
			# if we received a quit event, stop the loop
			if event.type == sdl2.SDL_QUIT:
				running = False
			# if a mouse button was clicked, print the time to the console
			if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
				print(current_time)
			# if a key was pressed, check which one
			if event.type == sdl2.SDL_KEYDOWN:
				# space changes the panel color randomly
				if event.key.keysym.sym == sdl2.SDLK_SPACE:
					fgcolor = randomColor()
				# 'h' toggles between 24- and 12-hour modes
				if event.key.keysym.sym == sdl2.SDLK_h:
					mode24 = not mode24
				# 'l' toggles between the local timezone and GMT
				if event.key.keysym.sym == sdl2.SDLK_l:
					modelocal = not modelocal
				# 'f' toggles fullscreen/windowed mode
				if event.key.keysym.sym == sdl2.SDLK_f:
					fullscreen = not fullscreen
					(width, height) = setFullscreen(window, fullscreen)
				# 't' selects the next available font for the clock text
				if event.key.keysym.sym == sdl2.SDLK_t:
					fontindex += 1
					if fontindex >= len(fontlist):
						fontindex = 0
					(font, ofont) = selectFont(fontlist, fontindex, fontsize)

		# convert the current time to the BCD time matrix
		bcd_time = timeToMatrix(current_time)

		# draw (turn on) the panels in the matrix with value '1'
		for row in range(0, 4):
			for col in range(0, 6):
				if int(bcd_time[row][col]) == 1:
					drawPanel(renderer, fgcolor, row, col)

		# render the time text on top of the clock panels
		drawText(renderer, font, ofont, current_time)

		# update the window title with the proper mode and timezone setting
		sdl2.SDL_SetWindowTitle(window, str.encode('BCD Clock (' + ('24h' if mode24 else '12h') + ' ' + (time.strftime('%Z') if modelocal else 'GMT') + ')'))

		# refresh/redraw the window
		sdl2.SDL_RenderPresent(renderer)

		# wait a little bit between updates
		sdl2.SDL_Delay(1000 // ups)

	# main loop has exited, clean up and quit

	# clean up fonts
	sdl2.sdlttf.TTF_CloseFont(ofont)
	sdl2.sdlttf.TTF_CloseFont(font)

	# quit sdl_ttf
	sdl2.sdlttf.TTF_Quit()

	# clean up the renderer
	sdl2.SDL_DestroyRenderer(renderer)

	# clean up the window
	sdl2.SDL_DestroyWindow(window)

	# quit sdl
	sdl2.SDL_Quit()


if __name__ == "__main__":
	# run the main loop!
	sys.exit(run())
