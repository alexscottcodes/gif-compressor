from cog import BasePredictor, Input, Path
import subprocess
import tempfile
import os
import shutil
from typing import Optional
import json


class Predictor(BasePredictor):
    def setup(self):
        """Load dependencies - gifsicle should be available in the container"""
        # Verify gifsicle is installed
        try:
            result = subprocess.run(
                ["gifsicle", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Gifsicle version: {result.stdout.strip()}")
        except Exception as e:
            raise RuntimeError(f"Gifsicle not available: {e}")

    def predict(
        self,
        gif: Path = Input(description="Input GIF file to compress"),
        optimization_level: int = Input(
            description="Optimization level (1-3). Higher = better compression but slower. 3 is recommended.",
            default=3,
            ge=1,
            le=3
        ),
        lossy_compression: Optional[int] = Input(
            description="Lossy compression level (20-200). Lower = better quality. 80 is a good balance. Leave empty for lossless.",
            default=None,
            ge=20,
            le=200
        ),
        colors: Optional[int] = Input(
            description="Reduce to this many colors (2-256). Leave empty to keep original colors.",
            default=None,
            ge=2,
            le=256
        ),
        scale: Optional[float] = Input(
            description="Scale factor (0.1-1.0). Leave empty to keep original size.",
            default=None,
            ge=0.1,
            le=1.0
        ),
        resize_width: Optional[int] = Input(
            description="Resize to this width in pixels (maintains aspect ratio). Overrides scale.",
            default=None,
            ge=1
        ),
        resize_height: Optional[int] = Input(
            description="Resize to this height in pixels (maintains aspect ratio). Overrides scale.",
            default=None,
            ge=1
        ),
        unoptimize: bool = Input(
            description="Unoptimize before compressing (useful for already-optimized GIFs)",
            default=False
        ),
    ) -> Path:
        """Compress a GIF file with minimal quality loss"""
        
        print("=" * 60)
        print("GIF COMPRESSION STARTING")
        print("=" * 60)
        
        # Get input file info
        input_size = os.path.getsize(gif)
        print(f"\n📊 Input file: {os.path.basename(gif)}")
        print(f"📦 Input size: {self._format_size(input_size)}")
        
        # Get GIF info
        gif_info = self._get_gif_info(gif)
        if gif_info:
            print(f"🎬 Frames: {gif_info['frames']}")
            print(f"📐 Dimensions: {gif_info['width']}x{gif_info['height']}")
            print(f"🎨 Colors: {gif_info['colors']}")
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "compressed.gif")
            
            # Build gifsicle command
            cmd = ["gifsicle"]
            
            # Optimization level
            if optimization_level == 1:
                cmd.append("-O1")
            elif optimization_level == 2:
                cmd.append("-O2")
            else:  # optimization_level == 3
                cmd.append("-O3")
            
            print(f"\n⚙️  Optimization level: {optimization_level}")
            
            # Unoptimize if requested
            if unoptimize:
                cmd.append("--unoptimize")
                print("🔄 Unoptimizing before compression")
            
            # Lossy compression
            if lossy_compression is not None:
                cmd.extend(["--lossy=" + str(lossy_compression)])
                print(f"💥 Lossy compression: {lossy_compression}")
            else:
                print("✨ Lossless compression")
            
            # Color reduction
            if colors is not None:
                cmd.extend(["--colors", str(colors)])
                print(f"🎨 Reducing to {colors} colors")
            
            # Resize options
            if resize_width is not None:
                cmd.extend(["--resize-width", str(resize_width)])
                print(f"📏 Resizing to width: {resize_width}px")
            elif resize_height is not None:
                cmd.extend(["--resize-height", str(resize_height)])
                print(f"📏 Resizing to height: {resize_height}px")
            elif scale is not None:
                cmd.extend(["--scale", str(scale)])
                print(f"📏 Scaling by: {scale}x")
            
            # Input and output
            cmd.extend([str(gif), "-o", output_path])
            
            # Show full command
            print(f"\n🔧 Command: {' '.join(cmd)}")
            print("\n" + "=" * 60)
            print("PROCESSING...")
            print("=" * 60 + "\n")
            
            # Run compression with progress output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    print(f"  {line.strip()}")
            
            process.wait()
            
            if process.returncode != 0:
                raise RuntimeError(f"Gifsicle failed with return code {process.returncode}")
            
            # Get output file info
            output_size = os.path.getsize(output_path)
            reduction = ((input_size - output_size) / input_size) * 100
            
            print("\n" + "=" * 60)
            print("COMPRESSION COMPLETE")
            print("=" * 60)
            print(f"\n📦 Output size: {self._format_size(output_size)}")
            print(f"💾 Size reduction: {reduction:.1f}%")
            print(f"📉 Compression ratio: {input_size / output_size:.2f}x")
            
            # Get output GIF info
            output_info = self._get_gif_info(output_path)
            if output_info:
                print(f"🎬 Output frames: {output_info['frames']}")
                print(f"📐 Output dimensions: {output_info['width']}x{output_info['height']}")
                print(f"🎨 Output colors: {output_info['colors']}")
            
            print("\n✅ Success!")
            print("=" * 60 + "\n")
            
            # Copy to output location
            final_output = Path(tempfile.mktemp(suffix=".gif"))
            shutil.copy(output_path, final_output)
            
            return final_output
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes as human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _get_gif_info(self, gif_path: Path) -> Optional[dict]:
        """Get information about the GIF file"""
        try:
            result = subprocess.run(
                ["gifsicle", "--info", str(gif_path)],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the output
            info = {}
            lines = result.stdout.strip().split('\n')
            
            # First line usually has basic info
            if lines:
                first_line = lines[0]
                # Try to extract dimensions
                if 'x' in first_line:
                    parts = first_line.split()
                    for i, part in enumerate(parts):
                        if 'x' in part and i > 0:
                            dims = part.strip('[]()').split('x')
                            if len(dims) == 2:
                                try:
                                    info['width'] = int(dims[0])
                                    info['height'] = int(dims[1])
                                except ValueError:
                                    pass
            
            # Count frames
            frame_count = result.stdout.count('+ image #')
            info['frames'] = max(1, frame_count)
            
            # Try to find color info
            for line in lines:
                if 'colors' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'color' in part.lower() and i > 0:
                            try:
                                info['colors'] = int(parts[i-1])
                            except ValueError:
                                pass
            
            return info if info else None
        except Exception as e:
            print(f"Warning: Could not get GIF info: {e}")
            return None