# -*- coding: utf-8 -*-
from os import remove, rmdir
from os.path import exists, join, getsize
from glob import glob
from tempfile import mkdtemp
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from django.test import TestCase
from django.conf import settings
from django.template import Template, Context
import Image
from cairotext.templatetags.cairotext import render_text

CACHE_DIR = join(settings.MEDIA_ROOT, 'cairotext_cache')

## uncomment to keep cache after running tests
#remove = lambda s: None
#rmdir = lambda s: None

class ColorTestCase(TestCase):
    pairs = (('#aaa', '0.667 0.667 0.667 1.000'),
             ('indigo', '0.294 0.000 0.510 1.000'),
             ('#fffefd', '1.000 0.996 0.992 1.000'),
             ('#036f', '0.000 0.200 0.400 1.000'),
             ('#9ab34f82', '0.604 0.702 0.310 0.510'))
    def test_convert_color(self):
        from cairotext.templatetags.cairotext import convert_color
        for html, colortuple in self.pairs:
            rgba = '%.3f %.3f %.3f %.3f' % convert_color(html)
            assert rgba == colortuple, \
                '%s -> %s (not %r)' % (html, rgba, colortuple)

def quote(s):
    if isinstance(s, basestring):
        return '"%s"' % s
    return repr(s)

class TemplateTagTestCase(TestCase):
    def test_01_render_text(self):
        directory = mkdtemp()
        filepath = join(directory, 'test.png')
        width, height = render_text('Test text', filepath, {})
        assert width == 80, width
        assert height == 13, height
        self.assertImageSize(filepath, (80, 13))
        self.assertImageFingerprint(
            filepath, '00fe21170617c1fde94d0113e26c7f7e')
        remove(filepath)
        rmdir(directory)

    def test_02_size(self):
        self.assertCairoText('Test text', size=20,
                             hash='bc35d3f66298f31363d56c5dd10c29ea',
                             image_size=(87, 15))

    def test_03_color(self):
        self.assertCairoText('Test text', color='#5a5a63',
                             hash='ecbcb66c8b62c7068df90a9bc5110804',
                             image_size=(80, 13))

    def test_04_background_color(self):
        self.assertCairoText('Test text', background='#b5b5b5',
                             hash='5e3d6ebdfc3becde25f7206d2deca066',
                             image_size=(80, 13))

    def test_05_height(self):
        self.assertCairoText('Test text', height=20,
                             hash='d026d70faf9ccfbaf46f69ece5497ed2',
                             image_size=(80, 20))

    def test_06_y(self):
        self.assertCairoText('Test text', height=20, y=15,
                             hash='ef07950cde55c1a371a7b13a954a1e9f',
                             image_size=(80, 20))

    def test_07_font1(self):
        self.assertCairoText('ÄIBÖ'.decode('UTF-8'), font='Serif',
                             height=19, y=15,
                             hash='51a648393678504100249d26a46228ce',
                             image_size=(48, 19))

    def test_08_font2(self):
        self.assertCairoText('AIBO', font='Serif',
                             height=19, y=15,
                             hash='e0ed3c72f26e2d174fa4296d99676d87',
                             image_size=(48, 19))

    def test_09_font3(self):
        self.assertCairoText('AIJO', font='Serif',
                             height=19, y=15,
                             hash='519ae8585da4a569869d122bbe6b5f15',
                             image_size=(42, 19))

    def test_10_font4(self):
        self.assertCairoText('ÄIJÖ'.decode('UTF-8'), font='Frutiger LT Std',
                             height=19, y=15, size=12,
                             color='#fff', background='#b5b5b5',
                             hash='d0c933357a1723b9c07da6b3da98248d',
                             image_size=(24, 19))

    def test_11_format(self):
        self.assertCairoText('Test text', format='gif',
                             hash='00fe21170617c1fde94d0113e26c7f7e',
                             image_size=(80, 13))

    def test_12_multiple(self):
        self.assertCairoText('ÄIJÖ'.decode('UTF-8'), font='Serif',
                             height=19, y=15, size=12,
                             color='#fff', background='#b5b5b5',
                             hash='184bcf51e19d4e48d198ef6381e86821',
                             image_size=(27, 19))

    def test_13_missing_base_settings(self):
        self.assertRaises(KeyError,
                          self.assertCairoText,
                          'text', base='"dummy"', hash='', image_size=())

    def test_14_base_settings(self):
        self.assertCairoText('Test text', base='"fancy"',
                             hash='ed88e6b683afd6fd6c0caa16776fd36d',
                             image_size=(179, 29))

    def test_15_base_settings_override(self):
        self.assertCairoText('Test text', base='"fancy"', size=8,
                             hash='bc056ad38119a791d138e18623b73a50',
                             image_size=(36, 6))

    def assertImageSize(self, filepath, size):
        img = Image.open(filepath)
        self.assertEqual(img.size, size)

    def assertImageFingerprint(self, filepath, hash):
        imghash = md5(Image.open(filepath).tostring()).hexdigest()
        self.assertEqual(imghash, hash)

    def assertCairoText(self, text, hash, image_size, base='', **params):
        for filepath in glob(join(CACHE_DIR, '*')):
            remove(filepath)
        paramstr = ' '.join('%s %s' % (key, quote(val))
                            for key, val in params.items())
        template_string = (
            '{%% load cairotext %%}'
            '{%% get_text_image "%s" %s %s as i %%}'
            '<img src="{{i.url}}"'
            ' width="{{i.width}}"'
            ' height="{{i.height}}" />' % (text, base, paramstr))
        template = Template(template_string)
        result = template.render(Context())
        path = result[17:69]
        filepath = join(settings.MEDIA_ROOT, path)
        self.assertImageSize(filepath, image_size)
        self.assertImageFingerprint(filepath, hash)
        remove(filepath)
