from .FaceProcess import FaceDefaultProcess, FaceNormalVectorProcess
from .Lighting import BaseLighting, BlinnPhongLighting
from .Rasterizer import Rasterizer
from .MVP import MVP
from .Shape import Object3D
from .Texture import (
    TextureDefaultProcess,
    TextureRandomColorProcess,
    TextureImageProcess,
)
from .VertexProcess import VertexProcess
from .Transform import Transfrom
from .Shader import Shader
from .Render import DefaultRender, BlinnPhongRender

from Graphics3D import (
    Shader,
    Object3D,
    VertexProcess,
    FaceDefaultProcess,
    MVP,
    TextureDefaultProcess,
    TextureRandomColorProcess,
    TextureImageProcess,
    BaseLighting,
    BlinnPhongLighting,
    Rasterizer,
    DefaultRender,
    BlinnPhongRender,
)
import numpy as np


def load_obj(obj_path):
    (
        vertexs,
        triangels,
        normal_vectors,
        textures,
        face_texture_idxs,
        vertexs2normal_vectors,
    ) = ([], [], [], [], [], {})
    with open(obj_path, "r") as f:
        for line in f:
            variants = line.strip().split()

            if len(variants) == 0:
                continue
            match (variants[0]):
                case ("v"):
                    vertexs += [[float(v) for v in variants[1:]]]
                case ("vt"):
                    textures += [[float(t) for t in variants[1:]]]
                case ("vn"):
                    normal_vectors += [[float(nv) for nv in variants[1:]]]
                case ("f"):
                    triangle_nv_idxs, num_triangle = None, 0
                    if len(variants) == 5:
                        triangels += [
                            [int(tri.split("/")[0]) for tri in variants[1:4]],
                            [
                                int(tri.split("/")[0])
                                for tri in variants[1:2] + variants[3:]
                            ],
                        ]
                        face_texture_idxs += [
                            [int(tri.split("/")[1]) for tri in variants[1:4]],
                            [
                                int(tri.split("/")[1])
                                for tri in variants[1:2] + variants[3:]
                            ],
                        ]
                        triangle_nv_idxs = [
                            [int(tri.split("/")[2]) for tri in variants[1:4]],
                            [
                                int(tri.split("/")[2])
                                for tri in variants[1:2] + variants[3:]
                            ],
                        ]
                        num_triangle = 2
                    elif len(variants) == 4:
                        triangels += [[int(tri.split("/")[0]) for tri in variants[1:]]]
                        face_texture_idxs += [
                            [int(tri.split("/")[1]) for tri in variants[1:4]]
                        ]
                        triangle_nv_idxs = [
                            [int(tri.split("/")[2]) for tri in variants[1:4]],
                        ]
                        num_triangle = 1

                    for tri, nv_idx in zip(
                        triangels[-num_triangle:], triangle_nv_idxs[-num_triangle:]
                    ):
                        for tri_p, nv_idx_p in zip(tri, nv_idx):
                            if vertexs2normal_vectors.get(tri_p, None) is None:
                                vertexs2normal_vectors[tri_p] = nv_idx_p
                            else:
                                assert vertexs2normal_vectors[tri_p] == nv_idx_p
                case _:
                    pass
        vertex_normal_vectors = []
        for i in range(len(vertexs)):
            vertex_normal_vectors.append(
                normal_vectors[vertexs2normal_vectors[i + 1] - 1]
            )
    return {
        "vertexs": np.array(vertexs),
        "triangles": np.array(triangels) - 1,
        "textures": np.array(textures),
        "face_texture_idxs": np.array(face_texture_idxs) - 1,
        "vertex_normal_vectors": np.array(vertex_normal_vectors),
    }
