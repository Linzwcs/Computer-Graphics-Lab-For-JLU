import numpy as np
from abc import ABCMeta, abstractmethod
from .algorithm import normalize_vector


class FaceProcess(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, **post):
        pass


class FaceDefaultProcess(FaceProcess):
    def __call__(self, **post):
        return post


class FaceNormalVectorProcess(FaceProcess):
    def __call__(self, **post):
        vertexs, triangles, textures, vertex_normal_vectors = (
            post["vertexs"],
            post["triangles"],
            post["textures"],
            post["vertex_normal_vectors"],
        )
        face_normal_vectors = []
        for triangle in triangles:
            face_normal_vectors += [
                normalize_vector(vertex_normal_vectors[triangle].mean(axis=0))
            ]
        post["face_normal_vectors"] = face_normal_vectors
        return post
