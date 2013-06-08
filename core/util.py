# -*- coding: utf-8 -*-

from __future__ import with_statement
import cairo
import gfx
import hashlib
import Image
import locale
import os
import re
import signal
import simplejson
import threading
import time
import urllib

_jsonFixupPattern = re.compile("\t+([a-z]|[A-Z]|[0-9]|[$_])+:\s+")

_htmlEntities = {
	'"': '&#34;',
	"'": '&#39;',
	'<': '&lt;',	# less-than sign
	'>': '&gt;',	# greater-than sign
	'': '&nbsp;',	# no-break space (= non-breaking space)[4]
	'¡': '&iexcl;',	# inverted exclamation mark
	'¢': '&cent;',	# cent sign
	'£': '&pound;',	# pound sign
	'¤': '&curren;',	# currency sign
	'¥': '&yen;',	# yen sign (= yuan sign)
	'¦': '&brvbar;',	# broken bar (= broken vertical bar)
	'§': '&sect;',	# section sign
	'¨': '&uml;',	# diaeresis (= spacing diaeresis); see German umlaut
	'©': '&copy;',	# copyright sign
	'ª': '&ordf;',	# feminine ordinal indicator
	'«': '&laquo;',	# left-pointing double angle quotation mark (= left pointing guillemet)
	'¬': '&not;',	# not sign
	'': '&shy;',	# soft hyphen (= discretionary hyphen)
	'®': '&reg;',	# registered sign ( = registered trade mark sign)
	'¯': '&macr;',	# macron (= spacing macron = overline = APL overbar)
	'°': '&deg;',	# degree sign
	'±': '&plusmn;',	# plus-minus sign (= plus-or-minus sign)
	'²': '&sup2;',	# superscript two (= superscript digit two = squared)
	'³': '&sup3;',	# superscript three (= superscript digit three = cubed)
	'´': '&acute;',	# acute accent (= spacing acute)
	'µ': '&micro;',	# micro sign
	'¶': '&para;',	# pilcrow sign ( = paragraph sign)
	'·': '&middot;',	# middle dot (= Georgian comma = Greek middle dot)
	'¸': '&cedil;',	# cedilla (= spacing cedilla)
	'¹': '&sup1;',	# superscript one (= superscript digit one)
	'º': '&ordm;',	# masculine ordinal indicator
	'»': '&raquo;',	# right-pointing double angle quotation mark (= right pointing guillemet)
	'¼': '&frac14;',	# vulgar fraction one quarter (= fraction one quarter)
	'½': '&frac12;',	# vulgar fraction one half (= fraction one half)
	'¾': '&frac34;',	# vulgar fraction three quarters (= fraction three quarters)
	'¿': '&iquest;',	# inverted question mark (= turned question mark)
	'À': '&Agrave;',	# Latin capital letter A with grave (= Latin capital letter A grave)
	'Á': '&Aacute;',	# Latin capital letter A with acute
	'Â': '&Acirc;',	# Latin capital letter A with circumflex
	'Ã': '&Atilde;',	# Latin capital letter A with tilde
	'Ä': '&Auml;',	# Latin capital letter A with diaeresis
	'Å': '&Aring;',	# Latin capital letter A with ring above (= Latin capital letter A ring)
	'Æ': '&AElig;',	# Latin capital letter AE (= Latin capital ligature AE)
	'Ç': '&Ccedil;',	# Latin capital letter C with cedilla
	'È': '&Egrave;',	# Latin capital letter E with grave
	'É': '&Eacute;',	# Latin capital letter E with acute
	'Ê': '&Ecirc;',	# Latin capital letter E with circumflex
	'Ë': '&Euml;',	# Latin capital letter E with diaeresis
	'Ì': '&Igrave;',	# Latin capital letter I with grave
	'Í': '&Iacute;',	# Latin capital letter I with acute
	'Î': '&Icirc;',	# Latin capital letter I with circumflex
	'Ï': '&Iuml;',	# Latin capital letter I with diaeresis
	'Ð': '&ETH;',	# Latin capital letter ETH
	'Ñ': '&Ntilde;',	# Latin capital letter N with tilde
	'Ò': '&Ograve;',	# Latin capital letter O with grave
	'Ó': '&Oacute;',	# Latin capital letter O with acute
	'Ô': '&Ocirc;',	# Latin capital letter O with circumflex
	'Õ': '&Otilde;',	# Latin capital letter O with tilde
	'Ö': '&Ouml;',	# Latin capital letter O with diaeresis
	'×': '&times;',	# multiplication sign
	'Ø': '&Oslash;',	# Latin capital letter O with stroke (= Latin capital letter O slash)
	'Ù': '&Ugrave;',	# Latin capital letter U with grave
	'Ú': '&Uacute;',	# Latin capital letter U with acute
	'Û': '&Ucirc;',	# Latin capital letter U with circumflex
	'Ü': '&Uuml;',	# Latin capital letter U with diaeresis
	'Ý': '&Yacute;',	# Latin capital letter Y with acute
	'Þ': '&THORN;',	# Latin capital letter THORN
	'ß': '&szlig;',	# Latin small letter sharp s (= ess-zed); see German Eszett
	'à': '&agrave;',	# Latin small letter a with grave
	'á': '&aacute;',	# Latin small letter a with acute
	'â': '&acirc;',	# Latin small letter a with circumflex
	'ã': '&atilde;',	# Latin small letter a with tilde
	'ä': '&auml;',	# Latin small letter a with diaeresis
	'å': '&aring;',	# Latin small letter a with ring above
	'æ': '&aelig;',	# Latin small letter ae (= Latin small ligature ae)
	'ç': '&ccedil;',	# Latin small letter c with cedilla
	'è': '&egrave;',	# Latin small letter e with grave
	'é': '&eacute;',	# Latin small letter e with acute
	'ê': '&ecirc;',	# Latin small letter e with circumflex
	'ë': '&euml;',	# Latin small letter e with diaeresis
	'ì': '&igrave;',	# Latin small letter i with grave
	'í': '&iacute;',	# Latin small letter i with acute
	'î': '&icirc;',	# Latin small letter i with circumflex
	'ï': '&iuml;',	# Latin small letter i with diaeresis
	'ð': '&eth;',	# Latin small letter eth
	'ñ': '&ntilde;',	# Latin small letter n with tilde
	'ò': '&ograve;',	# Latin small letter o with grave
	'ó': '&oacute;',	# Latin small letter o with acute
	'ô': '&ocirc;',	# Latin small letter o with circumflex
	'õ': '&otilde;',	# Latin small letter o with tilde
	'ö': '&ouml;',	# Latin small letter o with diaeresis
	'÷': '&divide;',	# division sign
	'ø': '&oslash;',	# Latin small letter o with stroke (= Latin small letter o slash)
	'ù': '&ugrave;',	# Latin small letter u with grave
	'ú': '&uacute;',	# Latin small letter u with acute
	'û': '&ucirc;',	# Latin small letter u with circumflex
	'ü': '&uuml;',	# Latin small letter u with diaeresis
	'ý': '&yacute;',	# Latin small letter y with acute
	'þ': '&thorn;',	# Latin small letter thorn
	'ÿ': '&yuml;',	# Latin small letter y with diaeresis
	'Œ': '&OElig;',	# Latin capital ligature oe[5]
	'œ': '&oelig;',	# Latin small ligature oe[6]
	'Š': '&Scaron;',	# Latin capital letter s with caron
	'š': '&scaron;',	# Latin small letter s with caron
	'Ÿ': '&Yuml;',	# Latin capital letter y with diaeresis
	'ƒ': '&fnof;',	# Latin small letter f with hook (= function = florin)
	'ˆ': '&circ;',	# modifier letter circumflex accent
	'˜': '&tilde;',	# small tilde
	'Α': '&Alpha;',	# Greek capital letter Alpha
	'Β': '&Beta;',	# Greek capital letter Beta
	'Γ': '&Gamma;',	# Greek capital letter Gamma
	'Δ': '&Delta;',	# Greek capital letter Delta
	'Ε': '&Epsilon;',	# Greek capital letter Epsilon
	'Ζ': '&Zeta;',	# Greek capital letter Zeta
	'Η': '&Eta;',	# Greek capital letter Eta
	'Θ': '&Theta;',	# Greek capital letter Theta
	'Ι': '&Iota;',	# Greek capital letter Iota
	'Κ': '&Kappa;',	# Greek capital letter Kappa
	'Λ': '&Lambda;',	# Greek capital letter Lambda
	'Μ': '&Mu;',	# Greek capital letter Mu
	'Ν': '&Nu;',	# Greek capital letter Nu
	'Ξ': '&Xi;',	# Greek capital letter Xi
	'Ο': '&Omicron;',	# Greek capital letter Omicron
	'Π': '&Pi;',	# Greek capital letter Pi
	'Ρ': '&Rho;',	# Greek capital letter Rho
	'Σ': '&Sigma;',	# Greek capital letter Sigma
	'Τ': '&Tau;',	# Greek capital letter Tau
	'Υ': '&Upsilon;',	# Greek capital letter Upsilon
	'Φ': '&Phi;',	# Greek capital letter Phi
	'Χ': '&Chi;',	# Greek capital letter Chi
	'Ψ': '&Psi;',	# Greek capital letter Psi
	'Ω': '&Omega;',	# Greek capital letter Omega
	'α': '&alpha;',	# Greek small letter alpha
	'β': '&beta;',	# Greek small letter beta
	'γ': '&gamma;',	# Greek small letter gamma
	'δ': '&delta;',	# Greek small letter delta
	'ε': '&epsilon;',	# Greek small letter epsilon
	'ζ': '&zeta;',	# Greek small letter zeta
	'η': '&eta;',	# Greek small letter eta
	'θ': '&theta;',	# Greek small letter theta
	'ι': '&iota;',	# Greek small letter iota
	'κ': '&kappa;',	# Greek small letter kappa
	'λ': '&lambda;',	# Greek small letter lambda
	'μ': '&mu;',	# Greek small letter mu
	'ν': '&nu;',	# Greek small letter nu
	'ξ': '&xi;',	# Greek small letter xi
	'ο': '&omicron;',	# Greek small letter omicron
	'π': '&pi;',	# Greek small letter pi
	'ρ': '&rho;',	# Greek small letter rho
	'ς': '&sigmaf;',	# Greek small letter final sigma
	'σ': '&sigma;',	# Greek small letter sigma
	'τ': '&tau;',	# Greek small letter tau
	'υ': '&upsilon;',	# Greek small letter upsilon
	'φ': '&phi;',	# Greek small letter phi
	'χ': '&chi;',	# Greek small letter chi
	'ψ': '&psi;',	# Greek small letter psi
	'ω': '&omega;',	# Greek small letter omega
	'ϑ': '&thetasym;',	# Greek theta symbol
	'ϒ': '&upsih;',	# Greek Upsilon with hook symbol
	'ϖ': '&piv;',	# Greek pi symbol
	' ': '&ensp;',	# en space[7]
	' ': '&emsp;',	# em space[8]
	' ': '&thinsp;',	# thin space[9]
	'': '&zwnj;',	# zero-width non-joiner
	'': '&zwj;',	# zero-width joiner
	'': '',	# left-to-right mark
	'': '',	# right-to-left mark
	'–': '&ndash;',	# en dash
	'—': '&mdash;',	# em dash
	'‘': '&lsquo;',	# left single quotation mark
	'’': '&rsquo;',	# right single quotation mark
	'‚': '&sbquo;',	# single low-9 quotation mark
	'“': '&ldquo;',	# left double quotation mark
	'”': '&rdquo;',	# right double quotation mark
	'„': '&bdquo;',	# double low-9 quotation mark
	'†': '&dagger;',	# dagger
	'‡': '&Dagger;',	# double dagger
	'•': '&bull;',	# bullet (= black small circle)[10]
	'…': '&hellip;',	# horizontal ellipsis (= three dot leader)
	'‰': '&permil;',	# per mille sign
	'′': '&prime;',	# prime (= minutes = feet)
	'″': '&Prime;',	# double prime (= seconds = inches)
	'‹': '&lsaquo;',	# single left-pointing angle quotation mark[11]
	'›': '&rsaquo;',	# single right-pointing angle quotation mark[12]
	'‾': '&oline;',	# overline (= spacing overscore)
	'⁄': '&frasl;',	# fraction slash (= solidus)
	'€': '&euro;',	# euro sign
	'ℑ': '&image;',	# black-letter capital I (= imaginary part)
	'℘': '&weierp;',	# script capital P (= power set = Weierstrass p)
	'ℜ': '&real;',	# black-letter capital R (= real part symbol)
	'™': '&trade;',	# trademark sign
	'ℵ': '&alefsym;',	# alef symbol (= first transfinite cardinal)[13]
	'←': '&larr;',	# leftwards arrow
	'↑': '&uarr;',	# upwards arrow
	'→': '&rarr;',	# rightwards arrow
	'↓': '&darr;',	# downwards arrow
	'↔': '&harr;',	# left right arrow
	'↵': '&crarr;',	# downwards arrow with corner leftwards (= carriage return)
	'⇐': '&lArr;',	# leftwards double arrow[14]
	'⇑': '&uArr;',	# upwards double arrow
	'⇒': '&rArr;',	# rightwards double arrow[15]
	'⇓': '&dArr;',	# downwards double arrow
	'⇔': '&hArr;',	# left right double arrow
	'∀': '&forall;',	# for all
	'∂': '&part;',	# partial differential
	'∃': '&exist;',	# there exists
	'∅': '&empty;',	# empty set (= null set = diameter)
	'∇': '&nabla;',	# nabla (= backward difference)
	'∈': '&isin;',	# element of
	'∉': '&notin;',	# not an element of
	'∋': '&ni;',	# contains as member
	'∏': '&prod;',	# n-ary product (= product sign)[16]
	'∑': '&sum;',	# n-ary summation[17]
	'−': '&minus;',	# minus sign
	'∗': '&lowast;',	# asterisk operator
	'√': '&radic;',	# square root (= radical sign)
	'∝': '&prop;',	# proportional to
	'∞': '&infin;',	# infinity
	'∠': '&ang;',	# angle
	'∧': '&and;',	# logical and (= wedge)
	'∨': '&or;',	# logical or (= vee)
	'∩': '&cap;',	# intersection (= cap)
	'∪': '&cup;',	# union (= cup)
	'∫': '&int;',	# integral
	'∴': '&there4;',	# therefore
	'∼': '&sim;',	# tilde operator (= varies with = similar to)[18]
	'≅': '&cong;',	# congruent to
	'≈': '&asymp;',	# almost equal to (= asymptotic to)
	'≠': '&ne;',	# not equal to
	'≡': '&equiv;',	# identical to; sometimes used for 'equivalent to'
	'≤': '&le;',	# less-than or equal to
	'≥': '&ge;',	# greater-than or equal to
	'⊂': '&sub;',	# subset of
	'⊃': '&sup;',	# superset of[19]
	'⊄': '&nsub;',	# not a subset of
	'⊆': '&sube;',	# subset of or equal to
	'⊇': '&supe;',	# superset of or equal to
	'⊕': '&oplus;',	# circled plus (= direct sum)
	'⊗': '&otimes;',	# circled times (= vector product)
	'⊥': '&perp;',	# up tack (= orthogonal to = perpendicular)
	'⋅': '&sdot;',	# dot operator[20]
	'⌈': '&lceil;',	# left ceiling (= APL upstile)
	'⌉': '&rceil;',	# right ceiling
	'⌊': '&lfloor;',	# left floor (= APL downstile)
	'⌋': '&rfloor;',	# right floor
	'〈': '&lang;',	# left-pointing angle bracket (= bra)[21]
	'〉': '&rang;',	# right-pointing angle bracket (= ket)[22]
	'◊': '&loz;',	# lozenge
	'♠': '&spades;',	# black spade suit[23]
	'♣': '&clubs;',	# black club suit (= shamrock)[24]
	'♥': '&hearts;',	# black heart suit (= valentine)[25]
	'♦': '&diams;',	# black diamond suit[26]
}


