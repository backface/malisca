# $Id: setup.py 6846 2009-12-17 02:19:16Z esr $
# Creates build/lib.linux-${arch}-${pyvers}/gpspacket.so,
# where ${arch} is an architecture and ${pyvers} is a Python version.

from distutils.core import setup

setup(	name="camera",
		version="0.01",
		author="Michael Aschauer",
		packages = ['camera'],
		data_files=[	('bin', ['camcontrol333.py','camcontrol353.py']),
					('share/camcontrol/',['camcontrol333.xml','camcontrol353.xml'])]
     )
