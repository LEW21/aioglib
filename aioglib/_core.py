from .aio import run, watch


class Runner:
	def __init__(self, start, finish):
		self.start = start
		self.finish = finish

	def __call__(self, *args):
		return run(self.start, self.finish, *args)


class Watcher:
	def __init__(self, install, uninstall):
		self.install = install
		self.uninstall = uninstall

	def __call__(self, *args):
		return watch(self.install, self.uninstall, *args)


def AioProperty(cls):
	def aio(self):
		try:
			return self._aio
		except AttributeError:
			self._aio = cls(self)
			return self._aio
	return property(aio)
