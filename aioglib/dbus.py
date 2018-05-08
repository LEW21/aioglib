from ._py37.dataclasses import dataclass
from gi.repository import GLib, Gio

from ._core import AioProperty, Runner, Watcher


BusType = Gio.BusType
MAXINT = GLib.MAXINT
Variant = GLib.Variant
VariantType = GLib.VariantType


@dataclass
class BusNameAppearedCallback:
	name: str
	name_owner: str


@dataclass
class BusNameVanishedCallback:
	name: str


@dataclass
class DBusInterfaceMethodCall:
	sender: str
	object_path: str
	interface_name: str
	method_name: str
	parameters: Variant
	invocation: Gio.DBusMethodInvocation


@dataclass
class DBusSignalCallback:
	sender_name: str
	object_path: str
	interface_name: str
	signal_name: str
	parameters: Variant


# Nothing for g_bus_(un)own_name, because g_bus_unown_name works synchroneously.
# It's simply broken.


def bus_watch_name_on_connection(con, name, flags):
	watch = Watcher(Gio.bus_watch_name_on_connection, Gio.bus_unwatch_name)
	return watch(con.pygi, name, flags, BusNameAppearedCallback, BusNameVanishedCallback)


class DBusConnection:
	"""
	We're automatically thread-safe, because:

	As an exception to the usual GLib rule that a particular object must not be used by two threads at the same time, GDBusConnection's methods may be called from any thread. This is so that g_bus_get() and g_bus_get_sync() can safely return the same GDBusConnection when called from any thread.
	"""
	def __init__(self, pygi):
		self.pygi = pygi

	def call(self, bus_name, object_path, interface_name, method_name, parameters, reply_type, flags, timeout_msec):
		call = Runner(self.pygi.call, self.pygi.call_finish)
		return call(bus_name, object_path, interface_name, method_name, parameters, reply_type, flags, timeout_msec)

	def signal_subscribe(self, sender, interface_name, member, object_path, arg0, flags):
		watch = Watcher(self.pygi.signal_subscribe, self.pygi.signal_unsubscribe)
		return watch(sender, interface_name, member, object_path, arg0, flags, DBusSignalCallback)

	def register_object(self, object_path, interface_info):
		"""
		get_property_closure and set_property_closure are not used, as they can't properly support greenlets.

		Gio docs: "Since 2.38, if you want to handle getting/setting D-Bus properties asynchronously, give NULL as your get_property() or set_property() function. The D-Bus call will be directed to your method_call function, with the provided interface_name set to "org.freedesktop.DBus.Properties"."
		"""
		watch = Watcher(self.pygi.register_object, self.pygi.unregister_object)
		return watch(object_path, interface_info, DBusInterfaceMethodCall, None, None)

	def emit_signal(self, destination_bus_name, object_path, interface_name, signal_name, parameters):
		return self.pygi.emit_signal(destination_bus_name, object_path, interface_name, signal_name, parameters)

	watch_name = bus_watch_name_on_connection

	@staticmethod
	async def new(stream, guid, flags=0, observer=None):
		f = Runner(Gio.DBusConnection.new, Gio.DBusConnection.new_finish)
		return (await f(stream, guid, flags, observer)).aio

	@staticmethod
	async def new_for_address(address, flags=0, observer=None):
		f = Runner(Gio.DBusConnection.new_for_address, Gio.DBusConnection.new_for_address_finish)
		return (await f(address, flags, observer)).aio

	def start_message_processing(self):
		self.pygi.start_message_processing()

	def close(self):
		return Runner(self.pygi.close, self.pygi.close_finish)()

Gio.DBusConnection.aio = AioProperty(DBusConnection)


async def bus_get(bus_type):
	bus = await Runner(Gio.bus_get, Gio.bus_get_finish)(bus_type)
	return bus.aio
