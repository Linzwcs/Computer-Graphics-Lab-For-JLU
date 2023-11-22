import numpy as np
from .algorithm import normalize_vector


class VertexProcess:
    def __call__(self, **post):
        vertexs = (post["M_view"] @ post["vertexs"].T).T
        vertexs_persp = (post["M_persp"] @ vertexs.T).T
        vertexs = vertexs / np.expand_dims(vertexs[:, 3], axis=1)
        vertexs_persp = vertexs_persp / np.expand_dims(vertexs_persp[:, 3], axis=1)

        post["vertexs"] = vertexs
        post["vertexs_persp"] = vertexs_persp

        if post.get("vertex_normal_vectors", None) is not None:
            vertex_normal_vectors = [[*vn, 0] for vn in post["vertex_normal_vectors"]]
            vertex_normal_vectors = (post["M_view"] @ post["vertex_normal_vectors"].T).T
            vertex_normal_vectors /= np.linalg.norm(
                vertex_normal_vectors, axis=1, keepdims=True
            )
            post["vertex_normal_vectors"] = vertex_normal_vectors
        return post
