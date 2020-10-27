from setuptools import setup, find_packages
from workflow import __version__

setup(name="django-workflow",
      version=__version__,
      description="Workflow editor for Django",
      long_description="Edit and Manage workflows to associate to your Django objects",
      author="SimplyOpen",
      author_email="info@simplyopen.org",
      url="https://github.com/simplyopen-it/django-workflow",
      packages=find_packages(),
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
