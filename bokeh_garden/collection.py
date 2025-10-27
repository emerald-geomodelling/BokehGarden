import bokeh.model
import bokeh.core.properties
import bokeh.util.callback_manager


class Collection(bokeh.model.Model):
	objects = bokeh.core.properties.Dict(
		bokeh.core.properties.String,
		bokeh.core.properties.Instance(bokeh.model.Model)
	)

	def __init__(self, **kwargs):
		# FIX: Initialize _triggered_attrs BEFORE calling super().__init__()
		# This prevents AttributeError during Bokeh 3.x property descriptor initialization
		object.__setattr__(self, '_triggered_attrs', set())
		super().__init__(**kwargs)

	def trigger(self, attr, old, new, hint=None, setter=None):
		"""
		Trigger a change event for an attribute.
		Thread safety is handled by IOLoop.add_callback in background_task.py
		"""
		if attr not in self._triggered_attrs:
			cls = type(self)
			if not hasattr(cls, attr):
				# Create a property descriptor at the class level
				prop = bokeh.core.properties.Any(default=None)
				from bokeh.core.property.descriptors import PropertyDescriptor
				descriptor = PropertyDescriptor(attr, prop)
				setattr(cls, attr, descriptor)
			self._triggered_attrs.add(attr)

		# Use standard Bokeh trigger - threading handled elsewhere
		super(Collection, self).trigger(attr, old, new, hint=hint, setter=setter)

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
		# Private attributes (starting with _) always go through normal Bokeh handling
		if name.startswith("_"):
			bokeh.model.Model.__setattr__(self, name, value)
			return

		# Check if this is a declared Bokeh property on the class
		cls = type(self)
		if hasattr(cls, name) and isinstance(getattr(cls, name), bokeh.core.property.descriptors.PropertyDescriptor):
			# This is a declared Bokeh property, use standard Bokeh handling
			bokeh.model.Model.__setattr__(self, name, value)
			return

		# For all other attributes (like 'data'), store in the objects dict
		try:
			objects = object.__getattribute__(self, '__dict__').get('objects', None)
			if objects is None:
				# objects dict not yet initialized
				object.__getattribute__(self, '__dict__')[name] = value
				return

			# Store in objects dict and trigger change event
			old = objects.get(name, None)
			objects[name] = value
			self.trigger(name, old, value)
		except (AttributeError, KeyError):
			# Fallback: store directly in __dict__
			object.__getattribute__(self, '__dict__')[name] = value

	def __getattribute__(self, name):
		#FIX for Bokeh 3.x: ALL internal Bokeh attributes must bypass custom logic
		# This includes _temp_document which is accessed during initialization
		if name.startswith("_") or name in (
				"objects", "trigger", "on_change", "document",
				"themed_values", "_property_values", "_unstable_default_values",
				"_document", "_temp_document",  # _temp_document MUST be here for Bokeh 3.x
				"properties", "properties_with_refs",
				"properties_with_values", "query_properties_with_values", "dataspecs",
				"lookup", "apply_theme", "unapply_theme", "select", "select_one",
				"set_select", "references", "to_serializable",
				"__class__", "__dict__", "__setattr__", "__getattribute__"
		):
			return super(Collection, self).__getattribute__(name)

		# Try to get from objects dict if it exists there
		try:
			objects = super(Collection, self).__getattribute__("objects")
			if objects is not None and name in objects:
				return objects[name]
		except (AttributeError, KeyError):
			pass

		# Otherwise use standard attribute access
		return super(Collection, self).__getattribute__(name)

	def __getattr__(self, name):
		# This is called only when __getattribute__ raises AttributeError
		if name.startswith("_"):
			return super(Collection, self).__getattribute__(name)

		try:
			return super(Collection, self).__getattribute__("objects")[name]
		except (AttributeError, KeyError):
			raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
