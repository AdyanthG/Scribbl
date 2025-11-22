import os
import uuid
import ffmpeg
from typing import List
from app.services.scene_model import Scene

class VideoRenderer:

    def __init__(self):
        self.output_width = 1280
        self.output_height = 720
        # Fallback font, might need to be adjusted based on deployment env
        self.font_path = "/System/Library/Fonts/Helvetica.ttc" if os.path.exists("/System/Library/Fonts/Helvetica.ttc") else "arial"

    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds."""
        try:
            probe = ffmpeg.probe(audio_path)
            return float(probe['format']['duration'])
        except Exception as e:
            print(f"Error probing audio: {e}")
            return 5.0

    def render_scene(self, scene: Scene) -> str:
        """
        Render a single scene video clip.
        Duration is determined by audio length if present, else scene.duration.
        """
        
        tmp_id = str(uuid.uuid4())
        output_path = f"/tmp/scene_{tmp_id}.mp4"

        # Determine duration
        duration = scene.duration
        if scene.audio_path and os.path.exists(scene.audio_path):
            audio_dur = self.get_audio_duration(scene.audio_path)
            # Add small buffer for pacing
            duration = max(duration, audio_dur + 0.5)

        # Input Image
        input_stream = ffmpeg.input(scene.sketch_path, loop=1, t=duration)
        
        # Motion Effect (Randomized Ken Burns)
        import random
        
        # Randomize zoom direction (in or out)
        zoom_direction = random.choice(["in", "out"])
        
        # Randomize pan direction (none, left, right, up, down)
        pan_direction = random.choice(["none", "left", "right", "up", "down"])
        
        # Base zoom expression
        if zoom_direction == "in":
            z_expr = "min(zoom+0.0015,1.5)"
        else:
            z_expr = "max(1.5-0.0015*on,1)"
            
        # Pan expressions (x and y coordinates)
        # Center by default
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
        
        if pan_direction == "left":
            x_expr = "x+1" # Move viewport right = pan left
        elif pan_direction == "right":
            x_expr = "x-1"
        elif pan_direction == "up":
            y_expr = "y+1"
        elif pan_direction == "down":
            y_expr = "y-1"

        video = input_stream.filter(
            'zoompan',
            z=z_expr,
            d=int(duration * 25), # 25 fps
            x=x_expr,
            y=y_expr,
            s=f'{self.output_width}x{self.output_height}'
        )

        # Text Overlay
        if scene.text:
            # Escape text for ffmpeg
            safe_text = scene.text.replace(":", "\:").replace("'", "")
            video = video.drawtext(
                text=safe_text,
                fontfile=self.font_path,
                fontsize=48,
                fontcolor='black',
                x='(w-text_w)/2',
                y='h-80', # Bottom centered
                box=1,
                boxcolor='white@0.8',
                boxborderw=10
            )

        # Audio
        audio = None
        if scene.audio_path and os.path.exists(scene.audio_path):
            audio = ffmpeg.input(scene.audio_path)
        else:
            # Silent audio track to ensure concatenation works
            audio = ffmpeg.input('anullsrc', f='lavfi', t=duration)

        # Output
        try:
            out = ffmpeg.output(
                video,
                audio,
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                r=25,
                preset='ultrafast',
                shortest=None
            )
            out.run(overwrite_output=True, quiet=True)
            return output_path
        except ffmpeg.Error as e:
            print(f"FFmpeg Error: {e.stderr.decode() if e.stderr else str(e)}")
            raise e

    def concat_scenes(self, scene_paths: List[str]) -> str:
        """Concatenate multiple scene .mp4 files into final video."""
        
        if not scene_paths:
            raise Exception("No scenes to concatenate")

        final_id = str(uuid.uuid4())
        output_path = f"/tmp/final_{final_id}.mp4"

        # Create file list for concat demuxer
        list_path = f"/tmp/list_{final_id}.txt"
        with open(list_path, "w") as f:
            for path in scene_paths:
                f.write(f"file '{path}'\n")

        try:
            (
                ffmpeg
                .input(list_path, format='concat', safe=0)
                .output(output_path, c='copy')
                .run(overwrite_output=True, quiet=True)
            )
            os.remove(list_path)
            return output_path
        except ffmpeg.Error as e:
            print(f"FFmpeg Concat Error: {e.stderr.decode() if e.stderr else str(e)}")
            raise e
