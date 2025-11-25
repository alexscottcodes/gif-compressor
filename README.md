# GIF Compressor 🎬

A high-quality GIF compression model for Replicate using gifsicle. Fast CPU-based compression with minimal quality loss.

## Features

- **Fast CPU compression** - No GPU needed, runs quickly on any machine
- **Smart defaults** - Optimized for quality with level 3 optimization
- **Lossless or lossy** - Choose between perfect quality or smaller files
- **Advanced options** - Color reduction, resizing, and more
- **Detailed logging** - Progress bars and compression statistics
- **Production-ready** - Proper error handling and Cog integration

### Basic Options

- **`optimization_level`** (1-3, default: 3)
  - Level 1: Fast, basic optimization
  - Level 2: Balanced optimization
  - Level 3: Maximum optimization (recommended)

- **`lossy_compression`** (20-200, optional)
  - Leave empty for lossless compression
  - 80 = good balance of quality and size
  - 50 = high quality, moderate compression
  - 100-150 = lower quality, better compression
  - Lower numbers = better quality

### Advanced Options

- **`colors`** (2-256, optional)
  - Reduce color palette to this many colors
  - Useful for further size reduction
  - 128 or 64 work well for most GIFs

- **`scale`** (0.1-1.0, optional)
  - Scale the GIF by this factor
  - 0.5 = half size, 0.75 = 75% size

- **`resize_width`** / **`resize_height`** (optional)
  - Resize to specific dimensions in pixels
  - Maintains aspect ratio
  - Overrides scale option

- **`unoptimize`** (boolean, default: false)
  - Unoptimize before compressing
  - Useful for already-optimized GIFs that need reprocessing

## Example Usage

### Simple compression (lossless)
```bash
cog predict -i gif=@input.gif
```

### Balanced quality and size
```bash
cog predict -i gif=@input.gif -i lossy_compression=80 -i colors=128
```

### Maximum compression
```bash
cog predict -i gif=@input.gif \
  -i lossy_compression=150 \
  -i colors=64 \
  -i scale=0.75
```

### Resize to specific width
```bash
cog predict -i gif=@input.gif \
  -i resize_width=500 \
  -i lossy_compression=80
```

## Using with Python

```python
import replicate

output = replicate.run(
    "unityaisolutions/gif-compressor",
    input={
        "gif": open("input.gif", "rb"),
        "optimization_level": 3,
        "lossy_compression": 80,
        "colors": 128
    }
)

# Save the compressed GIF
with open("output.gif", "wb") as f:
    f.write(output.read())
```

## Output Logs

The model provides detailed logging including:

- Input/output file sizes
- Compression ratio and reduction percentage
- GIF dimensions, frames, and colors
- Processing status and progress

Example output:
```
============================================================
GIF COMPRESSION STARTING
============================================================

📊 Input file: animation.gif
📦 Input size: 2.45 MB
🎬 Frames: 60
📐 Dimensions: 500x500
🎨 Colors: 256

⚙️  Optimization level: 3
💥 Lossy compression: 80
🎨 Reducing to 128 colors

============================================================
PROCESSING...
============================================================

gifsicle: optimizing...

============================================================
COMPRESSION COMPLETE
============================================================

📦 Output size: 487.32 KB
💾 Size reduction: 80.1%
📉 Compression ratio: 5.03x
🎬 Output frames: 60
📐 Output dimensions: 500x500
🎨 Output colors: 128

✅ Success!
============================================================
```

## Tips for Best Results

1. **Start with defaults** - The default settings work well for most GIFs
2. **Use lossy_compression=80** - Great balance for most use cases
3. **Reduce colors gradually** - Try 128 first, then 64 if needed
4. **Combine techniques** - lossy + color reduction = best compression
5. **Test different values** - Every GIF is different!

## Technical Details

- **Engine**: gifsicle (industry-standard GIF optimizer)
- **Speed**: Extremely fast on CPU (no GPU needed)
- **Quality**: Minimal perceptible quality loss with default settings
- **Format**: Input and output both GIF

## License

This Cog model wrapper is open source. Gifsicle is GPL-licensed.