import bokeh.model
import bokeh.core.properties
import bokeh.util.callback_manager


class Collection(bokeh.model.Model):
	objects = bokeh.core.properties.Dict(bokeh.core.properties.String,
										 bokeh.core.properties.Instance(bokeh.model.Model))

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self._triggered_attrs = set()

	def trigger(self, attr, old, new, hint=None, setter=None):
		# In Bokeh 3.x, trigger() requires the property to exist as a descriptor
		# and accepts hint and setter parameters
		if attr not in self._triggered_attrs:
			cls = type(self)
			if not hasattr(cls, attr):
				# Create a property descriptor at the class level
				prop = bokeh.core.properties.Any(default=None)
				from bokeh.core.property.descriptors import PropertyDescriptor
				descriptor = PropertyDescriptor(attr, prop)
				setattr(cls, attr, descriptor)
			self._triggered_attrs.add(attr)

		# Now call the parent trigger method with all parameters
		super().trigger(attr, old, new, hint=hint, setter=setter)

	def on_change(self, attr, *callbacks):
		# Ensure property exists before setting up callbacks
		cls = type(self)
		if not hasattr(cls, attr):
			prop = bokeh.core.properties.Any(default=None)
			from bokeh.core.property.descriptors import PropertyDescriptor
			descriptor = PropertyDescriptor(attr, prop)
			setattr(cls, attr, descriptor)
		bokeh.util.callback_manager.PropertyCallbackManager.on_change(self, attr, *callbacks)

	def __setattr__(self, name, value):
		if name.startswith("_"):
			bokeh.model.Model.__setattr__(self, name, value)
		else:
			old = self.objects.get(name, None)
			self.objects[name] = value
			self.trigger(name, old, value)

	def __getattribute__(self, name):
		# First check if it's a private attribute or a known class attribute
		if name.startswith("_") or name in ("objects", "trigger", "on_change"):
			return super(Collection, self).__getattribute__(name)

		# Try to get from objects dict if it exists there
		try:
			objects = super(Collection, self).__getattribute__("objects")
			if name in objects:
				return objects[name]
		except (AttributeError, KeyError):
			pass

		# Otherwise use standard attribute access
		return super(Collection, self).__getattribute__(name)

	def __getattr__(self, name):
		# This is called only when __getattribute__ raises AttributeError
		# Should not normally be reached due to __getattribute__ implementation above
		if name.startswith("_"):
			return super(Collection, self).__getattribute__(name)
		return super(Collection, self).__getattribute__("objects")[name]
