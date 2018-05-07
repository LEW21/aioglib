from .aio import call


class AsyncFunction:
	def __init__(self, start, finish):
		self.start = start
		self.finish = finish

	def __call__(self, *args):
		return call(self.start, self.finish, *args)


def make_callback(func):
	if func is None:
		return None

	return partial(get_event_loop().call_soon_threadsafe, func)


def AioProperty(cls):
	def aio(self):
		try:
			return self._aio
		except AttributeError:
			self._aio = cls(self)
			return self._aio
	return property(aio)
