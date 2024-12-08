from shapefunctions import*
from io import TextIOWrapper
import argparse

# Setup argument parser
parser = argparse.ArgumentParser()
parser.add_argument("fbxfilepath", help="Path to the fbx")
args = parser.parse_args()

# Configure sdk manager
lSdkManager = FbxManager.Create()
ios = FbxIOSettings.Create(lSdkManager, "IOSRoot") # IOSROOT
lSdkManager.SetIOSettings(ios)

# Create an importer
lImporter = FbxImporter.Create(lSdkManager, "")
if lImporter.Initialize(args.fbxfilepath, -1, lSdkManager.GetIOSettings()):
    print("The scene imported successfully.")
    print("~ wait until output finishes ~")
else:
    print("Failed to import the scene:")
    print(lImporter.GetStatus().GetErrorString())

# Import file contents to the scene container
lScene = FbxScene.Create(lSdkManager, "New Scene")
lImporter.Import(lScene)

# Get Animation Components
lAnimStack = lScene.GetCurrentAnimationStack()
lAnimLayer = lAnimStack.GetMember(0)


with open("data.txt", "w", encoding="utf-8") as outputfile:
    # Get All mesh in the Scene
    meshList = list()
    for i in range(lScene.GetRootNode().GetChildCount()):
        child = lScene.GetRootNode().GetChild(i)
        if type(child.GetNodeAttribute()) == FbxMesh:
            meshList.append(child.GetNodeAttribute())
    
    # write in output file
    print("--- FBX file Name ---", file=outputfile)
    print(args.fbxfilepath, file=outputfile)
    print("\n--- blendshapes and skins ---", file=outputfile)
    for mesh in meshList:
        deformers = GetDeformersName(mesh)
        print("Mesh:" + mesh.GetNode().GetName(), file=outputfile)
        print(f'  blendshape : {deformers["blendshape"]}', file=outputfile)
        print(f'  skin       : {deformers["skin"]}', file=outputfile)

    print("\n--- shapkeys ---", file=outputfile)
    for mesh in meshList:
        shapekeylist = GetShapekeys(mesh)
        for shape in shapekeylist:
            print(f'  "shapekey : " {shape.GetName()}', file=outputfile)

print("'data.txt' was written successfully.")

# Cleanup
lImporter.Destroy()
lSdkManager.Destroy()