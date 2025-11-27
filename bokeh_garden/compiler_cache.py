# compiler_cache.py
import hashlib
import bokeh.util.compiler
import os.path
import json

model_cache_path = os.path.expanduser("~/.bokeh-garden/model-cache")

if not os.path.exists(model_cache_path):
	os.makedirs(model_cache_path)


def model_cache(model, implementation):
	code_hash = hashlib.sha1(implementation.code.encode("utf-8")).hexdigest()

	# Fix: Use model.path instead of model.__module__/__name__
	model_id = model.path.replace("/", ".")

	model_path = os.path.join(model_cache_path, "%s.json" % (model_id,))
	cached_model = None

	if os.path.exists(model_path):
		try:
			with open(model_path, "r") as f:
				cached_model = json.load(f)
		except (json.JSONDecodeError, KeyError):
			cached_model = None

	if cached_model is not None and cached_model.get("code_hash") != code_hash:
		cached_model = None

	if not cached_model:
		# Compile using nodejs
		compiled = bokeh.util.compiler.nodejs_compile(
			implementation.code,
			lang=implementation.lang,
			file=implementation.file
		)

		# Store all fields including deps
		cached_model = {
			"code_hash": code_hash,
			"compiled": {
				"code": compiled.get("code", ""),
				"deps": compiled.get("deps", {}),
				"error": compiled.get("error", None),
			}
		}

		with open(model_path, "w") as f:
			json.dump(cached_model, f, indent=2)

	# Return as AttrDict so .deps works
	return bokeh.util.compiler.AttrDict(cached_model["compiled"])


bokeh.util.compiler.set_cache_hook(model_cache)
