import bokeh.themes
import importlib
from . import collection


def load_cls(name):
	modname, clsname = name.rsplit(".", 1)
	return getattr(importlib.import_module(modname), clsname)


class PlotCollection(collection.Collection):
	def __init__(self, doc, layout=None, overlays=None, widgets=None, **kwargs):
		self._doc = doc
		self._layout_template = layout if layout is not None else {}
		self._overlays_template = overlays if overlays is not None else []
		self._widgets_template = widgets if widgets is not None else {}
		self._layout = None
		self._overlays = []
		collection.Collection.__init__(self, **kwargs)
		self.generate_plots()

	@property
	def doc(self):
		return self._doc

	def instantiate(self, template, overlays=False):
		if isinstance(template, (list, tuple)):
			return [self.instantiate(item, overlays=overlays) for item in template]
		elif isinstance(template, dict):
			# CRITICAL: Make a DEEP copy to avoid modifying shared templates
			import copy
			t = copy.deepcopy(template)

			if "widget" in t:
				if "base" in t:
					t["override"], t["widget"] = t.pop("widget"), t.pop("base")
				w = t.pop("widget")

				# Resolve widget templates
				while w in self._widgets_template:
					t_w = copy.deepcopy(self._widgets_template[w])
					if "base" in t_w:
						t_w["override"], t_w["widget"] = t_w.pop("widget"), t_w.pop("base")
					w = t_w.pop("widget", None)
					t_w.update(t)
					t = t_w

				if "override" in t:
					w = t.pop("override")
				elif w is None:
					raise Exception("No override and no widget", t.keys())

				if isinstance(w, str):
					w = load_cls(w)

				args = []
				if hasattr(w, "appwidget") or overlays:
					args = [self]
				elif hasattr(w, '__name__') and 'Upload' in w.__name__:
					# Special case: Upload widgets need document/PlotCollection
					args = [self]

				kwargs = self.instantiate(t, overlays=overlays)

				try:
					return w(*args, **kwargs)
				except Exception as e:
					raise Exception("%s.%s(*%s, **%s): %s" % (
						w.__module__, w.__name__,
						args,
						kwargs,
						e
					))
			else:
				return {name: self.instantiate(value, overlays=overlays) for name, value in t.items()}
		else:
			return template

	def generate_plots(self):
		self._layout = self.instantiate(self._layout_template)
		self._doc.add_root(self._layout)
		self._overlays = self.instantiate(self._overlays_template, overlays=True)
