from django import template
register = template.Library()

from django.template import Node, TemplateSyntaxError, Variable
from django.core.mail import mail_admins

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import struct
from urlparse import urljoin
from os import remove, rename
from os.path import join, abspath, exists, split
from pprint import pformat
from subprocess import Popen, PIPE
import cairo

from django.conf import settings

PARAM_KEYWORDS = set(
    ['font', 'size', 'baseline', 'height', 'color', 'background'])

_colors = {
    'aliceblue':'#f0f8ff','antiquewhite':'#faebd7','aqua':'#00ffff',
    'aquamarine':'#7fffd4','azure':'#f0ffff','beige':'#f5f5dc',
    'bisque':'#ffe4c4','black':'#000000','blanchedalmond':'#ffebcd',
    'blue':'#0000ff','blueviolet':'#8a2be2','brown':'#a52a2a',
    'burlywood':'#deb887','cadetblue':'#5f9ea0','chartreuse':'#7fff00',
    'chocolate':'#d2691e','coral':'#ff7f50','cornflowerblue':'#6495ed',
    'cornsilk':'#fff8dc','crimson':'#dc143c','cyan':'#00ffff',
    'darkblue':'#00008b','darkcyan':'#008b8b','darkgoldenrod':'#b8860b',
    'darkgray':'#a9a9a9','darkgreen':'#006400','darkkhaki':'#bdb76b',
    'darkmagenta':'#8b008b','darkolivegreen':'#556b2f','darkorange':'#ff8c00',
    'darkorchid':'#9932cc','darkred':'#8b0000','darksalmon':'#e9967a',
    'darkseagreen':'#8fbc8f','darkslateblue':'#483d8b',
    'darkslategray':'#2f4f4f','darkturquoise':'#00ced1','darkviolet':'#9400d3',
    'deeppink':'#ff1493','deepskyblue':'#00bfff','dimgray':'#696969',
    'dodgerblue':'#1e90ff','firebrick':'#b22222','floralwhite':'#fffaf0',
    'forestgreen':'#228b22','fuchsia':'#ff00ff','gainsboro':'#dcdcdc',
    'ghostwhite':'#f8f8ff','gold':'#ffd700','goldenrod':'#daa520',
    'gray':'#808080','green':'#008000','greenyellow':'#adff2f',
    'honeydew':'#f0fff0','hotpink':'#ff69b4','indianred':'#cd5c5c',
    'indigo':'#4b0082','ivory':'#fffff0','khaki':'#f0e68c',
    'lavender':'#e6e6fa','lavenderblush':'#fff0f5','lawngreen':'#7cfc00',
    'lemonchiffon':'#fffacd','lightblue':'#add8e6','lightcoral':'#f08080',
    'lightcyan':'#e0ffff','lightgoldenrodyellow':'#fafad2',
    'lightgreen':'#90ee90','lightgrey':'#d3d3d3','lightpink':'#ffb6c1',
    'lightsalmon':'#ffa07a','lightseagreen':'#20b2aa','lightskyblue':'#87cefa',
    'lightslategray':'#778899','lightsteelblue':'#b0c4de',
    'lightyellow':'#ffffe0','lime':'#00ff00','limegreen':'#32cd32',
    'linen':'#faf0e6','magenta':'#ff00ff','maroon':'#800000',
    'mediumaquamarine':'#66cdaa','mediumblue':'#0000cd',
    'mediumorchid':'#ba55d3','mediumpurple':'#9370db',
    'mediumseagreen':'#3cb371','mediumslateblue':'#7b68ee',
    'mediumspringgreen':'#00fa9a','mediumturquoise':'#48d1cc',
    'mediumvioletred':'#c71585','midnightblue':'#191970','mintcream':'#f5fffa',
    'mistyrose':'#ffe4e1','moccasin':'#ffe4b5','navajowhite':'#ffdead',
    'navy':'#000080','oldlace':'#fdf5e6','olive':'#808000',
    'olivedrab':'#6b8e23','orange':'#ffa500','orangered':'#ff4500',
    'orchid':'#da70d6','palegoldenrod':'#eee8aa','palegreen':'#98fb98',
    'paleturquoise':'#afeeee','palevioletred':'#db7093','papayawhip':'#ffefd5',
    'peachpuff':'#ffdab9','peru':'#cd853f','pink':'#ffc0cb','plum':'#dda0dd',
    'powderblue':'#b0e0e6','purple':'#800080','red':'#ff0000',
    'rosybrown':'#bc8f8f','royalblue':'#4169e1','saddlebrown':'#8b4513',
    'salmon':'#fa8072','sandybrown':'#f4a460','seagreen':'#2e8b57',
    'seashell':'#fff5ee','sienna':'#a0522d','silver':'#c0c0c0',
    'skyblue':'#87ceeb','slateblue':'#6a5acd','slategray':'#708090',
    'snow':'#fffafa','springgreen':'#00ff7f','steelblue':'#4682b4',
    'tan':'#d2b48c','teal':'#008080','thistle':'#d8bfd8','tomato':'#ff6347',
    'turquoise':'#40e0d0','violet':'#ee82ee','wheat':'#f5deb3',
    'white':'#ffffff','whitesmoke':'#f5f5f5','yellow':'#ffff00',
    'yellowgreen':'#9acd32'}