def CleanString(v, hashers = None):
	def deepstr(val):
		if IsIterable(val):
			r = ''
			for i in val:
				r = r + '_' + deepstr(isinstance(val, dict) and val[i] or ((not isinstance(val, dict)) and i or None))
			return r
		else:
			return str(hash(val))
	if not isinstance(v, str):
		v = deepstr(v)
	if hashers:
		s = ''
		for algo in hashers:
			s = s + '_' + GetHexHash(v, algo)
		return s
	else:
		r, v = [], v.replace('0' * 15, '') # edge case: some floats like 0.8 become 0.80000000000000002 or similar. precision not needed, hack: scratch the 15 0s
		for c in v:
			r.append(c.isalnum() and c or '_')
		return ''.join(r)


def ClearDirectory(path):
	for root, dirs, files in os.walk(path, topdown = False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))


def DynGfx(func, *args, **options):
	def _getErrorImageUrl(err = None):
		return '/gfx/icon/fam-mini/action_stop.gif?err=' + UrlEscape(repr(err)) + '&func=' + UrlEscape(repr(func)) + '&args=' + UrlEscape(repr(args)) + '&options=' + UrlEscape(repr(options))
	if not 'ext' in options:
		options['ext'] = 'png'
	if IsString(func):
		func = func in gfx.__dict__ and gfx.__dict__[func] or func
	fileName = (IsString(func) and func or func.__name__) + CleanString(args, ['md5', 'sha1']) + '.' + options['ext']
	fileUrl = '/cache/gfx/dyn/' + fileName;
	filePath = MapPath('ui' + fileUrl)
	try:
		if not os.path.exists(filePath):
			if callable(func):
				surface = func(*args)
			else:
				raise Exception("Unknown operation: '" + func + "'")
			if isinstance(surface, cairo.Surface):
				if options['ext'] != 'png':
					raise Exception("Invalid 'ext' option value '" + options['ext'] + "' for '" + func.__name__ + "' operation: expected 'png'.")
				surface.write_to_png(filePath)
				surface.finish()
			elif isinstance(surface, Image.Image):
				surface.save(filePath)
		return os.path.exists(filePath) and fileUrl or _getErrorImageUrl()
	except Exception, err:
		if 'rethrow' in options:
			raise
		else:
			return _getErrorImageUrl(err)


