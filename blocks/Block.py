import bpy
import mathutils

class Block:
    """A basic block with a single texture
    
    This class should be inherited by every other block class
    """

    def __init__(self, id, unlocalizedName, textureName):
        self._id = id
        self._unlocalizedName = unlocalizedName
        self._textureName = textureName
    
    def getBlockTexturePath(self, textureName):
        return bpy.path.abspath("//textures/blocks/" + textureName + ".png")

    def make(self, x, y, z, metadata):
        obj = self.makeObject(x, y, z, metadata)
        self.applyMaterial(obj, metadata)
    
    def makeObject(self, x, y, z, metadata):
        mesh = bpy.data.meshes.new(name="Block")
        mesh.from_pydata([[-0.5,-0.5,-0.5],[0.5,-0.5,-0.5],[-0.5,0.5,-0.5],[0.5,0.5,-0.5],[-0.5,-0.5,0.5],[0.5,-0.5,0.5],[-0.5,0.5,0.5],[0.5,0.5,0.5]],[],[[0,1,3,2],[4,5,7,6],[0,1,5,4],[0,2,6,4],[2,3,7,6],[1,3,7,5]])
        mesh.update()

        obj = bpy.data.objects.new("Block", mesh)
        obj.location.x = x + 0.5
        obj.location.y = y + 0.5
        obj.location.z = z + 0.5
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
            mat.use_nodes = True
            mat.node_tree.links.remove(mat.node_tree.links[0])
            mat.node_tree.nodes["Material Output"].location = [600, 0]

            #Mix Shader
            mat.node_tree.nodes.new(type="ShaderNodeMixShader")
            mat.node_tree.nodes["Mix Shader"].location = [400,0]
            mat.node_tree.links.new(mat.node_tree.nodes["Mix Shader"].outputs[0], mat.node_tree.nodes["Material Output"].inputs[0])

            #Multiply
            mat.node_tree.nodes.new(type="ShaderNodeMath")
            mat.node_tree.nodes["Math"].location = [200,200]
            mat.node_tree.nodes["Math"].operation = "MULTIPLY"
            mat.node_tree.nodes["Math"].use_clamp = True
            mat.node_tree.links.new(mat.node_tree.nodes["Math"].outputs[0], mat.node_tree.nodes["Mix Shader"].inputs[0])

            #First Diffuse Shader (already exists from default use_node setup)
            mat.node_tree.nodes["Diffuse BSDF"].location = [200, 0]
            mat.node_tree.links.new(mat.node_tree.nodes["Diffuse BSDF"].outputs[0], mat.node_tree.nodes["Mix Shader"].inputs[1])

            #Second Diffuse Shader
            mat.node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
            mat.node_tree.nodes["Diffuse BSDF.001"].location = [200,-150]
            mat.node_tree.links.new(mat.node_tree.nodes["Diffuse BSDF.001"].outputs[0], mat.node_tree.nodes["Mix Shader"].inputs[2])

            #Initialize Texture
            try:
                tex = bpy.data.images[self._unlocalizedName]
            except KeyError:
                tex = bpy.data.images.load(self.getBlockTexturePath(self._textureName))
                tex.name = self._unlocalizedName

            #First Image Texture
            mat.node_tree.nodes.new(type="ShaderNodeTexImage")
            mat.node_tree.nodes["Image Texture"].location = [0, 50]
            mat.node_tree.nodes["Image Texture"].image = tex
            mat.node_tree.nodes["Image Texture"].interpolation = "Closest"
            mat.node_tree.nodes["Image Texture"].projection = "BOX"
            mat.node_tree.links.new(mat.node_tree.nodes["Image Texture"].outputs[0], mat.node_tree.nodes["Diffuse BSDF"].inputs[0])

            #Second Image Texture
            mat.node_tree.nodes.new(type="ShaderNodeTexImage")
            mat.node_tree.nodes["Image Texture.001"].location = [0, -250]
            mat.node_tree.nodes["Image Texture.001"].image = tex
            mat.node_tree.nodes["Image Texture.001"].interpolation = "Closest"
            mat.node_tree.nodes["Image Texture.001"].projection = "BOX"
            mat.node_tree.links.new(mat.node_tree.nodes["Image Texture.001"].outputs[0], mat.node_tree.nodes["Diffuse BSDF.001"].inputs[0])

            #Separate XYZ
            mat.node_tree.nodes.new(type="ShaderNodeSeparateXYZ")
            mat.node_tree.nodes["Separate XYZ"].location = [-300,200]
            mat.node_tree.links.new(mat.node_tree.nodes["Separate XYZ"].outputs[2], mat.node_tree.nodes["Math"].inputs[0])
            mat.node_tree.links.new(mat.node_tree.nodes["Separate XYZ"].outputs[2], mat.node_tree.nodes["Math"].inputs[1])

            #First Mapping
            mat.node_tree.nodes.new(type="ShaderNodeMapping")
            mat.node_tree.nodes["Mapping"].location = [-400, 0]
            mat.node_tree.nodes["Mapping"].scale[1] = -1.0
            mat.node_tree.links.new(mat.node_tree.nodes["Mapping"].outputs[0], mat.node_tree.nodes["Image Texture"].inputs[0])

            #Second Mapping
            mat.node_tree.nodes.new(type="ShaderNodeMapping")
            mat.node_tree.nodes["Mapping.001"].location = [-400,-300]
            mat.node_tree.nodes["Mapping.001"].rotation = mathutils.Euler((0.0, 0.0, -1.5707963705062866), 'XYZ')
            mat.node_tree.nodes["Mapping.001"].scale[0] = -1.0
            mat.node_tree.links.new(mat.node_tree.nodes["Mapping.001"].outputs[0], mat.node_tree.nodes["Image Texture.001"].inputs[0])

            #Texture Coordinate
            mat.node_tree.nodes.new(type="ShaderNodeTexCoord")
            mat.node_tree.nodes["Texture Coordinate"].location = [-600,0]
            mat.node_tree.links.new(mat.node_tree.nodes["Texture Coordinate"].outputs[0], mat.node_tree.nodes["Mapping"].inputs[0])
            mat.node_tree.links.new(mat.node_tree.nodes["Texture Coordinate"].outputs[0], mat.node_tree.nodes["Mapping.001"].inputs[0])
            mat.node_tree.links.new(mat.node_tree.nodes["Texture Coordinate"].outputs[1], mat.node_tree.nodes["Separate XYZ"].inputs[0])

        obj.data.materials.append(mat)