def convert_color(s):
    if not isinstance(s, basestring):
        return s
    if not s.startswith('#'):
        s = _colors[s]
    l = len(s)
    if l in (4, 5):
        c = [int(x*2, 16)/255.0 for x in s[1:]]
    elif l in (7, 9):
        c = [int(s[i:i+2], 16)/255.0 for i in range(1, l, 2)]
    else:
        raise ValueError('color %r has invalid length' % s)
    if len(c) < 4:
        c.append(1)
    return tuple(c)

def read_png_chunk(pngfile):
    "Read a PNG chunk from the input file, return tag name and data."
    # http://www.w3.org/TR/PNG/#5Chunk-layout
    data_bytes, tag = struct.unpack('!I4s', pngfile.read(8))
    data = pngfile.read(data_bytes)
    return tag, data

def get_png_size(filepath):
    pngfile = file(filepath, 'rb')
    signature = pngfile.read(8)
    if (signature != struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10)):
        raise ValueError("Invalid PNG signature")
    while True:
        try:
            tag, data = read_png_chunk(pngfile)
        except ValueError, e:
            raise ValueError('Invalid PNG file: ' + e.args[0])
        if tag == 'IHDR': # http://www.w3.org/TR/PNG/#11IHDR
            return struct.unpack("!2I5B", data)[:2]
    raise ValueError('PNG header not found')

def render_text(text, filepath, params):
    size = params.get('size', 18)
    weight = cairo.FONT_WEIGHT_NORMAL
    style = cairo.FONT_SLANT_NORMAL
    font = params.get('font', 'Sans')

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
    context = cairo.Context(surface)
    context.select_font_face(font, style, weight)
    context.set_font_size(size)
    extents = context.text_extents(text)
    x = -extents[0]
    baseline = params.get('baseline', -extents[1])
    width = max(1, extents[2])
    height = max(1, params.get('height', extents[3]))

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    font_options = surface.get_font_options()
    font_options.set_antialias(cairo.ANTIALIAS_GRAY)
    context = cairo.Context(surface)

    # Paint the background, default is white.
    background = convert_color(params.get('background', (1, 1, 1, 1)))
    context.set_source_rgba(*background)
    context.paint()

    color = convert_color(params.get('color', (0, 0, 0, 1))) # black
    context.set_source_rgba(*color)

    context.select_font_face(font, style, weight)
    context.set_font_size(size)
    # We need to adjust by the text's offsets to center it.
    context.move_to(x, baseline)
    # We stroke and fill to make sure thinner parts are visible.
    context.text_path(text)
    #context.set_line_width(0.05)
    #context.stroke_preserve()
    context.fill()

    filepath = abspath(filepath)
    try:
        surface.write_to_png(filepath)
    except IOError, e:
        raise IOError("Can't save image in %r: %s\n"
                      "Text: %r\n"
                      "Parameters: %r" % (filepath, e, text, params))
    optimizer = Optimizer()
    if optimizer.is_enabled():
        optimizer.optimize(filepath)
    surface.finish()

    return int(width), int(height)

class OptimizerError(Exception): pass

