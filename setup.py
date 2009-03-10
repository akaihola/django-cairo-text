from distutils.core import setup
import glob

setup(
    name='django-cairo-text',
    version=__import__('cairotext').__version__,
    description='Re-usable Django app for rendering custom fonts as images',
    author='Antti Kaihola',
    author_email='akaihol+cairotext@ambitone.com',
    url='http://github.com/akaihola/django-cairo-text/',
    requires=('pycairo (>=1.8.2)',),
    packages=['cairotext', 'cairotext.templatetags'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.3',
        'Topic :: Text Processing :: Fonts',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
    ]
)
