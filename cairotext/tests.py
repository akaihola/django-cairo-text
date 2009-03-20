# -*- coding: utf-8 -*-
from os import remove, rmdir
from os.path import exists, join, getsize, dirname
from glob import glob
from tempfile import mkdtemp
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.template import Template, Context
import Image
from cairotext.templatetags.cairotext import \
    render_text, Optimizer, OptimizerError
from cairotext.test_optimizer import TEST_IMAGE

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
                             image_size=(87, 15),
                             filesize=961)

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

    def test_06_baseline(self):
        self.assertCairoText('Test text', height=20, baseline=15,
                             hash='ef07950cde55c1a371a7b13a954a1e9f',
                             image_size=(80, 20))

    def test_07_font1(self):
        self.assertCairoText('ÄIBÖ'.decode('UTF-8'), font='Serif',
                             height=19, baseline=15,
                             hash='51a648393678504100249d26a46228ce',
                             image_size=(48, 19))

    def test_08_font2(self):
        self.assertCairoText('AIBO', font='Serif',
                             height=19, baseline=15,
                             hash='e0ed3c72f26e2d174fa4296d99676d87',
                             image_size=(48, 19))

    def test_09_font3(self):
        self.assertCairoText('AIJO', font='Serif',
                             height=19, baseline=15,
                             hash='519ae8585da4a569869d122bbe6b5f15',
                             image_size=(42, 19))

    def test_10_font4(self):
        self.assertCairoText('ÄIJÖ'.decode('UTF-8'), font='Frutiger LT Std',
                             height=19, baseline=15, size=12,
                             color='#fff', background='#b5b5b5',
                             hash='d0c933357a1723b9c07da6b3da98248d',
                             image_size=(24, 19))

    def test_11_multiple(self):
        self.assertCairoText('ÄIJÖ'.decode('UTF-8'), font='Serif',
                             height=19, baseline=15, size=12,
                             color='#fff', background='#b5b5b5',
                             hash='184bcf51e19d4e48d198ef6381e86821',
                             image_size=(27, 19))

    def test_12_missing_base_settings(self):
        self.assertRaises(KeyError,
                          self.assertCairoText,
                          'text', base='"dummy"', hash='', image_size=())

    def test_13_base_settings(self):
        self.assertCairoText('Test text', base='"fancy"',
                             hash='ed88e6b683afd6fd6c0caa16776fd36d',
                             image_size=(179, 29))

    def test_14_base_settings_override(self):
        self.assertCairoText('Test text', base='"fancy"', size=8,
                             hash='bc056ad38119a791d138e18623b73a50',
                             image_size=(36, 6))

    def test_15_cache(self):
        """
        An existing file in the cache shouldn't be replaced.  Render some text
        as an image, replace the cached file with another image, render again
        and make sure the image wasn't overwritten by checking that the
        appended byte is still there.
        """
        filepath1 = self.assertCairoText(
            'Test text', delete=False,
            hash='00fe21170617c1fde94d0113e26c7f7e',
            image_size=(80, 13))
        Image.new('RGBA', (10, 10)).save(filepath1)
        filepath2 = self.assertCairoText(
            'Test text', delete=False,
            hash='a75d7d422fd00bf31208b013e74d8394',
            image_size=(10, 10))
        self.assertEqual(filepath1, filepath2)
        remove(filepath2)

    def test_16_embed(self):
        template_string = (
            '{% load cairotext %}'
            '{% get_text_image "text" as i %}'
            '<!-- {{i.path}} -->'
            '<img src="{{i.embed}}" width="{{i.width}}" height="{{i.height}}" />')
        template = Template(template_string)
        result = template.render(Context())
        path, img_tag = result[5:].split(' -->')
        self.assertEqual(
            img_tag,
            u'<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAANCAYAAAAjf9cfAAAABmJLR0QA/wD/AP+gvaeTAAACQ0lE\n'
            u'QVQ4jc2TMUvyURTGn/uaLkE0SAQmDg4OhURWU0NfIVCk+gYtITT4DfoAbdoiFEJtLbUEDSHUFM7S\n'
            u'5pBSGpKi/f3/3iG89M+/ve+7xPvAGe45557n4bn3GABjjCQJ0E/Bj/PXj7H/Bf4vMSO7pA/rRjEC\n'
            u'oJOTE21ubmp2dlbBYFDxeFwHBwdqt9u2b3t7W8YYJZNJua5r867rKplMyhij3d1dyzOJE78AcF2X\n'
            u'nZ0d37okFhcXabfbADw/PxOJRJBEuVxmhHK5jCRisRitVgs+Pol/fC5+RaFQQBILCwucnZ3RaDTo\n'
            u'9XpUKhVSqRSSyOfztv/q6gpjDIlEAsdxcByHRCJBIBDg5ubGM9uP81sx6+vrSOL29nasVqvVkEQ8\n'
            u'Hvfk9/b2kESpVKJUKo0J/k6MgcmrPT09rW63++2nC4VC6vf79vz29qbl5WU7a2ZmRnd3dwoGg557\n'
            u'/7zaX8X5YTAYeM6dTkcvLy96f39Xs9lUvV7X6+vrH+eMCJmamkISjuN4bFtdXUUS9/f3YzZPwtbW\n'
            u'ln2mw8NDJJHNZsf6/DgFEI1GkcTl5SXD4dAWj4+PkcT8/DzFYpHHx0e63S6tVouHhweOjo5IpVK2\n'
            u'f7Q5S0tLDIdDer0esVgMSZyfn3vE+HEKIJPJTFzt/f39yav4qffp6YlwOIwkLi4uLOnp6SmSmJub\n'
            u'o9ls2rwfpwDq9TqZTIZoNGrt+4zr62tbD4VChMNhVlZWyOVyVKtVANLpNJLY2Njw3HVdl7W1NSSR\n'
            u'Tqdt3o/zN0UNzMzUv9N1AAAAAElFTkSuQmCC" width="35" height="13" />')
        remove(path)

    def test_17_pngnq(self):
        settings.CAIROTEXT_OPTIMIZER = 'pngnq -n 4 %(path)s'
        settings.CAIROTEXT_OPTIMIZED_PATH = '%(directory)s/%(name)s-nq8.png'
        try:
            self.assertCairoText('Test text', size=20,
                                 hash='dae8857d033198914b596d4869a3106c',
                                 image_size=(87, 15),
                                 filesize=281L)
            self.assertEqual(len(mail.outbox), 0)
        except OSError, e:
            if e.args != (2, 'No such file or directory'):
                raise
        self.reset_optimizer_settings()

    def test_18_optimize(self):
        self.set_test_optimizer_settings()
        self.assertCairoText('text', size=18,
                             hash='885fd961af65b1f31c08c3f4942884fd',
                             image_size=(35, 13),
                             filesize=654L)
        self.assertEqual(len(mail.outbox), 0)
        self.reset_optimizer_settings()

    def test_19_optimize_fail(self):
        self.set_test_optimizer_settings('-f')
        self.assertCairoText('text', size=18,
                             hash='885fd961af65b1f31c08c3f4942884fd',
                             image_size=(35, 13),
                             filesize=654L)
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(
            m.subject, '[Django] Cairotext external optimizer failure')
        self.assertEqual(
            m.body,
            'Original PNG path: media/cairotext_cache/'
            '47ce8fb8dc6517ea07aaede77935703a.png\n'
            'Optimized PNG path: media/cairotext_cache/'
            '47ce8fb8dc6517ea07aaede77935703a-optimized.png\n'
            'Optimizer command line:'
            ' python ../cairotext/test_optimizer.py -f'
            ' media/cairotext_cache/47ce8fb8dc6517ea07aaede77935703a.png\n'
            'Optimizer return value: 1\n')
        self.reset_optimizer_settings()

    def test_20_optimize_missing(self):
        self.set_test_optimizer_settings('-n')
        self.assertCairoText('text', size=18,
                             hash='885fd961af65b1f31c08c3f4942884fd',
                             image_size=(35, 13),
                             filesize=654L)
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(
            m.subject, '[Django] Cairotext optimized image missing')
        self.assertEqual(
            m.body,
            'Original PNG path: media/cairotext_cache/'
            '47ce8fb8dc6517ea07aaede77935703a.png\n'
            'Optimized PNG path: media/cairotext_cache/'
            '47ce8fb8dc6517ea07aaede77935703a-optimized.png\n'
            'Optimizer command line:'
            ' python ../cairotext/test_optimizer.py -n'
            ' media/cairotext_cache/47ce8fb8dc6517ea07aaede77935703a.png\n'
            'Optimizer return value: 0\n')
        self.reset_optimizer_settings()

    def set_test_optimizer_settings(self, options=''):
        settings.CAIROTEXT_OPTIMIZER = 'python %s %s %%(path)s' % (
            '../cairotext/test_optimizer.py', options)
        settings.CAIROTEXT_OPTIMIZED_PATH = (
            '%(directory)s/%(name)s-optimized.png')

    def reset_optimizer_settings(self):
        settings.CAIROTEXT_OPTIMIZER = None
        settings.CAIROTEXT_OPTIMIZED_PATH = None

    def assertImageSize(self, filepath, size):
        img = Image.open(filepath)
        self.assertEqual(img.size, size)

    def assertImageFingerprint(self, filepath, hash):
        imghash = md5(Image.open(filepath).tostring()).hexdigest()
        self.assertEqual(imghash, hash)

    def assertFileSize(self, filepath, size):
        self.assertEqual(getsize(filepath), size)

    def assertCairoText(self, text, hash, image_size, base='', delete=True,
                        filesize=None, **params):
        if delete:
            for filepath in glob(join(CACHE_DIR, '*')):
                remove(filepath)
        paramstr = ' '.join('%s %s' % (key, quote(val))
                            for key, val in params.items())
        template_string = (
            '{%% load cairotext %%}'
            '{%% get_text_image "%s" %s %s as i %%}'
            '<!-- {{i.path}} -->'
            '<img src="{{i.url}}"'
            ' width="{{i.width}}"'
            ' height="{{i.height}}" />' % (text, base, paramstr))
        template = Template(template_string)
        result = template.render(Context())
        path = result[5:].split(' -->')[0]
        filepath = path
        self.assertImageSize(filepath, image_size)
        self.assertImageFingerprint(filepath, hash)
        if filesize is not None:
            self.assertFileSize(filepath, filesize)
        if delete:
            remove(filepath)
        else:
            return filepath

