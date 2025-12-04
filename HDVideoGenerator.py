#!/usr/bin/env python3
"""
HD Video Generator for Testing
Creates sample MJPEG video files with configurable resolutions for testing HD streaming.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import io

class HDVideoGenerator:
    """Generate HD test video files in MJPEG format."""
    
    # Predefined resolutions
    RESOLUTIONS = {
        'sd': (352, 288),      # Standard Definition
        '480p': (720, 480),    # 480p
        '720p': (1280, 720),   # HD 720p
        '1080p': (1920, 1080), # Full HD 1080p
    }
    
    def __init__(self, output_file='test_video_hd.Mjpeg'):
        self.output_file = output_file
        
    def generate_frame(self, frame_number, width, height, quality=85):
        """Generate a single test frame with frame number overlay."""
        # Create image with gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for y in range(height):
            color_value = int((y / height) * 255)
            color = (color_value // 3, color_value // 2, color_value)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Draw frame number and resolution
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", width // 20)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Add text overlay
        text = f"Frame: {frame_number}\n{width}x{height}"
        
        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with shadow for better visibility
        draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Draw decorative elements
        # Corner markers
        marker_size = min(width, height) // 10
        draw.rectangle([10, 10, 10+marker_size, 10+marker_size], outline=(255, 0, 0), width=5)
        draw.rectangle([width-10-marker_size, 10, width-10, 10+marker_size], outline=(0, 255, 0), width=5)
        draw.rectangle([10, height-10-marker_size, 10+marker_size, height-10], outline=(0, 0, 255), width=5)
        draw.rectangle([width-10-marker_size, height-10-marker_size, width-10, height-10], outline=(255, 255, 0), width=5)
        
        # Convert to JPEG bytes
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality)
        return buffer.getvalue()
    
    def generate_video(self, resolution='720p', num_frames=300, quality=85):
        """
        Generate a test video file.
        
        Args:
            resolution: One of 'sd', '480p', '720p', '1080p' or tuple (width, height)
            num_frames: Number of frames to generate
            quality: JPEG quality (1-100, higher = better quality = larger size)
        """
        # Get resolution dimensions
        if isinstance(resolution, str):
            if resolution not in self.RESOLUTIONS:
                print(f"Unknown resolution: {resolution}")
                print(f"Available resolutions: {list(self.RESOLUTIONS.keys())}")
                return False
            width, height = self.RESOLUTIONS[resolution]
        else:
            width, height = resolution
        
        print(f"Generating HD test video: {self.output_file}")
        print(f"Resolution: {width}x{height}")
        print(f"Frames: {num_frames}")
        print(f"Quality: {quality}")
        print("-" * 50)
        
        total_size = 0
        
        with open(self.output_file, 'wb') as f:
            for frame_num in range(1, num_frames + 1):
                # Generate frame
                frame_data = self.generate_frame(frame_num, width, height, quality)
                frame_size = len(frame_data)
                
                # Write frame length (5 bytes, decimal string)
                frame_length_str = str(frame_size).zfill(5)
                f.write(frame_length_str.encode('ascii'))
                
                # Write frame data
                f.write(frame_data)
                
                total_size += frame_size + 5
                
                # Progress update
                if frame_num % 30 == 0 or frame_num == num_frames:
                    avg_frame_size = frame_size / 1024  # KB
                    print(f"Frame {frame_num}/{num_frames} | "
                          f"Size: {avg_frame_size:.1f} KB | "
                          f"Total: {total_size/1024/1024:.2f} MB")
        
        # Statistics
        avg_frame_size = total_size / num_frames
        estimated_bitrate = (avg_frame_size * 30 * 8) / 1024  # Kbps at 30 FPS
        
        print("-" * 50)
        print(f"Video generation complete!")
        print(f"Output file: {self.output_file}")
        print(f"Total size: {total_size/1024/1024:.2f} MB")
        print(f"Average frame size: {avg_frame_size/1024:.2f} KB")
        print(f"Estimated bitrate @ 30fps: {estimated_bitrate:.0f} Kbps")
        print(f"Fragmentation needed: {'YES' if avg_frame_size > 1400 else 'NO'}")
        
        if avg_frame_size > 1400:
            fragments_per_frame = (avg_frame_size / 1384) 
            print(f"Estimated fragments per frame: {fragments_per_frame:.0f}")
        
        return True
    
    def generate_test_suite(self):
        """Generate a full test suite with multiple resolutions."""
        test_configs = [
            ('sd', 'test_video_sd.Mjpeg', 200, 75),
            ('480p', 'test_video_480p.Mjpeg', 200, 80),
            ('720p', 'test_video_720p.Mjpeg', 200, 85),
            ('1080p', 'test_video_1080p.Mjpeg', 150, 85),
        ]
        
        print("=" * 60)
        print("HD VIDEO TEST SUITE GENERATOR")
        print("=" * 60)
        print()
        
        for resolution, filename, frames, quality in test_configs:
            self.output_file = filename
            self.generate_video(resolution, frames, quality)
            print()
        
        print("=" * 60)
        print("Test suite generation complete!")
        print("=" * 60)


def main():
    """Main function with command-line interface."""
    if len(sys.argv) < 2:
        print("HD Video Generator for Testing")
        print()
        print("Usage:")
        print(f"  {sys.argv[0]} <resolution> [output_file] [num_frames] [quality]")
        print()
        print("Resolutions: sd, 480p, 720p, 1080p")
        print()
        print("Examples:")
        print(f"  {sys.argv[0]} 720p                    # Generate 720p video with defaults")
        print(f"  {sys.argv[0]} 1080p hd_test.Mjpeg     # Generate 1080p with custom name")
        print(f"  {sys.argv[0]} 720p test.Mjpeg 500 90  # 500 frames, quality 90")
        print(f"  {sys.argv[0]} suite                   # Generate full test suite")
        print()
        return
    
    resolution = sys.argv[1]
    
    # Generate test suite
    if resolution == 'suite':
        generator = HDVideoGenerator()
        generator.generate_test_suite()
        return
    
    # Parse arguments
    output_file = sys.argv[2] if len(sys.argv) > 2 else f'test_video_{resolution}.Mjpeg'
    num_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 85
    
    # Generate video
    generator = HDVideoGenerator(output_file)
    generator.generate_video(resolution, num_frames, quality)


if __name__ == "__main__":
    main()
