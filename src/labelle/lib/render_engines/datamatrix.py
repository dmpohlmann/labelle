from PIL import Image

from labelle.lib.constants import DataMatrix
from labelle.lib.render_engines.exceptions import NoContentError
from labelle.lib.render_engines.render_context import RenderContext
from labelle.lib.render_engines.render_engine import (
    RenderEngine,
    RenderEngineException,
)
from labelle.lib.utils import draw_image, scaling


class DataMatrixTooBigError(RenderEngineException):
    def __init__(self) -> None:
        msg = "Too much information to store in the DataMatrix code"
        super().__init__(msg)


class DataMatrixRenderEngine(RenderEngine):
    _content: str

    def __init__(self, content: str):
        super().__init__()
        if not len(content):
            raise NoContentError()
        self._content = content

    def render(self, context: RenderContext) -> Image.Image:
        try:
            dm = DataMatrix(self._content)
            matrix = dm.matrix
        except ValueError as e:
            if "too long" in str(e).lower():
                raise DataMatrixTooBigError() from e
            raise
        rows = len(matrix)
        cols = len(matrix[0]) if matrix else 0

        height_px = context.height_px
        dm_scale = height_px // rows
        if not dm_scale:
            raise DataMatrixTooBigError()

        dm_offset = (height_px - rows * dm_scale) // 2
        label_width_px = cols * dm_scale

        bitmap = Image.new("1", (label_width_px, height_px))

        with draw_image(bitmap) as draw:
            for i, row in enumerate(matrix):
                for j, val in enumerate(row):
                    if val:
                        dm_pixels = scaling(
                            (j * dm_scale, i * dm_scale + dm_offset), dm_scale
                        )
                        draw.point(dm_pixels, 1)
        return bitmap
