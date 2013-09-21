import os
import glob

# Figure out the names of each module available for import.
__modules__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]
__supermodules__ = [ os.path.split(os.path.split(f)[0])[1] for f in glob.glob(os.path.dirname(__file__)+"/*/__init__.py")] 
__all__ =  __modules__ + __supermodules__