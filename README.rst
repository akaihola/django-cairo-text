===================
 django-cairo-text
===================

This is a re-usable Django app for using custom fonts on a web page
for headings, navigation and the like.  It uses the Cairo graphics
library to create images dynamically out of text snippets and caches
them.  Currently output in the PNG format is possible since that's all
Cairo supports.


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
  <img src="{{img.url}}" alt="{{myvar}}"
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

The template tag returns an image information dictionary like this::

  img == {'url': '/media/cairotext_cache/41f97f2c80e9c581c9fa85ca4efda8d9.png',
          'width': 120,
          'height': 61}

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