class Optimizer(object):
    def __init__(self):
        self.cmdline_template = getattr(
            settings, 'CAIROTEXT_OPTIMIZER', None)
        self.dest_path_template = getattr(
            settings, 'CAIROTEXT_OPTIMIZED_PATH', None)

    def is_enabled(self):
        return self.cmdline_template and self.dest_path_template

    def optimize(self, filepath):
        self.filepath = filepath
        params = self.get_params_for(filepath)
        self.cmdline = self.cmdline_template % params
        self.dest_path = self.dest_path_template % params
        process = Popen(self.cmdline, shell=True, stdout=PIPE, stderr=PIPE)
        self.stdout, self.stderr = process.stdout.read(), process.stderr.read()
        self.retval = process.wait()
        if self.retval:
            self.error('Cairotext external optimizer failure')
        elif not exists(self.dest_path):
            self.error('Cairotext optimized image missing')
        elif self.stdout or self.stderr:
            if not self.stderr.startswith('libpng warning: '):
                self.error('Cairotext optimizer output')
        if exists(self.dest_path):
            # os.rename overwrites existing destination
            rename(self.dest_path, filepath)

    def get_params_for(self, filepath):
        directory, filename = split(filepath)
        name, ext = filename.rsplit('.', 1)
        return {'path': filepath,
                'directory': directory,
                'name': name,
                'ext': ext}

    def error(self, subject):
        message = (
            'Original PNG path: %s\n'
            'Optimized PNG path: %s\n'
            'Optimizer command line: %s\n'
            'Optimizer return value: %d\n%s%s' % (
                self.filepath, self.dest_path, self.cmdline,
                self.retval, self.stdout, self.stderr))
        if settings.DEBUG:
            raise OptimizerError(message)
        else:
            mail_admins(subject, message, fail_silently=True)

class TextImage(object):
    def __init__(self, url, path, size):
        self.url = url
        self.path = path
        self.width, self.height = size
    def _embed(self):
        if not hasattr(self, '_base64'):
            self._base64 = ('data:image/png;base64,%s' %
                            file(self.path).read().encode('base64')[:-1])
        return self._base64
    embed = property(_embed)

class GetTextImageNode(Node):
    def __init__(self, base_params, text, overrides, varname):
        self.base_params = base_params
        self.text = text
        self.overrides = overrides
        self.varname = varname
    def render(self, context):
        params = {}
        if self.base_params is not None:
            params = self.base_params.resolve(context)
        if isinstance(params, basestring):
            try:
                presets = settings.CAIROTEXT_PRESETS
                params = dict(presets[params])
            except (AttributeError, KeyError):
                raise KeyError('Preset "%s" not found in '
                               'settings.CAIROTEXT_PRESETS' % params)
        params.update(dict((key, val.resolve(context))
                           for key, val in self.overrides.items()))
        text = self.text.resolve(context)
        name = md5(text.encode('UTF-8') + pformat(params)).hexdigest()
        render_dir = getattr(settings, 'CAIROTEXT_DIR', 'cairotext_cache')
        filename = '%s.png' % name
        fileurl = urljoin(settings.MEDIA_URL, join(render_dir, filename))
        filepath = join(settings.MEDIA_ROOT, render_dir, filename)
        size = None
        if not exists(filepath):
            size = render_text(text, filepath, params)
        pngsize = get_png_size(filepath)
        assert size is None or size == pngsize, \
            'size mismatch: expected %rx%r, got %rx%r' % (size+pngsize)

        context[self.varname] = TextImage(fileurl, filepath, pngsize)
        return ''

def compile(parser, value):
    if value[0] in '-0123456789':
        return Variable(value)
    return parser.compile_filter(value)

def do_get_text_image(parser, token):
    """
    To use presets from settings.CAIROTEXT_PRESETS['base_params'] and
    override text color, use:

    {% get_text_image "Text" color "#aaa" font "Sans" height 20 as img %}
    <img src="{{img.url}}" width="{{img.width}}" height="{{img.height}}" />
    """
    bits = token.split_contents()
    count = len(bits)
    if count < 4:
        raise TemplateSyntaxError('%r expects at least 3 arguments')
    if bits[-2] != 'as':
        raise TemplateSyntaxError('%r expects "as" as its '
                                  'second last argument')
    text = parser.compile_filter(bits[1])
    base_params = None
    if count % 2:
        base_params = parser.compile_filter(bits[2])
    overrides = dict((keyword, compile(parser, value))
                     for keyword, value in zip(bits[2+count%2:-2:2], bits[3+count%2:-2:2]))
    varname = bits[-1]

    unknown_keywords = set(overrides.keys()).difference(PARAM_KEYWORDS)
    if unknown_keywords:
        raise TemplateSyntaxError('%r got unknown keywords %s' % (
                bits[0],
                ', '.join(unknown_keywords)))
    return GetTextImageNode(base_params, text, overrides, varname)
do_get_text_image = register.tag('get_text_image', do_get_text_image)