class OptimizerTestCase(TestCase):

    def setUp(self):
        settings.CAIROTEXT_OPTIMIZER = (
            'python ../cairotext/test_optimizer.py %(path)s')
        settings.CAIROTEXT_OPTIMIZED_PATH = (
            '%(directory)s/%(name)s-optimized.png')

    def tearDown(self):
        settings.CAIROTEXT_OPTIMIZER = None
        settings.CAIROTEXT_OPTIMIZED_PATH = None

    def test_01_params(self):
        o = Optimizer()
        params = o.get_params_for('/absolute/path/filename.png')
        self.assertEqual(params, {'directory': '/absolute/path',
                                  'path': '/absolute/path/filename.png',
                                  'ext': 'png',
                                  'name': 'filename'})

    def test_02_error(self):
        o = Optimizer()
        o.filepath = '/absolute/path/filename.png'
        params = o.get_params_for(o.filepath)
        o.cmdline = o.cmdline_template % params
        o.dest_path = o.dest_path_template % params
        o.retval = 1
        o.stdout = 'test stdout content\n'
        o.stderr = 'test stderr content\n'
        o.error('test subject')
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(
            m.subject, '[Django] test subject')
        self.assertEqual(
            m.body,
            'Original PNG path: /absolute/path/filename.png\n'
            'Optimized PNG path: /absolute/path/filename-optimized.png\n'
            'Optimizer command line:'
            ' python ../cairotext/test_optimizer.py'
            ' /absolute/path/filename.png\n'
            'Optimizer return value: 1\n'
            'test stdout content\n'
            'test stderr content\n')

    def test_03_error_debug(self):
        settings.DEBUG = True
        o = Optimizer()
        o.filepath = '/absolute/path/filename.png'
        params = o.get_params_for(o.filepath)
        o.cmdline = o.cmdline_template % params
        o.dest_path = o.dest_path_template % params
        o.retval = 1
        o.stdout = 'test stdout content\n'
        o.stderr = 'test stderr content\n'
        try:
            o.error('test subject')
            self.fail('o.error did not raise exception')
        except Exception, e:
            assert isinstance(e, OptimizerError), e
            self.assertEquals(
                e.message,
                'Original PNG path: /absolute/path/filename.png\n'
                'Optimized PNG path: /absolute/path/filename-optimized.png\n'
                'Optimizer command line:'
                ' python ../cairotext/test_optimizer.py'
                ' /absolute/path/filename.png\n'
                'Optimizer return value: 1\n'
                'test stdout content\n'
                'test stderr content\n')
        self.assertEqual(len(mail.outbox), 0)
        settings.DEBUG = False

    def test_04_optimizer_enabled(self):
        self.assert_(Optimizer().is_enabled())

    def test_05_optimize(self):
        directory = mkdtemp()
        filepath = join(directory, 'test.png')
        file(filepath, 'w').write('dummy')
        o = Optimizer()
        o.optimize(filepath)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEquals(file(filepath).read(), TEST_IMAGE)
        remove(filepath)
        rmdir(directory)
