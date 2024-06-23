import functools
import math
from typing import Annotated, Any, Iterable, Tuple

import imgui
from attr import define, field
from pydantic import BaseModel, Field
from ShaderFlow.Message import ShaderMessage
from ShaderFlow.Modules.Depth import (
    DepthAnything,
    DepthAnythingV2,
    DepthEstimator,
    Marigold,
    ZoeDepth,
)
from ShaderFlow.Scene import ShaderScene
from ShaderFlow.Texture import ShaderTexture
from ShaderFlow.Variable import ShaderVariable
from typer import Option

from Broken import pydantic_cli
from Broken.Externals.Upscaler import BrokenUpscaler, NoUpscaler, Realesr, Waifu2x
from Broken.Loaders import LoaderImage
from DepthFlow import DEPTHFLOW


class DepthFlowState(BaseModel):

    height: float = Field(default=0.35)
    """Peak value of the Depth Map, in the range [0, 1]. The camera is 1 distance away from depth=0
    at the z=1 plane, so this also controls the intensity of the effect"""

    static: float = Field(default=0.25)
    """Focal depth of offsets, in the range [0, 1]. A value of 0 makes the background (depth=0)
    stationary, while a value of 1 makes the foreground (depth=1) stationary on offset changes"""

    focus: float = Field(default=0.5)
    """Focal depth of projections, in the range [0, 1]. A value of 0 makes the background (depth=0)
    stationaty, while a value of 1 makes the foreground (depth=1) stationary on isometric changes"""

    invert: float = Field(default=0.0)
    """Interpolate between (0=max, 1=min)=0 or (0=min, 1=max)=1 Depth Map's value interpretation"""

    zoom: float = Field(default=1.0)
    """Camera zoom factor, in the range [0, inf]. 2 means a quarter of the image is visible"""

    isometric: float = Field(default=0.0)
    """Isometric factor of the camera projection. Zero is fully perspective, 1 is orthographic"""

    dolly: float = Field(default=0.0)
    """Same effect as isometric, but with "natural units" of AFAIK `isometric = atan(dolly)*(2/pi)`.
    Keeps the ray target constant and move back ray origins by this amount"""

    mirror: bool = Field(default=True)
    """Apply GL_MIRRORED_REPEAT to the image, makes it continuous"""

    # # Center

    center_x: float = Field(default=0)
    """Horizontal 'true' offset of the camera, the camea *is* above this point"""

    center_y: float = Field(default=0)
    """Vertical 'true' offset of the camera, the camea *is* above this point"""

    @property
    def center(self) -> Tuple[float, float]:
        """'True' offset of the camera, the camea *is* above this point"""
        return (self.center_x, self.center_y)

    @center.setter
    def center(self, value: Tuple[float, float]):
        self.center_x, self.center_y = value

    # # Origin

    origin_x: float = Field(default=0)
    """Hozirontal focal point of the offsets, *as if* the camera was above this point"""

    origin_y: float = Field(default=0)
    """Vertical focal point of the offsets, *as if* the camera was above this point"""

    @property
    def origin(self) -> Tuple[float, float]:
        """Focal point of the offsets, *as if* the camera was above this point"""
        return (self.origin_x, self.origin_y)

    @origin.setter
    def origin(self, value: Tuple[float, float]):
        self.origin_x, self.origin_y = value

    # # Parallax

    offset_x: float = Field(default=0)
    """Parallax horizontal displacement, change this over time for the 3D effect"""

    offset_y: float = Field(default=0)
    """Parallax vertical displacement, change this over time for the 3D effect"""

    @property
    def offset(self) -> Tuple[float, float]:
        """Parallax displacement, change this over time for the 3D effect"""
        return (self.offset_x, self.offset_y)

    @offset.setter
    def offset(self, value: Tuple[float, float]):
        self.offset_x, self.offset_y = value

    # # Special

    def reset(self) -> None:
        for name, field in self.model_fields.items(): # noqa
            setattr(self, name, field.default)

    class _PFX_DOF(BaseModel):
        enable:     bool  = Field(default=False)
        start:      float = Field(default=0.6)
        end:        float = Field(default=1.0)
        exponent:   float = Field(default=2.0)
        intensity:  float = Field(default=1)
        quality:    int   = Field(default=4)
        directions: int   = Field(default=16)

        def pipeline(self) -> Iterable[ShaderVariable]:
            yield ShaderVariable("uniform", "bool",  "iDofEnable",     self.enable)
            yield ShaderVariable("uniform", "float", "iDofStart",      self.start)
            yield ShaderVariable("uniform", "float", "iDofEnd",        self.end)
            yield ShaderVariable("uniform", "float", "iDofExponent",   self.exponent)
            yield ShaderVariable("uniform", "float", "iDofIntensity",  self.intensity/100)
            yield ShaderVariable("uniform", "int",   "iDofQuality",    self.quality)
            yield ShaderVariable("uniform", "int",   "iDofDirections", self.directions)

    dof: _PFX_DOF = Field(default_factory=_PFX_DOF)
    """Depth of Field Post-Processing configuration"""

    class _PFX_Vignette(BaseModel):
        enable:    bool  = Field(default=False)
        intensity: float = Field(default=30)
        decay:     float = Field(default=0.1)

        def pipeline(self) -> Iterable[ShaderVariable]:
            yield ShaderVariable("uniform", "bool",  "iVignetteEnable",    self.enable)
            yield ShaderVariable("uniform", "float", "iVignetteIntensity", self.intensity)
            yield ShaderVariable("uniform", "float", "iVignetteDecay",     self.decay)

    vignette: _PFX_Vignette = Field(default_factory=_PFX_Vignette)
    """Vignette Post-Processing configuration"""

    def pipeline(self) -> Iterable[ShaderVariable]:
        yield ShaderVariable("uniform", "float", "iDepthHeight",    self.height)
        yield ShaderVariable("uniform", "float", "iDepthStatic",    self.static)
        yield ShaderVariable("uniform", "float", "iDepthFocus",     self.focus)
        yield ShaderVariable("uniform", "float", "iDepthInvert",    self.invert)
        yield ShaderVariable("uniform", "float", "iDepthZoom",      self.zoom)
        yield ShaderVariable("uniform", "float", "iDepthIsometric", self.isometric)
        yield ShaderVariable("uniform", "float", "iDepthDolly",     self.dolly)
        yield ShaderVariable("uniform", "vec2",  "iDepthCenter",    self.center)
        yield ShaderVariable("uniform", "vec2",  "iDepthOrigin",    self.origin)
        yield ShaderVariable("uniform", "vec2",  "iDepthOffset",    self.offset)
        yield ShaderVariable("uniform", "bool",  "iDepthMirror",    self.mirror)
        yield from self.dof.pipeline()
        yield from self.vignette.pipeline()