def FixupCcss(ccss, imports, lazyImports = False):
	pos, css = -1, ''
	for imp in imports:
		if lazyImports:
			css = css + "@import url('/cache/css" + imp.replace('.ccss', '.css') + "');\n"
		else:
			css = css + "@import url('/api/stylesheet.dyn.css?" + imp + "');\n"
	css = css + '\n'
	for line in ccss.splitlines(True):
		pos = line.find(': rgba ')
		if pos > 0:
			css = css + line[:pos + 6] + '(' + line[pos + 7:-2] + ');\n'
		else:
			css = css + line
	return css


def FixupJson(json):
	fix, lines, strip, ignore = '', json.splitlines(), None, 0
	for line in lines:
		line, ignore = HandleComments(line, ignore)
		if not ignore:
			if not _jsonFixupPattern.match(line):
				fix = fix + line + '\n'
			else:
				strip = line.strip()
				pos = strip.find(':')
				if pos:
					fix = fix + "\"" + strip[:pos] + "\"" + strip[pos:] + '\n'
				else:
					fix = fix + line + '\n'
	return fix.strip()


def GetDictValueOr(dict, key, default):
	return key in dict and dict[key] or default


def GetDictValueOrDict(dict, key):
	return key in dict and dict[key] or {}


def GetDictValueOrList(dict, key):
	return key in dict and dict[key] or []


