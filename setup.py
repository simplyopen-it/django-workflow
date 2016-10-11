import os
import re
import codecs
from setuptools import setup, find_packages
from workflow import __version__

def find_version(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    with codecs.open(filename, encoding='utf-8') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name="django-workflow",
      version=find_version('workflow', '__init__.py'),
      description="Workflow editor for Django",
      long_description="Edit and Manage workflows to associate to your Django objects",
      author="SimplyOpen",
      author_email="info@simplyopen.org",
      packages=find_packages(),
      package_dir={'workflow': 'workflow'},
      install_requires=[
          'Django>=1.7',
          'django-extensions>=1.3.10',
      ],
      include_package_data = True,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
      ],
)
