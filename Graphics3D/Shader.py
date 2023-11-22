import numpy as np
from .Transform import Transfrom
from .FaceProcess import FaceDefaultProcess
from .Render import Render, BlinnPhongRender


class Shader:
    def __init__(
        self,
        width=1000,
        height=600,
    ):
        "pipline:"
        self.MVP_processor = None
        self.model_transform_processor = Transfrom()
        self.vertexs_processor = None
        self.face_processor = FaceDefaultProcess()
        self.lighting_processor = None
        self.rasterizer_processor = None
        self.texture_mapping_processor = None
        self.render_processor = BlinnPhongRender()
        self.display_image = None
        self.width = width
        self.height = height

    def set_vertexs_processor(self, vertexs_processor):
        self.vertexs_processor = vertexs_processor

    def set_face_processor(self, face_processor):
        self.face_processor = face_processor

    def set_lighting_processor(self, lighting):
        self.lighting_processor = lighting

    def set_MVP_processor(self, mvp):
        self.MVP_processor = mvp

    def set_texture_mapping_processor(self, texture_processor):
        self.texture_mapping_processor = texture_processor

    def set_rasterizer_processor(self, rasterizer_processor):
        self.rasterizer_processor = rasterizer_processor

    def set_render_processor(self, render_processor):
        self.render_processor = render_processor

    def display(self, object3d):
        post = object3d.get_post_obj()
        post["width"], post["height"] = self.width, self.height

        post = self.MVP_processor(**post)
        # if self.model_transform_processor is not None:
        post = self.model_transform_processor(**post)
        post = self.vertexs_processor(**post)
        post = self.face_processor(**post)
        post = self.rasterizer_processor(**post)
        post = self.texture_mapping_processor(**post)
        post = self.lighting_processor(**post)
        post = self.render_processor(**post)
        # light_image, texture_image = post["light_image"], post["texture_image"]
        # print(light_image, texture_image)
        # display_image = post["image"]
        self.display_image = post["image"].transpose(1, 0, 2)
        return self.display_image
