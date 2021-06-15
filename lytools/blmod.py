import importlib;

def lytdummy():
    pass;

def reg(n):

    try:
        module=importlib.import_module('.'+n, 'lytools');
        return module.register, module.unregister;

    except:
        return lytdummy, lytdummy;