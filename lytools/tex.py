import bpy; C=bpy.context; D=bpy.data;

bake_slot=None; textypes=["albedo", "orm", "normal"];

def MKIMG(name, path):

    new_img=D.images.new(name, width=64, height=64);

    new_img.source='FILE';
    new_img.filepath=path;

    return new_img;

def MKMAT(name, path):

    path=path+'\\'+name;

    if name not in D.materials:
        mat=D.materials["Template"].copy();
        mat.name=name;

    else:
        mat=D.materials[name];

    for texmap in textypes:

        n=name+'_'+texmap;

        if n not in D.images:
            im=MKIMG(n, path+'\\'+n+'.png');

        else:
            im=D.images[n];

        mat.node_tree.nodes[texmap].image=im;

    C.scene.update();

def DLMAT(name):
    mat=D.materials[name];
    images=[im for im in D.images if im.name.startswith(name+'_')];

    for im in images:
        D.images.remove(im);

    mat.use_fake_user=0;
    if mat.users: mat.user_clear();

    D.materials.remove(D.materials[name]);

def GTBAKESLOT():

    global bake_slot;

    for screen in D.screens:
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                bake_slot=area.spaces.active;

def PAINT():

    if not bake_slot: GTBAKESLOT();

    me=C.object.data;
    me.uv_textures[1].active=1;
    me.uv_textures[0].active=0;

    mat=me.materials[0];
    imnodes=mat.node_tree.nodes;
    imnodes=[node for node in imnodes if hasattr(node, "texture")];
    texfams=[node.image.name.split("_")[0] for node in imnodes];

    matname=mat.name.replace("_paint", "");

    for texmap in textypes:

        for tex, node in zip(texfams, imnodes):
            node.image=D.images[tex+'_'+texmap];

        imname=matname+'_'+texmap;
        if imname not in D.images:
            new_img=D.images.new(imname, width=256, height=256);
            new_img.source='GENERATED';

        im=D.images[imname];

        im.use_alpha=1;
        im.alpha_mode='STRAIGHT';
        im.file_format='PNG';
        im.filepath_raw='//'+imname+'.png';

        bpy.ops.object.mode_set(mode='EDIT');
        bpy.ops.mesh.select_mode(type='VERT');
        bpy.ops.mesh.select_all(action='SELECT');

        bake_slot.image=im;
        bpy.ops.object.mode_set(mode='OBJECT');

        C.scene.render.bake_type='FULL';
        bpy.ops.object.bake_image();

        im.save();

    me.uv_textures[0].active=1;
    me.uv_textures[1].active=0;

    MKMAT(matname, ('\\'.join(im.filepath_raw.split('\\')[:-1]))+'\\');

    for tex, node in zip(texfams, imnodes):
        node.image=D.images[tex+'_albedo'];


