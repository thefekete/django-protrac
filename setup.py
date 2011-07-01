"""
Heavily inspired by the django-basic-apps setup.py by nathanborror.

http://github.com/nathanborror/django-basic-apps
"""
import os
from distutils.core import setup


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == "":
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


package_dir = "protrac"


packages = []
for dirpath, dirnames, filenames in os.walk(package_dir):
    # ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if "__init__.py" in filenames:
        packages.append(".".join(fullsplit(dirpath)))


# need to go 4 deep for admin templates, plus one for good measure
template_patterns = [
        'templates/*.html',
        'templates/*/*.html',
        'templates/*/*/*.html',
        'templates/*/*/*/*.html',
        'templates/*/*/*/*/*.html',]

package_data = dict(
        (package_name, template_patterns) for package_name in packages)


setup(name='django-protrac',
    version='0.1',
    description='Production Tracking App for Django',
    author='Dan Fekete',
    packages=packages,
    package_data=package_data)
