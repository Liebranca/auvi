import bpy;
from arcana.Bytes import CRK;

verts=[];
faces=[];

uvs=[];

crk=CRK.read(
  "/home/lyeb/Desktop/spritebake/sheet.crk"
    
);

idex=2;

beg=crk[idex]['face'][0][0];

verts.extend(crk[idex]['co']);
faces.extend(crk[idex]['face']);

i=0;
for tup in faces:
  faces[i]=[j-beg for j in tup];
  i+=1;

uvs.extend(crk[idex]['uv']);

if "FROM_PY" in bpy.data.meshes:
  bpy.data.meshes.remove(bpy.data.meshes["FROM_PY"]);
    
me=bpy.data.meshes.new("FROM_PY");
me.from_pydata(verts,[],faces);

ob=bpy.data.objects.new("FROM_PY",me);
bpy.context.collection.objects.link(ob);

me.uv_layers.new();

for face in me.polygons:
  for vi,loop in zip(face.vertices,face.loop_indices):
    loop=me.uv_layers.active.data[loop];    
    loop.uv[:]=uvs[vi][:];
    
me.materials.append(bpy.data.materials['sheet']);