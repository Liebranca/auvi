from bpy.types import Scene;
import importlib;

def lytdummy():
    pass;

def reg(n):

    if not hasattr(Scene, "lymport"):
        from .importer import register as reg_lymport;
        reg_lymport();

    try:
        module=importlib.import_module('.'+n, 'lytools');
        return module.register, module.unregister;

    except:
        return lytdummy, lytdummy;