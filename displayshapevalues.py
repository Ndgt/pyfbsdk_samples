from shapefunctions import*
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

    print("\n--- shapkey & values ---", file=outputfile)
    for mesh in meshList:
        print("Mesh:" + mesh.GetNode().GetName(), file=outputfile)
        if HasBlendShape(mesh)[0]:
            blendshapeindex = HasBlendShape(mesh)[1]
            shapekeys = GetShapekeys(mesh)
            for i in range(mesh.GetShapeCount()):
                shapecurve = mesh.GetShapeChannel(blendshapeindex, i, lAnimLayer)
                if shapecurve:
                    KeyIndex = 0
                    for j in range(shapecurve.KeyGetCount()):
                        shape = shapekeys[i].GetName()
                        frame = shapecurve.KeyGetTime(j).GetFrameCount()
                        value = shapecurve.KeyGetValue(j)
                        print(f"frame:{frame} shapekey:{shape} value:{value}", file=outputfile)
        print("", file=outputfile)        

print("'data.txt' was written successfully.")

# Cleanup
lImporter.Destroy()
lSdkManager.Destroy()