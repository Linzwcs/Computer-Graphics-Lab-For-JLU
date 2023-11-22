import numpy as np


class Object3D:
    def __init__(self, vertexs=None, triangles=None, **args):
        args["vertexs"] = np.array([[*v, 1] for v in vertexs])
        args["triangles"] = np.array(triangles)
        if args.get("textures", None) is not None:
            args["textures"] = np.array(args["textures"])
        if args.get("vertex_normal_vectors", None) is not None:
            args["vertex_normal_vectors"] = np.array(
                [[*vn, 0] for vn in args["vertex_normal_vectors"]]
            )
        if args.get("face_texture_idxs", None) is not None:
            args["face_texture_idxs"] = np.array(args["face_texture_idxs"])

        self.post_process_obj = args

    def get_post_obj(self):
        return self.post_process_obj
