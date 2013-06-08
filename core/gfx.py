
import cairo
import Image
import math
import os
import sys
import util


POS_TOP = 0
POS_RIGHT = 1
POS_BOTTOM = 2
POS_LEFT = 3
ALIGN_NEAR = -1
ALIGN_CENTER = 0
ALIGN_FAR = 1
CORNER_SIZE = 8
CORNER_JOIN = 0


def CreateSurfaceContext(width, height):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	cr = cairo.Context(surface)
	return (surface, cr)

def Alpha(image, alphaFactor = 1.0, redFactor = 1.0, greenFactor = 1.0, blueFactor = 1.0):
	def uint(i):
	    i = int(i)
	    if i > sys.maxint and i <= 2 * sys.maxint + 1:
	        return int((i & sys.maxint) - sys.maxint - 1)
	    else:
	        return i
	def mult(value, factor):
		return int(((type(factor) == int or type(factor) == float) and float(factor) or 1.0) * ((type(value) == int or type(value) == float) and float(value) or 1.0))
	def toHex(val):
		return hex(val > 255 and 255 or (val > 0 and val or 0))[2:].rjust(2, '0')
	if util.IsString(image):
		image = Image.open(util.MapPath('ui/' + image.strip('/')), 'r')
	nu = Image.new('RGBA', (image.size[0], image.size[1]))
	for x in xrange(0, image.size[0]):
		for y in xrange(0, image.size[1]):
			color = image.getpixel((x,y))
			alpha, color0, color1, color2 = int(((len(color) < 4) and 255 or color[3]) * alphaFactor), mult(color[0], redFactor), mult(color[1], greenFactor), mult(color[2], blueFactor)
			nu.putpixel((x, y,), uint(int("0x" + toHex(alpha) + toHex(color2) + toHex(color1) + toHex(color0), 16)))
	return nu


def Blend(path, rgba):
	source = cairo.ImageSurface.create_from_png(util.MapPath(path))
	width = source.get_width()
	height = source.get_height()
	surface, cr = CreateSurfaceContext(width, height)
	cr.set_source_surface(source, 0, 0)
	cr.rectangle(0, 0, width, height)
	cr.fill_preserve()
	cr.set_source_rgba(*rgba)
	cr.fill()
	surface.flush()
	source.finish()
	return surface


def Color(rgba):
	surface, cr = CreateSurfaceContext(2, 2)
	cr.rectangle(-2, -2, 6, 6)
	cr.set_source_rgba(*rgba)
	cr.fill()
	surface.flush()
	return surface


def Texturize(image):
	if util.IsString(image):
		image = Image.open(util.MapPath('ui' + image), 'r')
	imgWidth, imgHeight = image.size [0], image.size [1]
	nu = Image.new(image.mode, (imgWidth * 2, imgHeight * 2))
	nu.paste(image, (0, 0, imgWidth, imgHeight))
	flip = image.transpose(Image.FLIP_LEFT_RIGHT)
	nu.paste(flip, (imgWidth, 0, imgWidth * 2, imgHeight))
	nu.paste(image.transpose(Image.FLIP_TOP_BOTTOM), (0, imgHeight, imgWidth, imgHeight * 2))
	nu.paste(flip.transpose(Image.FLIP_TOP_BOTTOM), (imgWidth, imgHeight, imgWidth * 2, imgHeight * 2))
	return nu
