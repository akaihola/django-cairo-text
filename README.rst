===================
 django-cairo-text
===================

This is a re-usable Django app for using custom fonts on a web page
for headings, navigation and the like.  It uses the Cairo graphics
library to create images dynamically out of text snippets.  Currently
output in the PNG format is possible since that's all Cairo supports.
You can create ``<img>`` tags which either link to cached image files
or embed encoded image data in the ``src=`` attribute.


Downloads
=========

Use the `django-cairo-text GitHub repository`_ to download the app.

.. _django-cairo-text GitHub repository: http://github.com/akaihola/django-cairo-text/


Dependencies
============

Cairotext uses the PyCairo library so you need to have that and the
Cairo libraries installed along with any fonts you'd like to use.


Quickstart
==========

The template tag ``get_text_image`` generates the image and saves its
URL and pixel size in the context::

  {% load cairotext %}
  {% get_text_image myvar font "Arial" color "#ab3fd0" size 14 as img %}
  Image retrieved with a separate request:
  <img src="{{img.url}}" alt="{{myvar}}"
       width="{{img.width}}" height="{{img.height}}" />
  Image data embedded in HTML:
  <img src="{{img.embed}}" alt="{{myvar}}"
       width="{{img.width}}" height="{{img.height}}" />

You can use the following keywords to customize the appearance of the
text:

* ``font`` (name of typeface)
* ``size`` (font size in pixels)
* ``height`` (image height in pixels)
* ``baseline`` (text baseline in pixels from top of image)
* ``background`` (background color, HTML format)
* ``color`` (text color, HTML format)

Presets can be provided in the Django settings file, and they can be
used and overridden in the template tag.

Behind the scenes, django-cairo-text checks if the image already has
been rendered. If not, a new image is generated and saved to
disk.




Author
======

The original author is `Antti Kaihola`_ of Ambitone Oy.  Ambitone Oy
is a small Finnish new media and web development house which focuses
on Django in its web projects.

.. _Antti Kaihola: http://djangopeople.net/akaihola


Installation
============

Put the cairotext app in your Python path.  Then add 'cairotext' to
INSTALLED_APPS in settings.py.  If you want to customize the defaults,
you can include ``CAIROTEXT_DIR`` (default is ``cairotext_cache``
inside your ``MEDIA_ROOT``) and ``CAIROTEXT_PRESETS`` as well::

  INSTALLED_APPS = (
    # [...]
    'cairotext',)
  CAIROTEXT_DIR = 'cairotext_cache'
  CAIROTEXT_PRESETS = dict(
    fancy=dict(
        font='Arial',
        size=40,
        background='#fc8',
        color='#630',
	height=60,
        baseline=50))


Usage
=====

To show text with a custom font, first load the tag library with ``{%
load cairotext %}`` and then render the image using the
``get_text_image`` template tag::

  {% get_text_image page.title font "jiffy" as img %}

Similarly for string literals::

  {% get_text_image "Hello there!" font "jiffy" as img %}

You can specify font size and color, too::

  {% get_text_image "Hello there!" font "jiffy" size 18 as img %}

Colors are specified with a standard CSS specification. So you can get
green text either::

  {% get_text_image "Hello there!" font "jiffy" color "#00ff00" as img %}

or::

  {% get_text_image "Hello there!" font "jiffy" color "green" as img %}

You can also specify the background color::
  
  {% get_text_image "Hello there!" font "jiffy" color "#0f0" background "black" as img %}

The template tag returns an image object with attributes like this::

  img.url == '/media/cairotext_cache/ba5bfc5b16f25c44bd242230056be56b.png'
  img.embed == (
    'data:image/png;base64,'
    'iVBORw0KGgoAAAANSUhEUgAAAFUAAAAJCAMAAAB0Z5DkAAAAGFBMVEX+/v7+/v79/f3t7e3Hx8eZ\n'
    'mZlSUlIdHR3QDIZLAAAAi0lEQVQoz7VS0Q6DQAgjetD//2OBAjExbkucPFDo2Sp4In8IXBmPF1y/\n'
    'nD9xBUwM+d0KqMCCz1KjVhLdJO3JOKeTOjpiOUGyq5VgbTLlqhTMNGjJsKUjDr2pdzsNa4Isb1zj\n'
    'LCScF6MjhrXFYNyCrHkXy5sN8DGXtGvr1o+/X9HphI/vTSyvNjj4OQ72GgXnYsLNkAAAAABJRU5E\n'
    'rkJggg==')
  img.width == 85
  img.height == 9

