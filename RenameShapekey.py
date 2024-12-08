from fbx import*
from pathlib import Path
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
    print("~ wait until convert finishes ~")
else:
    print("Failed to import the scene:")
    print(lImporter.GetStatus().GetErrorString())

# Import file contents to the scene container
lScene = FbxScene.Create(lSdkManager, "New Scene")
lImporter.Import(lScene)

# Get Animation Components
lAnimStack = lScene.GetCurrentAnimationStack()
lAnimLayer = lAnimStack.GetMember(0)

convertmaps = {
    "a" : "あ",
    "i" : "い", 
    "u" : "う",
    "e" : "え",
    "o" : "お"
}

# Get All mesh in the Scene
meshList = list()
for i in range(lScene.GetRootNode().GetChildCount()):
    child = lScene.GetRootNode().GetChild(i)
    if type(child.GetNodeAttribute()) == FbxMesh:
        meshList.append(child.GetNodeAttribute())

for mesh in meshList:
    if HasBlendShape(mesh)[0]:
        blendshapeindex = HasBlendShape(mesh)[1]
        for i in range(mesh.GetShapeCount()):
            for word in convertmaps.keys():
                if word == mesh.GetShape(blendshapeindex, i, 0).GetName():
                    mesh.GetShape(blendshapeindex, i, 0).SetName(convertmaps[word])

# Prepare for export
inputfilepath = Path(args.fbxfilepath)
parent_dir = inputfilepath.parent
stem = inputfilepath.stem
suffix = inputfilepath.suffix
fbxoutputpath = stem + "_ShapeRenamed" + suffix
lExporter = FbxExporter.Create(lSdkManager, "")
lExporter.Initialize(fbxoutputpath, -1, ios)

# Export the Scene
if lExporter.Export(lScene):
    print("The converted file successfully exported.")
    print("Shapekeys were converted successfully.")
else:
    print("Failed to export the test fbx file...")

# Cleanup
lImporter.Destroy()
lExporter.Destroy()
lSdkManager.Destroy()