# -------------------------------------------------------------------------------------------------|

DEPTHFLOW_ABOUT = """
🌊 Image to → 2.5D Parallax Effect Video. High quality, user first.\n

Usage: Chain commands, at minimum just [green]main[/green] for a realtime window, drag and drop images
       - The --main command is used for exporting videos, setting quality, resolution
       - All commands have a --help option with extensible configuration

Examples:
• (depthflow realesr --scale 2 input -i ~/image.png main -o ./output.mp4 --ssaa 1.5)
• (depthflow input -i ~/image16x9.png main -h 1440) [bright_black]# Auto calculates w=2560[/bright_black]
"""

@define
class DepthFlowScene(ShaderScene):
    __name__ = "DepthFlow"

    # Constants
    DEFAULT_IMAGE = "https://w.wallhaven.cc/full/pk/wallhaven-pkz5r9.png"
    DEPTH_SHADER  = (DEPTHFLOW.RESOURCES.SHADERS/"DepthFlow.glsl")

    # DepthFlow objects
    estimator: DepthEstimator = field(factory=DepthAnything)
    upscaler: BrokenUpscaler = field(factory=NoUpscaler)
    state: DepthFlowState = field(factory=DepthFlowState)

    def input(self,
        image: Annotated[str,  Option("--image",   "-i", help="Background Image [green](Path, URL, NumPy, PIL)[/green]")],
        depth: Annotated[str,  Option("--depth",   "-d", help="Depthmap of the Image [medium_purple3](None to estimate)[/medium_purple3]")]=None,
    ) -> None:
        """Load an Image from Path, URL and its estimated DepthMap to the Scene, and optionally upscale it. See 'input --help'"""
        image = self.upscaler.upscale(LoaderImage(image))
        depth = LoaderImage(depth) or self.estimator.estimate(image)
        self.aspect_ratio = (image.width/image.height)
        self.image.from_image(image)
        self.depth.from_image(depth)

    def _pydantic_cli(self, option: Any, attribute: str) -> None:
        @functools.wraps(pydantic_cli(option))
        def wrapper(*args, **kwargs) -> None:
            for name, value in kwargs.items():
                setattr(option, name, value)
            setattr(self, attribute, option)
        return wrapper

    def commands(self):
        self.typer.description = DEPTHFLOW_ABOUT
        self.typer.command(self.input)

        with self.typer.panel("⭐️ Upscalers"):
            self.typer.command(self._pydantic_cli(Realesr(), "upscaler"), name="realesr",
                help="Configure and use RealESRGAN [green](See 'realesr --help' for options)[/green] [dim](by https://github.com/xinntao/Real-ESRGAN)[/dim]")
            self.typer.command(self._pydantic_cli(Waifu2x(), "upscaler"), name="waifu2x",
                help="Configure and use Waifu2x    [green](See 'waifu2x --help' for options)[/green] [dim](by https://github.com/nihui/waifu2x-ncnn-vulkan)[/dim]")

        with self.typer.panel("🌊 Depth Estimators"):
            self.typer.command(self._pydantic_cli(DepthAnything(), "estimator"), name="anything",
                help="Configure and use DepthAnything   [green](See 'anything  --help' for options)[/green] [dim](by https://github.com/LiheYoung/Depth-Anything)[/dim]")
            self.typer.command(self._pydantic_cli(DepthAnythingV2(), "estimator"), name="anything2",
                help="Configure and use DepthAnythingV2 [green](See 'anything2 --help' for options)[/green] [dim](by https://github.com/DepthAnything/Depth-Anything-V2)[/dim]")
            self.typer.command(self._pydantic_cli(ZoeDepth(), "estimator"), name="zoedepth",
                help="Configure and use ZoeDepth        [green](See 'zoedepth  --help' for options)[/green] [dim](by https://github.com/isl-org/ZoeDepth)[/dim]")
            self.typer.command(self._pydantic_cli(Marigold(), "estimator"), name="marigold",
                help="Configure and use Marigold        [green](See 'marigold  --help' for options)[/green] [dim](by https://github.com/prs-eth/Marigold)[/dim]")

    def setup(self):
        if self.image.is_empty():
            self.input(image=DepthFlowScene.DEFAULT_IMAGE)
        self.time = 0

    def build(self):
        ShaderScene.build(self)
        self.image = ShaderTexture(scene=self, name="image").repeat(False)
        self.depth = ShaderTexture(scene=self, name="depth").repeat(False)
        self.shader.fragment = self.DEPTH_SHADER
        self.aspect_ratio = (16/9)

    def update(self):

        # In and out dolly zoom
        self.state.dolly = (0.5 + 0.5*math.cos(self.cycle))

        # Infinite 8 loop shift
        self.state.offset_x = (0.2 * math.sin(1*self.cycle))
        self.state.offset_y = (0.2 * math.sin(2*self.cycle))

        # Integral rotation (better for realtime)
        self.camera.rotate(
            direction=self.camera.base_z,
            angle=math.cos(self.cycle)*self.dt*0.4
        )

        # Fixed known rotation
        # self.camera.rotate2d(1.5*math.sin(self.cycle))

        # Zoom in on the start
        # self.config.zoom = 1.2 - 0.2*(2/math.pi)*math.atan(self.time)

    def handle(self, message: ShaderMessage):
        ShaderScene.handle(self, message)

        if isinstance(message, ShaderMessage.Window.FileDrop):
            files = iter(message.files)
            self.input(image=next(files), depth=next(files, None))

    def pipeline(self) -> Iterable[ShaderVariable]:
        yield from ShaderScene.pipeline(self)
        yield from self.state.pipeline()

    def ui(self) -> None:
        if (state := imgui.slider_float("Height", self.state.height, 0, 1, "%.2f"))[0]:
            self.state.height = max(0, state[1])
        if (state := imgui.slider_float("Static", self.state.static, 0, 1, "%.2f"))[0]:
            self.state.static = max(0, state[1])
        if (state := imgui.slider_float("Focus", self.state.focus, 0, 1, "%.2f"))[0]:
            self.state.focus = max(0, state[1])
        if (state := imgui.slider_float("Invert", self.state.invert, 0, 1, "%.2f"))[0]:
            self.state.invert = max(0, state[1])
        if (state := imgui.slider_float("Zoom", self.state.zoom, 0, 2, "%.2f"))[0]:
            self.state.zoom = max(0, state[1])
        if (state := imgui.slider_float("Isometric", self.state.isometric, 0, 1, "%.2f"))[0]:
            self.state.isometric = max(0, state[1])
        if (state := imgui.slider_float("Dolly", self.state.dolly, 0, 5, "%.2f"))[0]:
            self.state.dolly = max(0, state[1])

        imgui.text("- True camera position")
        if (state := imgui.slider_float("Center X", self.state.center_x, -self.aspect_ratio, self.aspect_ratio, "%.2f"))[0]:
            self.state.center_x = state[1]
        if (state := imgui.slider_float("Center Y", self.state.center_y, -1, 1, "%.2f"))[0]:
            self.state.center_y = state[1]

        imgui.text("- Fixed point at height changes")
        if (state := imgui.slider_float("Origin X", self.state.origin_x, -self.aspect_ratio, self.aspect_ratio, "%.2f"))[0]:
            self.state.origin_x = state[1]
        if (state := imgui.slider_float("Origin Y", self.state.origin_y, -1, 1, "%.2f"))[0]:
            self.state.origin_y = state[1]

        imgui.text("- Parallax offset")
        if (state := imgui.slider_float("Offset X", self.state.offset_x, -2, 2, "%.2f"))[0]:
            self.state.offset_x = state[1]
        if (state := imgui.slider_float("Offset Y", self.state.offset_y, -2, 2, "%.2f"))[0]:
            self.state.offset_y = state[1]
