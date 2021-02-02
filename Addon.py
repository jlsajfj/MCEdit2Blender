import bpy
import importlib
import math
import mathutils
from bpy.props import (StringProperty)
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
import blockmanager
import nbt
importlib.reload(blockmanager)
from blockmanager import BlockManager


class SchematicImporter(Operator, ImportHelper) :
    bl_idname = "import.schematic"
    bl_label = "Import Schematic"
    
    _blockManager = BlockManager()
 
    def execute(self, context) :
        filename_ext = ".schematic"
        
        filter_glob = StringProperty(default="*.schematic", options={'HIDDEN'},)

        if self.filepath.split('\\')[-1].split('.')[1].lower() != 'schematic':
            print ("  Selected file = ", self.filepath)
            raise IOError("The selected input file is not a *.schematic file")

        nbtfile = nbt.nbt.NBTFile(self.filepath,'rb')

        height = nbtfile["Height"].value
        width = nbtfile["Width"].value
        length = nbtfile["Length"].value

        bpy.data.scenes[0].render.engine = "CYCLES"
        bpy.data.scenes[0].render.fps = 20
        bpy.data.scenes[0].render.fps_base = 1
        bpy.context.user_preferences.system.use_mipmaps = False
        bpy.types.Object.blockId = bpy.props.IntProperty(name="Block ID", description="Stores the id of this object's block", default=0)
        bpy.types.Object.blockMetadata = bpy.props.IntProperty(name="Block Metadata", description="Stores the metadata of this object's block", default=0)
        for index, dataValue in enumerate(nbtfile["Blocks"].value):
            if dataValue != 0:
                self._blockManager.draw(context, index % width - math.floor(width / 2), length - math.floor((index % (width * length)) / width) - math.ceil(length / 2) - 1, math.floor(index / (width * length)), dataValue, nbtfile["Data"][index])

        return {"FINISHED"}

def import_images_button(self, context):
    self.layout.operator(SchematicImporter.bl_idname, text="MCEdit Schematic (.schematic)")

def register():
    bpy.utils.register_class(SchematicImporter)
    bpy.types.INFO_MT_file_import.append(import_images_button)
 
def unregister():
    bpy.utils.unregister_class(SchematicImporter)
    bpy.types.INFO_MT_mesh_add.remove(import_images_button)
 
if __name__ == "__main__":
    register()