def GetDateString():
	return time.strftime('%d %b %Y')


def GetDateTimeString():
	return GetDateString() + ' ' + GetTimeString()


def GetHash(value):
	h = 0
	if isinstance(value, dict):
		for k in value:
			h = h ^ GetHash(k) ^ GetHash(value[k])
	elif IsIterable(value):
		for v in value:
			h = h ^ GetHash(v)
	elif hasattr(value, '__dict__'):
		for k in value.__dict__:
			h = h ^ GetHash(value.__dict__[k])
	else:
		h = hash(value)
	return h


def GetHexHash(value, algo = 'md5'):
	hasher = hashlib.new(algo)
	hasher.update(value)
	return hasher.hexdigest()


def GetTimeString():
	return time.strftime('%H:%M:%S')


def HandleComments(line, ignore):
	pos = line.find('/*')
	if pos >= 0:
		pos2 = line.find('*/')
		if pos2 < 0:
			line = line[:pos]
			ignore = ignore + 1
		elif pos2 > pos:
			line = line[:pos] + line[pos2 + 2:]
		elif pos2 < pos:
			line = line[pos2 + 2:pos]
	else:
		pos2 = line.find('*/')
		if pos2 >= 0:
			line = line[pos2 + 2:]
			ignore = ignore - 1
	return (line, ignore)


