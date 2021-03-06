import bpy
import mathutils
from Block import Block

class Transparent(Block):
    """A block with a texture that contains transparent or translucent pixels"""
    
    def makeObject(self, x, y, z, metadata):
        mesh = bpy.data.meshes.new(name="Block")
        mesh.from_pydata([[-0.5,-0.5,-0.5],[0.5,-0.5,-0.5],[-0.5,0.5,-0.5],[0.5,0.5,-0.5],[-0.5,-0.5,0.5],[0.5,-0.5,0.5],[-0.5,0.5,0.5],[0.5,0.5,0.5]],[],[[0,1,3,2],[4,5,7,6],[0,1,5,4],[0,2,6,4],[2,3,7,6],[1,3,7,5]])
        mesh.update()

        obj = bpy.data.objects.new("Block", mesh)
        obj.location.x = x + 0.5
        obj.location.y = y + 0.5
        obj.location.z = z + 0.5
        obj.scale = (0.9998999834060669, 0.9998999834060669, 0.9998999834060669) # workaround for overlapping object shading issue
        obj.blockId = self._id
        obj.blockMetadata = metadata
        bpy.context.scene.objects.link(obj)

        activeObject = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.objects.active = activeObject
        
        return obj
    
    def applyMaterial(self, obj, metadata):
        try:
            mat = bpy.data.materials[self._unlocalizedName]
        except KeyError:
            mat = bpy.data.materials.new(self._unlocalizedName)
            mat.preview_render_type = "CUBE"
            mat.use_nodes = True
            mat.node_tree.nodes["Material Output"].location = [400, 0]
            mat.node_tree.nodes["Diffuse BSDF"].location = [0, -75]
            mat.node_tree.links.remove(mat.node_tree.links[0])
            
            #Mix Shader
            mat.node_tree.nodes.new(type="ShaderNodeMixShader")
            mat.node_tree.nodes["Mix Shader"].location = [200, 0]
            mat.node_tree.links.new(mat.node_tree.nodes["Diffuse BSDF"].outputs[0], mat.node_tree.nodes["Mix Shader"].inputs[2])
            mat.node_tree.links.new(mat.node_tree.nodes["Mix Shader"].outputs[0], mat.node_tree.nodes["Material Output"].inputs[0])
            
            #Transparent Shader
            mat.node_tree.nodes.new(type="ShaderNodeBsdfTransparent")
            mat.node_tree.nodes["Transparent BSDF"].location = [0, 100]
            mat.node_tree.links.new(mat.node_tree.nodes["Transparent BSDF"].outputs[0], mat.node_tree.nodes["Mix Shader"].inputs[1])
            
            #Initialize Texture
            try:
                tex = bpy.data.images[self._unlocalizedName]
            except KeyError:
                tex = bpy.data.images.load(self.getBlockTexturePath(self._textureName))
                tex.name = self._unlocalizedName
            
            #First Image Texture
            mat.node_tree.nodes.new(type="ShaderNodeTexImage")
            mat.node_tree.nodes["Image Texture"].location = [-200, 75]
            mat.node_tree.nodes["Image Texture"].image = tex
            mat.node_tree.nodes["Image Texture"].interpolation = "Closest"
            mat.node_tree.nodes["Image Texture"].projection = "FLAT"
            mat.node_tree.links.new(mat.node_tree.nodes["Image Texture"].outputs[0], mat.node_tree.nodes["Diffuse BSDF"].inputs[0])
            mat.node_tree.links.new(mat.node_tree.nodes["Image Texture"].outputs[1], mat.node_tree.nodes["Mix Shader"].inputs[0])
            
            #UV Map
            mat.node_tree.nodes.new(type="ShaderNodeUVMap")
            mat.node_tree.nodes["UV Map"].location = [-400, 0]
            mat.node_tree.nodes["UV Map"].uv_map = "UVMap"
            mat.node_tree.links.new(mat.node_tree.nodes["UV Map"].outputs[0], mat.node_tree.nodes["Image Texture"].inputs[0])
        
        obj.data.materials.append(mat)
