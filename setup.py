from setuptools import setup, find_packages
from setuptools import distutils
import os

rootpath = os.path.dirname(__file__)
if rootpath != '':
    os.chadir(rootpath)
app_path = os.path.join(rootpath, 'immigrationcenter')

# def find_data(rootpath, exclude=None):
#     if exclude is None:
#         exclude = []
#     data_files = []
#     for dirpath, dirnames, filenames in os.walk(rootpath):
#         for i, dirname in enumerate(dirnames):
#             if dirname.startswith('.'):
#                 del dirnames[i]
#         if '__init__.py' in filenames:
#             pass
#         elif filenames:
#             data_files.append(
#                 [os.path.join(distutils.sysconfig.get_python_lib(), dirpath),
#                  [os.path.join(dirpath, f) for f in filenames]])
#         if dirnames:
#             [dirnames.remove(name) for name in exclude if name in dirnames]
#     return data_files

setup(name = "django-ordermanagement",
      version = "0.1",
      description = "Workflow editor for Django",
      long_description="Edit and Manage workflows to associate to your Django objects",
      author = "SimplyOpen",
      author_email = "info@simplyopen.org",
      packages = find_packages(),
#      package_data={'order_management': ['templates/order_management/*']},
      package_dir={'workflow': 'workflow'},
#      data_files = find_data(app_path, exclude=['media', 'hidden']),
      install_requires=['Django>=1.4'],
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