def HtmlEscape(value):
	value = value.replace('&', '&amp;')
	for k in _htmlEntities:
		value = value.replace(k, _htmlEntities[k])
	return value


def IsIterable(v):
	return hasattr(v, '__iter__')


def IsString(v):
	return isinstance(v, str) or isinstance(v, unicode)


def KillProcess(pid = 0, win = False):
	if win:
		os.popen('TASKKILL /PID ' + str(pid or os.getpid()) + ' /F')
	else:
		os.kill(pid or os.getpid(), signal.SIGKILL)


def ListContains(list, pred):
	return ListIndexOf(list, pred) >= 0


def ListHasValue(list, startIndex):
	if list:
		for i in xrange(startIndex, len(list)):
			if list[i]:
				return True
	return False


def ListIndexOf(list, pred):
	for i in xrange(0, len(list)):
		if pred(list[i]):
			return i
	return -1


def MapPath(relativePath):
	return os.path.join('/' + os.path.abspath(os.path.dirname(__file__) + '/..').strip('/'), relativePath.strip('/'))


def PlusMinus(test, val):
	if test:
		return abs(val)
	else:
		return -val


def PreprocessCcss(ccssRaw, imports):
	def convertColor(val):
		return (val != 0) and 1.0 / (255.0 / float(val)) or 0
	def processArgs(*args):
		retargs = []
		for arg in args:
			if isinstance(arg, list) and len(arg) == 4 and isinstance(arg[0], int) and isinstance(arg[1], int) and isinstance(arg[2], int) and isinstance(arg[3], float):
				retargs.append([convertColor(arg[0]), convertColor(arg[1]), convertColor(arg[2]), arg[3]])
			elif isinstance(arg, list):
				retargs.append(processArgs(*arg))
			else:
				retargs.append(arg)
		return retargs
	ccss, ignore = '', 0
	for line in ccssRaw.splitlines(True):
		line, ignore = HandleComments(line, ignore)
		if not ignore:
			if line.strip().startswith('$'):
				indent = line.find('$')
				line = ('\t' * indent) + line[indent + 1:]
				linestrip = line.strip()
				if linestrip.startswith('border-radius:'):
					indent = line.find('border-radius:')
					vals = line[line.find(':') + 1:].strip().split(' ')
					if vals and len(vals):
						if len(vals) == 1:
							vals = vals * 4
						names = ['border-top-left-radius', 'border-top-right-radius', 'border-bottom-right-radius', 'border-bottom-left-radius']
						prefixes = ['', '-webkit-', '-khtml-', '-moz-', '-opera-']
						for i in xrange(0, len(prefixes)):
							ccss = ccss + ('\t' * indent) + prefixes[i] + 'border-radius: %spx %spx %spx %spx\n' % (len(vals) > 0 and vals[0] or 0, len(vals) > 1 and vals[1] or 0, len(vals) > 2 and vals[2] or 0, len(vals) > 3 and vals[3] or 0)
						for i in xrange(0, len(vals)):
							if vals[i] and vals[i] != '0':
								for ip in xrange(0, len(prefixes)):
									ccss = ccss + ('\t' * indent) + prefixes[ip] + names[i] + ': ' + vals[i] + 'px\n'
				elif linestrip.startswith('image:'):
					ccss = ccss + ('\t' * indent) + 'image: url("' + DynGfx(linestrip[6:].strip().split(' ')[0].strip(), *processArgs(*simplejson.loads('[' + (' '.join(linestrip[6:].strip().split(' ')[1:])) + ']'))) + '")\n'
				elif linestrip.startswith('shadow-top:'):
					sc = linestrip[11:].strip()
					ccss = ccss + ('\t' * indent) + 'text-shadow: ' + sc + ' 0px "-1px" 0px\n'
					ccss = ccss + ('\t' * indent) + 'filter: "Shadow(Color=' + sc + ', Direction=0, Strength=1)"\n'
				elif linestrip.startswith('shadow-bottom:'):
					sc = linestrip[14:].strip()
					ccss = ccss + ('\t' * indent) + 'text-shadow: ' + sc + ' 0px "1px" 0px\n'
					ccss = ccss + ('\t' * indent) + 'filter: "Shadow(Color=' + sc + ', Direction=0, Strength=-1)"\n'
				elif linestrip.startswith('import:'):
					imports.append(linestrip[linestrip.find('import:') + 7:].strip())
			else:
				ccss = ccss + line
	return ccss


