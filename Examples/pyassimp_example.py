from pyassimp import load

with load('../Assignment4/objects/raymanModel.obj') as scene:

    assert len(scene.meshes)
    mesh = scene.meshes[0]

    assert len(mesh.vertices)
    print(mesh.vertices[0])
