from fbx import*
from io import TextIOWrapper
import argparse

def HasBlendShape(mesh: FbxMesh) -> tuple:
    result = False
    index = -1
    count = mesh.GetDeformerCount()
    if count > 0:
        for i in range(count):
            if type(mesh.GetDeformer(i)) == FbxBlendShape:
                result = True
                index = i
                break
    return (result, index)

def GetBlendShape(mesh: FbxMesh) -> FbxBlendShape:
    for i in mesh.GetDeformerCount():
        deformer = mesh.GetDeformer(i)
        if type(deformer) == FbxBlendShape:
            return deformer

def DisplayDeformers(outputfile:TextIOWrapper, mesh: FbxMesh) -> None:
    deformers = dict([["blendshape", ""], ["skin", ""]])
    for i in range(mesh.GetDeformerCount()):
        deformer = mesh.GetDeformer(i)
        if type(deformer) == FbxBlendShape:
            deformers["blendshape"] = deformer.GetName()
        elif type(deformer) == FbxSkin:
            deformers["skin"] = deformer.GetName()

    # write to ouput file
    print("Mesh:" + mesh.GetNode().GetName(), file=outputfile)
    print(f'  blendshape : {deformers["blendshape"]}', file=outputfile)
    print(f'  skin       : {deformers["skin"]}', file=outputfile)

def DisplayShapekeys(outputfile:TextIOWrapper, mesh: FbxMesh) -> None:
    if HasBlendShape(mesh)[0]:
        print("Mesh:" + mesh.GetNode().GetName(), file=outputfile)
        shapecount = mesh.GetShapeCount()
        blendshapeindex = HasBlendShape(mesh)[1]
        for i in range(shapecount):
            shape = mesh.GetShape(blendshapeindex, i, 0)
            print(f'  "shapekey : " {shape.GetName()}', file=outputfile)
        print("", file=outputfile)


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
        DisplayDeformers(outputfile, mesh)

    print("\n--- shapkeys ---", file=outputfile)
    for mesh in meshList:
        DisplayShapekeys(outputfile, mesh)

print("'data.txt' was written successfully.")

# Cleanup
lImporter.Destroy()
lSdkManager.Destroy()