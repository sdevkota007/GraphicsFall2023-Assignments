from pyassimp import load

with load('../objects/rayman/raymanModel.obj') as scene:

    assert len(scene.meshes)
    mesh = scene.meshes[0]

    assert len(mesh.vertices)
    print(mesh.vertices[0])
