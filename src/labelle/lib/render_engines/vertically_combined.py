from __future__ import annotations

from typing import Sequence

from PIL import Image

from labelle.lib.render_engines.empty import EmptyRenderEngine
from labelle.lib.render_engines.render_context import RenderContext
from labelle.lib.render_engines.render_engine import RenderEngine


class VerticallyCombinedRenderEngine(RenderEngine):
    padding: int

    def __init__(
        self,
        render_engines: Sequence[RenderEngine],
        padding: int = 0,
    ):
        super().__init__()
        self.render_engines = render_engines
        self.padding = padding

    def render(self, context: RenderContext) -> Image.Image:
        render_engines = self.render_engines or [EmptyRenderEngine()]
        n = len(render_engines)

        total_padding = self.padding * (n - 1)
        available_height = context.height_px - total_padding
        per_engine_height = available_height // n

        bitmaps = []
        for engine in render_engines:
            child_context = RenderContext(
                height_px=per_engine_height,
                background_color=context.background_color,
                foreground_color=context.foreground_color,
            )
            bitmaps.append(engine.render(child_context))

        if len(bitmaps) == 1:
            return bitmaps[0]

        max_width = max(b.width for b in bitmaps)
        total_height = sum(b.height for b in bitmaps) + total_padding
        merged_bitmap = Image.new("1", (max_width, total_height))

        y_offset = 0
        for bitmap in bitmaps:
            x_offset = (max_width - bitmap.width) // 2
            merged_bitmap.paste(bitmap, box=(x_offset, y_offset))
            y_offset += bitmap.height + self.padding

        return merged_bitmap