Bold or italic text is not directly supported - I haven't looked into
such features in Cairo yet.  You can of course use a bold or italic
version of the font file.

PNG issues
----------

Note that cairotext is able to spit out PNGs with transparency.  To
show these properly in IE 5.5+ and 6, you need to apply the Javascript
IE PNG hack (if you're using a popular Javascript base library,
there's probably a plugin for this).

Caching
-------

If you change the font file or something similar that the caching
mechanism in cairotext is not clever enough to detect, you can simply
delete the generated files. They will then be regenerated. The caching
mechanism doesn't use the database, it only looks at what's available
in the file system.

Presets
-------

In accordance with the DRY principle, you can specify presets in the
Django settings.py file for font settings you use frequently in your
templates.

The ``CAIROTEXT_PRESETS`` dictionary should contain preset names as
keys and rendering option dictionaries as values.  A useful pattern
for inheriting options is to use a function::

  def navi(**kwargs):
      params = dict(
          font='Frutiger LT Std',
          size=14,
          height=14,
          baseline=14,
          color='#5a5a63',
          background='white')
      params.update(kwargs)
      return params
  
  CAIROTEXT_PRESETS = dict(
      navigation=navi(background='#b5b5b5'),
      navigation_hover=navi(background='#b5b5b5', color='white'),
      section_menu=navi(background='#d3d2d2'),
      section_menu_hover=navi(background='#e4e4e4'),
      body_h1=dict(font='Arial', size=16, height=16, baseline=16, color='#505050'))

Use presets in templates by inserting the preset name after the text
to be rendered.  Options can still be overridden::

  {% get_text_image mytext "navigation" color "green" as img %}

This would render green 14px Frutiger on a gray background.

Image optimization
------------------

You might want to optimize the size of generated PNG files in order to
minimize network traffic.  An external optimizer utility can be called
automatically for each generated image.  Two settings have to be
defined:

* CAIROTEXT_OPTIMIZER defines the command line for the optimizer
  binary

* CAIROTEXT_OPTIMIZED_PATH defines where the optimizer saves the
  optimized image

Both settings can contain Python-style named string formatting
specifiers which refer to the following values:

* ``%(path)s``: full path of the final PNG file

* ``%(directory)s``: path of the directory where the PNG is to be
  saved

* ``%(name)s``: image name without the extension

* ``%(ext)s``: always 'png'

An example::

  CAIROTEXT_OPTIMIZER = 'pngnq -s 4 %(path)s'
  CAIROTEXT_OPTIMIZED_PATH = '%(directory)s/%(name)s-nq8.png'

With these settings, Cairotext would optimize each generated file
using the pngnq_ optimizer.  The color palette of the image would be
reduced to four colors.  On one site, this method reduced average
image sizes to 26% of original while still resulting in acceptable
quality.

.. _pngnq: http://pngnq.sourceforge.net/


Related apps and blog posts
===========================

Cairotext is originally based on a blog post titled `django and cairo:
rendering pretty titles`_ by Andrew Godwin.  Experience from using and
modifying `django-rendertext`_ (by olau at iola in Denmark, based on
derelm's snippet) and `sorl-thumbnail`_ was also taken advantage of.
Apologies to the django-rendertext team for stealing bits from their
readme file.

.. _django and cairo\: rendering pretty titles: http://www.aeracode.org/2007/12/15/django-and-cairo-rendering-pretty-titles/
.. _django-rendertext: http://code.google.com/p/django-rendertext/
.. _sorl-thumbnail: http://code.google.com/p/sorl-thumbnail/

Other implementations of similar ideas:

* `improved text image view`_ by Jacob Kaplan-Moss
* `simple text image view`_ by derelm, based on work by Andrew Gwozdziewycz and Jacob Kaplan-Moss (above)
* `django-image-replacement`_ by Ludwig Pettersson

.. _improved text image view: http://jacobian.org/writing/improved-text-image-view/
.. _simple text image view:  http://www.djangosnippets.org/snippets/117/
.. _django-image-replacement: http://code.google.com/p/django-image-replacement