def SyncDict(target, source):
	for k, v in source.items():
		if k in target and type(target[k]) == dict and type(v) == dict:
			SyncDict(target[k], v)
		else:
			target[k] = v


def ToJson(obj, dump = True, dumpIndent = 4, dicFilter = None):
	dic = {}
	if type(obj) != dict:
		try:
			obj = obj.__dict__
		except:
			return obj
	for k, v in obj.items():
		if not dicFilter:
			dic[k] = ToJson(v, False, dumpIndent, dicFilter)
		else:
			f = dicFilter(k, v)
			if f[0]:
				dic[f[1]] = f[2]
	return dump and simplejson.dumps(dic, indent = dumpIndent) or dic


class AppServerError(Exception):
	def __init__(self, id, details, allowRetryContinue = True, status = ''):
		self.id = id
		self.details = details
		self.allowRetryContinue = allowRetryContinue
		self.status = status


class RedirectError(Exception):
	def __init__(self, location):
		self.Location = location

	def __str__(self):
		return self.Location


class RepeatTimer():
	def __init__(self, interval, delegate):
		def repeat(event, interval, delegate):
			while True:
				event.wait(interval)
				if event.isSet():
					break
				delegate()
		self.Event = threading.Event()
		self.Thread = threading.Thread(target = repeat, args = (self.Event, interval, delegate))

	def Start(self):
		self.Thread.start()

	def Stop(self):
		self.Event.set()


