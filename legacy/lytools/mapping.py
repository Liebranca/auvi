import bpy;
from mathutils.bvhtree import BVHTree
from mathutils import Vector;
from math import sqrt;

from bpy.types import Panel, Operator, PropertyGroup, Object, Material, Scene;
from bpy.utils import register_class, unregister_class;

#   ---     ---     ---     ---     ---

class MAPPING_TILE:

    def __init__(self, ob, x, y):
        self.ob=ob; self.bvh=BVHTree.FromObject(ob, bpy.context.scene);

        ob.data.use_auto_smooth=0;
        self.normals=[v.normal for v in ob.data.vertices];
        ob.data.use_auto_smooth=1; ob.data.calc_normals();

        self.co=(x, y);

class MAPPING_GRID:

    def __init__(self, size, subdivs):
        self.size=size; self.subdivs=subdivs; self.hsize=int(self.size/2);
        self.cont=[[None for x in range(size)] for y in range(size)];
        self.edge_verts_count=((subdivs*4)+4);

    def insert(self, ob):
        x,y=(ob.location/2)[0:2];
        x=int(x+self.hsize); x=x if x>=0 else 0; x=x if x<self.size else self.size-1;
        y=int(y+self.hsize); y=y if y>=0 else 0; y=y if y<self.size else self.size-1;

        self.cont[x][y]=MAPPING_TILE(ob, x, y);

    def at(self, x, y):
        x=int(x+self.hsize);
        y=int(y+self.hsize);

        if not ((0 <= x < self.size) and (0 <= y < self.size)):
            return None;

        return self.cont[x][y];

    def calcEdges(self):

        edges={};

        for y in range(0, self.size):
            for x in range(0, self.size):
                t=self.cont[x][y];

                for vert in t.ob.data.vertices:

                    mark=0;
                    co_idex=(
                        round(vert.co.x+t.ob.location.x, 4),
                        round(vert.co.y+t.ob.location.y, 4)
                    );

                    if x and vert.co.x==-1:
                        try: edges[co_idex].append([x,y,vert.index]);
                        except: edges[co_idex]=[[x,y,vert.index]];

                        mark=1;

                    elif x!=(self.size-1) and vert.co.x==1:
                        try: edges[co_idex].append([x,y,vert.index]);
                        except: edges[co_idex]=[[x,y,vert.index]];

                        mark=1;

                    if not mark:
                        if y and vert.co.y==-1:
                            try: edges[co_idex].append([x,y,vert.index]);
                            except: edges[co_idex]=[[x,y,vert.index]];

                        elif y!=(self.size-1) and vert.co.y==1:
                            try: edges[co_idex].append([x,y,vert.index]);
                            except: edges[co_idex]=[[x,y,vert.index]];

        self.edges=edges;

    def getFocus(self, target):
        x,y=target[0:2];
        x=int(x+self.hsize); x=x if x>=0 else 0; x=x if x<self.size else self.size-1;
        y=int(y+self.hsize); y=y if y>=0 else 0; y=y if y<self.size else self.size-1;

        near=self.cont[x][y]; surr=[];
        for x in range(self.size):
            for y in range(self.size):
                t=self.cont[x][y];
                if t != near: surr.append(t);

        return near, surr;

#   ---     ---     ---     ---     ---

mgrid=None;

def MKGRID():
    global mgrid; mgrid=MAPPING_GRID(2, 8);
    for ob in bpy.context.scene.objects:
        mgrid.insert(ob);

    mgrid.calcEdges();

def SCULPT():

    target=bpy.context.scene.cursor_location;
    radius=1; strength=0.25;

    center, surr=mgrid.getFocus(target);
    tiles=surr+[center]; edges_to_avg={};

    for tile in tiles:
        point=target-tile.ob.location; point.z=0;
        near_points=tile.bvh.find_nearest_range(point, radius);

        for near in near_points:
            idx=near[2]; poly=tile.ob.data.polygons[idx];

            for vi in poly.vertices:
                vert=tile.ob.data.vertices[vi]; dist=abs((vert.co-point).length);
                mod=max(0, strength-(3*(dist**2) - 2*(dist**3))); vert.co.z+=mod;

                co_idex=(
                    round(vert.co[0]+tile.ob.location.x, 4),
                    round(vert.co[1]+tile.ob.location.y, 4)
                );

                try:
                    f=mgrid.edges[co_idex];

                    if (abs(vert.co.x)==1) or (abs(vert.co.y)==1):
                        edges_to_avg[co_idex]=vert.co;

                except: None;

        tile.ob.data.calc_normals();

    to_update={};
    for co_idex in edges_to_avg:
        edgedata=mgrid.edges[co_idex]; indices={};
        neighbors=len(edgedata); normal=Vector([0,0,0]);
        for d in edgedata:
            x,y,vi=d; t=mgrid.cont[x][y]; vert=t.ob.data.vertices[vi];
            normal+=vert.normal; indices[(x,y,vi)]=0; to_update[(x,y)]=t;
            tp_co=edges_to_avg[co_idex];
            if vert.co.z != tp_co.z: vert.co.z=tp_co.z;

        normal=(normal/neighbors).normalized();
        for d in indices:
            x,y,vi=d; mgrid.cont[x][y].normals[vi]=normal;

    for t in list(to_update.values()):
        t.ob.data.use_auto_smooth=1;
        t.ob.data.normals_split_custom_set_from_vertices(t.normals);

MKGRID();

#   ---     ---     ---     ---     ---

class LYT_MPSCULPT(Operator):

    bl_idname      = "lytmap.sculpt";
    bl_label       = "";

    bl_description = "";

#   ---     ---     ---     ---     ---

    def execute(self, context):
        SCULPT(); return {'FINISHED'};

class LYT_mappingPanel(Panel):

    bl_label       = 'LYT MAPPER';
    bl_idname      = 'LYT_mappingPanel';
    bl_space_type  = 'PROPERTIES';
    bl_region_type = 'WINDOW';
    bl_context     = 'world';
    bl_category    = 'LYT';

#   ---     ---     ---     ---     ---
    
    @classmethod
    def poll(cls, context):
        return context.scene != None;

    def draw(self, context):
        layout=self.layout; row=layout.row();
        row.operator("lytmap.sculpt", text="TEST", icon="RNDCURVE");

#   ---     ---     ---     ---     ---

def register():
    register_class(LYT_MPSCULPT);
    register_class(LYT_mappingPanel);

def unregister():
    register_class(LYT_mappingPanel);
    register_class(LYT_MPSCULPT);

#   ---     ---     ---     ---     ---