import os
import uuid
import asyncio
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

            # 1. Extract Text
            await update_status("extracting")
            pdf_data = self.pdf_processor.process_pdf(pdf_path)
            full_text = pdf_data["full_text"]
            
            # 2. Generate Script
            await update_status("scripting")
            script = self.script_generator.generate_script(full_text)
            
            # 3. Generate Storyboard
            await update_status("storyboard")
            storyboard = self.storyboard_generator.generate_storyboard(script)
            
            # 4. Build Scenes (Sketches + Audio)
            await update_status("scenes")
            scenes = await self.scene_composer.build_scenes(storyboard)
            
            # 5. Render Scenes & Final Video
            await update_status("rendering")
            
            loop = asyncio.get_running_loop()
            
            # Render scenes in parallel
            render_tasks = []
            for scene in scenes:
                task = loop.run_in_executor(None, self.video_renderer.render_scene, scene)
                render_tasks.append(task)
                
            scene_paths = await asyncio.gather(*render_tasks)
                
            final_video_path = self.video_renderer.concat_scenes(scene_paths)
            
            # 6. Upload Final Video
            await update_status("uploading")
            dest = f"projects/{project_id}/final.mp4"
            final_url = self.storage.upload_file(final_video_path, dest)
            
            # Cleanup
            os.remove(final_video_path)
            for p in scene_paths:
                if os.path.exists(p):
                    os.remove(p)
                    
            print(f"[{project_id}] DONE! Video URL: {final_url}")
            return final_url

        except Exception as e:
            print(f"[{project_id}] Pipeline FAILED: {e}")
            raise e