class Resources():
	def __init__(self, filePath):
		def escapeIf(value):
			return value.startswith('~~ ') and value[3:] or HtmlEscape(value)
		key, level, strip, self.Languages, self.Resources = '', 0, '', [], {}
		with open(filePath) as resFile:
			for line in resFile:
				strip = line.strip()
				if strip:
					if len(self.Languages):
						if line.startswith('\t\t'):
							self.Resources [self.Languages [level]] [key] = self.Resources [self.Languages [level]] [key] + ' ' + escapeIf(strip)
						elif line.startswith('\t'):
							level = level + 1
							self.Resources [self.Languages [level]] [key] = escapeIf(strip)
						else:
							key = strip
							level = -1
					else:
						self.Languages = map(lambda val: val.strip(), strip.split(' '))
						for lang in self.Languages:
							self.Resources[lang] = {}

	def __call__(self, name, *args):
		return self.Get(name, '', *args)

	def Get(self, name, lang = '', *args):
		if not lang or not lang in self.Languages:
			lang = self.PickLanguage()
		result = self.Resources [lang] [name]
		for i in range(0, len(args)):
			result = result.replace('{' + str(i) + '}', (args[i] != None) and str(args[i]) or '')
		return result

	def PickLanguage(self, lang = '', langs = []):
		langIndex, count, tmp = -1, 0, ''
		if not langs:
			try:
				langs = [locale.getdefaultlocale()[0]]
			except ValueError:
				langs = []
		if not lang or not lang in self.Languages:
			for l in langs:
				if l in self.Languages:
					langIndex = count
					break
				count = count + 1
			count = 0
			for l in langs:
				if l and l[:2] in self.Languages and count < langIndex:
					langIndex, tmp = count, l[:2]
					break
				count = count + 1
			count = 0
			for l in langs:
				for sl in self.Languages:
					if sl and sl[:2] == l and count < langIndex:
						tmp, langIndex = sl[:2], count
						break
				count = count + 1
		if tmp:
			lang = tmp
		elif langIndex >= 0:
			lang = langs[langIndex]
		if not lang or not lang in self.Languages:
			lang = self.Languages[0]
		return lang

	def WriteJavaScripts(self, pathPrefix):
		filePath, first = '', False
		for lc in self.Languages:
			filePath = pathPrefix + lc + '.js'
			with open(filePath, 'w') as jsFile:
				jsFile.write('$B.Resources.__Update("_", {')
				first = True
				for k in self.Resources[lc]:
					jsFile.write("%s\n%s: '%s'" % (not first and ',' or '', k, self.Resources[lc][k].replace("'", '\\\'')));
					first = False
				jsFile.write('\n});\n')


def UrlEscape(value):
	return urllib.pathname2url(value)
