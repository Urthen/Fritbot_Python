import lya

class Config(object):
	def __init__(self):
		self._cfg = None
		self.recent_files = None

	def __getattr__(self, attr):
		if attr in self.__dict__:
			return self.__dict__[attr]
		else:
			return self._cfg[attr]

	def loadConfig(self, files = None):
		# Load most recently loaded files if none were specified. Used to re-load configuration if neccesary.
		if files is None:
			if self.recent_files is not None:
				files = self.recent_files
			else:
				return #files not specified and no recent files, no-op - but this should never happen in practice
		self.recent_files = files

		self._cfg = lya.AttrDict.from_yaml('default.yaml')
		for path in files: self._cfg.update_yaml(path)

cfg = Config()
