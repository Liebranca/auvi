import bpy, os, importlib;

def RELPATH(to):
    path=bpy.context.blend_data.filepath;
    return os.path.relpath(to, path);

def lytdummy():
    pass;

def reg(n):

    if not hasattr(bpy.types.Scene, "lymport"):
        from .importer import register as reg_lymport;
        reg_lymport();

    try:
        module=importlib.import_module('.'+n, 'lytools');
        return module.register, module.unregister;

    except:
        return lytdummy, lytdummy;