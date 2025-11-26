import os
import uuid
import asyncio
import gc
from app.services.pdf_processor import PDFProcessor
from app.services.script_generator import ScriptGenerator
from app.services.storyboard_generator import StoryboardGenerator
from app.services.scene_composer import SceneComposer
from app.services.video_renderer import VideoRenderer
from app.services.storage import StorageManager

class ProjectOrchestrator:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.script_generator = ScriptGenerator()
        self.storyboard_generator = StoryboardGenerator()
        self.scene_composer = SceneComposer()
        self.video_renderer = VideoRenderer()
        self.storage = StorageManager()

    async def process_project(self, pdf_path: str, project_id: str, status_callback=None):
        """
        Full pipeline: PDF -> Script -> Storyboard -> Scenes -> Video
        """
        async def update_status(step):
            print(f"[{project_id}] {step}...")
            if status_callback:
                await status_callback(step)

        await update_status("starting")
        
        try:
            # 0. Data Collection: Save Source PDF
            print(f"[{project_id}] Collecting source data...")
            source_dest = f"projects/{project_id}/source.pdf"
            self.storage.upload_file(pdf_path, source_dest)

            import time
            pipeline_start = time.time()

            # 1. Extract Text
            await update_status("extracting")
            t0 = time.time()
            pdf_data = self.pdf_processor.process_pdf(pdf_path)
            full_text = pdf_data["full_text"]
            print(f"[{project_id}] Extraction took {time.time() - t0:.2f}s")
            
            # 2. Generate Script
            await update_status("scripting")
            t0 = time.time()
            script = self.script_generator.generate_script(full_text)
            print(f"[{project_id}] Script generation took {time.time() - t0:.2f}s")
            
            # 3. Generate Storyboard
            await update_status("storyboard")
            t0 = time.time()
            storyboard = self.storyboard_generator.generate_storyboard(script)
            print(f"[{project_id}] Storyboard generation took {time.time() - t0:.2f}s")
            
            # 4. Build Scenes (Sketches + Audio)
            await update_status("scenes")
            t0 = time.time()
            scenes = await self.scene_composer.build_scenes(storyboard)
            print(f"[{project_id}] Scene composition took {time.time() - t0:.2f}s")
            gc.collect() # Free memory after image/audio generation
            
            # 5. Render Scenes & Final Video
            await update_status("rendering")
            t0 = time.time()
            
            loop = asyncio.get_running_loop()
            
            # Render scenes in parallel (Max 5 minutes)
            # High Performance Mode: Concurrency 8
            sem = asyncio.Semaphore(8)

            async def render_with_limit(scene):
                async with sem:
                    return await loop.run_in_executor(None, self.video_renderer.render_scene, scene)

            render_tasks = [render_with_limit(s) for s in scenes]
            scene_paths = await asyncio.gather(*render_tasks)
            print(f"[{project_id}] Scene rendering took {time.time() - t0:.2f}s")
            
            t1 = time.time()
            gc.collect() # Free memory after rendering clips
                
            final_video_path = self.video_renderer.concat_scenes(scene_paths)
            print(f"[{project_id}] Concatenation took {time.time() - t1:.2f}s")
            
            # 6. Upload Final Video
            await update_status("uploading")
            dest = f"projects/{project_id}/final.mp4"
            final_url = self.storage.upload_file(final_video_path, dest)
            
            # Cleanup
            os.remove(final_video_path)
            for p in scene_paths:
                if os.path.exists(p):
                    os.remove(p)
                    
            total_time = time.time() - pipeline_start
            print(f"[{project_id}] DONE! Video URL: {final_url}")
            print(f"[{project_id}] Total Pipeline Time: {total_time:.2f}s")
            return final_url

        except Exception as e:
            print(f"[{project_id}] CRITICAL PIPELINE ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                self.storage.save_json(status_path, {
                    "id": project_id,
                    "status": "failed", 
                    "error": str(e)
                })
            except Exception as write_err:
                print(f"[{project_id}] Failed to write error status: {write_err}")
            
            raise e
