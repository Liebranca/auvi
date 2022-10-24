import bpy, os, importlib;

import io
from contextlib import redirect_stdout

def SHUT_OPS(call, args=[], kwargs={}):

    stdout = io.StringIO()
    with redirect_stdout(stdout):
        call(*args, **kwargs);

def RELPATH(to):
    path=bpy.context.blend_data.filepath;
    return os.path.relpath(to, path);

def lytdummy():
    pass;

def reg(n):

    if not hasattr(bpy.types.Scene, "lymport"):
        from .importer import register as reg_lymport;
        from .packaging import register as reg_packaging;
        reg_lymport(); reg_packaging();

    if n in ["matlib", "matmk", "matmix", "mapping", "packaging"]:
        module=importlib.import_module('.'+n, 'lytools');
        return module.register, module.unregister;

    else:
        from .matlib import register, unregister
        from .importer import PERMABLOCKS; PERMABLOCKS();
        return register, unregister;