from setuptools import setup, find_packages
from workflow import __version__

setup(name = "django-workflow",
      version = __version__,
      description = "Workflow editor for Django",
      long_description="Edit and Manage workflows to associate to your Django objects",
      author = "SimplyOpen",
      author_email = "info@simplyopen.org",
      packages = find_packages(),
      package_dir={'workflow': 'workflow'},
      install_requires=['Django>=1.7'],
      include_package_data = True,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: Log Analysis',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Security',
          'Topic :: System :: Logging',
      ],
      zip_safe=False,
)
