from __future__ import annotations

import io
import math
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from labelle.lib.render_engines.exceptions import NoContentError
from labelle.lib.render_engines.render_context import RenderContext
from labelle.lib.render_engines.render_engine import (
    RenderEngine,
    RenderEngineException,
)


class PicturePathDoesNotExist(RenderEngineException):
    pass


class UnidentifiedImageFileError(RenderEngineException):
    def __init__(self, exception) -> None:
        super().__init__(exception)


class PictureRenderEngine(RenderEngine):
    def __init__(self, picture_path: Path | str) -> None:
        super().__init__()
        if picture_path == "":
            raise NoContentError()
        self.picture_path = Path(picture_path)
        if not self.picture_path.is_file():
            raise PicturePathDoesNotExist(
                f"Picture path does not exist: {picture_path}"
            )

    @staticmethod
    def _open_svg(path: Path, height_px: int) -> Image.Image:
        """Render an SVG file to a PIL Image at the target height."""
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM

        drawing = svg2rlg(str(path))
        if drawing is None:
            raise UnidentifiedImageFileError(
                Exception(f"Failed to parse SVG: {path}")
            )
        # Scale to target height
        scale = height_px / drawing.height
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        png_data = renderPM.drawToString(drawing, fmt="PNG")
        return Image.open(io.BytesIO(png_data))

    def render(self, context: RenderContext) -> Image.Image:
        height_px = context.height_px
        try:
            if self.picture_path.suffix.lower() == ".svg":
                img = self._open_svg(self.picture_path, height_px)
            else:
                img = Image.open(self.picture_path)
                if img.height > height_px:
                    ratio = height_px / img.height
                    img = img.resize((math.ceil(img.width * ratio), height_px))

            img = img.convert("L", palette=Image.AFFINE)
            return ImageOps.invert(img).convert("1")
        except UnidentifiedImageError as e:
            raise UnidentifiedImageFileError(e) from e
