import hashlib
import bokeh.util.compiler
import os.path
import hashlib
import json

model_cache_path = os.path.expanduser("~/.bokeh-garden/model-cache")
if not os.path.exists(model_cache_path):
    os.makedirs(model_cache_path)

def model_cache(model, implementation):
    code_hash = hashlib.sha1(implementation.code.encode("utf-8")).hexdigest()
    model_id = ("%s.%s" % (model.module, model.name)).replace("/", ".")

    cached_model = None
    model_path = os.path.join(model_cache_path, "%s.json" % (model_id,))
    if os.path.exists(model_path):
        with open(model_path, "r") as f:
            cached_model = json.load(f)
    if cached_model is not None and cached_model["code_hash"] != code_hash:
        cached_model = None

    if not cached_model:
        compiled = bokeh.util.compiler.nodejs_compile(implementation.code, lang=implementation.lang, file=implementation.file)
        cached_model = {
            "code_hash": code_hash,
            "compiled": dict(compiled)
        }
        with open(model_path, "w") as f:
            json.dump(cached_model, f)

    cached_model["compiled"] = bokeh.util.compiler.AttrDict(cached_model["compiled"])
    return cached_model["compiled"]

bokeh.util.compiler.set_cache_hook(model_cache)
