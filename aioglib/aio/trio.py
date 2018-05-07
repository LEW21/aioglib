from gi.repository import GLib, Gio
from outcome import capture

try:
	import trio.hazmat
except NotImplementedError as e:
	raise ImportError('Cannot import trio', e)

from ..util import get_main_context


def is_active():
	try:
		trio.hazmat.current_trio_token()
		return True
	except RuntimeError as e:
		print(e)
		return False


async def call(start, finish, *args):
	trio_token = trio.hazmat.current_trio_token()
	trio_task = trio.hazmat.current_task()

	trio_cancel_raiser = None
	cancellable = Gio.Cancellable.new()
	def abort(raiser):
		nonlocal trio_cancel_raiser
		trio_cancel_raiser = raiser
		cancellable.cancel()
		return trio.hazmat.Abort.FAILED

	def wake_up(outcome):
		trio_token.run_sync_soon(trio.hazmat.reschedule, trio_task, outcome)

	def start_fn():
		start(*([arg for arg in args] + [cancellable, (lambda _, cbres: wake_up(capture(finish, cbres)))]))
	get_main_context().invoke_full(0, start_fn)

	try:
		return await trio.hazmat.wait_task_rescheduled(abort)
	except GLib.Error as e:
		if e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
			trio_cancel_raiser()
		else:
			raise
