from domain.entities import Shot, AssetMode, ShotEstado
import traceback

class ProcessShot:
    def __init__(self, fs, prompt_service, image_client, video_client, logger, assets_repo):
        self.fs = fs
        self.prompt_service = prompt_service
        self.image_client = image_client
        self.video_client = video_client
        self.logger = logger
        self.assets_repo = assets_repo

    def execute(self, shot: Shot) -> Shot:
        try:
            self.logger.info(f"Starting processing for shot {shot.video_id}/{shot.block_id}/{shot.shot_id}")
            
            # State transition: PENDIENTE -> EN_PROCESO
            shot.estado = ShotEstado.EN_PROCESO
            
            # Asset Resolution
            asset_obj = None
            ref_image_url = None
            
            if shot.asset_id:
                self.logger.info(f"Resolving asset: {shot.asset_id}")
                asset_obj = self.assets_repo.get_asset(shot.asset_id)
                
                if not asset_obj:
                    raise Exception(f"Asset ID not found in catalog: {shot.asset_id}")
                
                resolved_path = self.assets_repo.resolve_file_path(asset_obj.file_name)
                if not resolved_path:
                    raise Exception(f"Asset physical file not found: {asset_obj.file_name}")
                
                # Update Shot metadata
                shot.asset_resolved_file_name = asset_obj.file_name
                shot.asset_resolved_path = str(resolved_path)
                
                # Check consistency
                if shot.mv_context != asset_obj.mv_context_default:
                    shot.asset_mv_context_mismatch = True
                    self.logger.warning(f"Context mismatch! Shot: {shot.mv_context} vs Asset: {asset_obj.mv_context_default}")
                
                # Get public URL for reference
                ref_image_url = self.fs.get_public_url(str(resolved_path))
                self.logger.info(f"Using reference image: {ref_image_url} (image_input)")
                self.logger.info(f"Asset resolved. Ref URL: {ref_image_url}")
            else:
                self.logger.info("No reference image provided. Generating from prompt only.")
                self.logger.warning(f"No asset_id provided. Image will be generated without reference asset.")

            
            # 1. Generación de prompts (if not already provided)
            # Re-generate prompt if asset is present to ensure anchor is included,
            # or if prompt is missing.
            # NOTE: If prompt is already present (e.g. from previous run), we might want to respect it.
            # But the goal says "inject anchor". Let's force update ONLY if asset is present OR prompt missing.
            # Safest is: "if not prompt OR (asset and prompt doesn't contain anchor logic?)"
            # For simplicity, if asset is present, we assume we want to enrich the prompt.
            # But let's stick to simple logic: Only if missing for now, OR if specific flag provided?
            # Implementation plan said: "Update generate_image_prompt... If asset provided... Append".
            # The user might have manually edited the prompt. Overwriting existing prompt is risky.
            # Let's ONLY generate if missing.
            
            if not shot.prompt_imagen:
                self.logger.info("Generating image prompt...")
                shot.prompt_imagen = self.prompt_service.generate_image_prompt(shot, asset=asset_obj)
            
            if not shot.prompt_video:
                self.logger.info("Generating video prompt...")
                shot.prompt_video = self.prompt_service.generate_video_prompt(shot)

            # 2. Generar imagen (always required)
            self.logger.info(f"Generating image with prompt: {shot.prompt_imagen[:50]}...")
            
            # Use ref_image_url if resolved
            img_url = self.image_client.generate(shot.prompt_imagen, ref_image_url=ref_image_url)
            
            shot.image_path = self.fs.save_image(shot, img_url)
            self.logger.info(f"Image saved to {shot.image_path}")

            # 3. Conditional video generation based on asset_mode
            if shot.asset_mode == AssetMode.STILL_ONLY:
                self.logger.info("Asset mode is STILL_ONLY, skipping video generation")
            elif shot.asset_mode == AssetMode.IMAGE_1F_VIDEO:
                self.logger.info(f"Generating video with prompt: {shot.prompt_video[:50]}...")
                vid_url = self.video_client.generate(shot.image_path, shot.prompt_video)
                shot.video_path = self.fs.save_video(shot, vid_url)
                self.logger.info(f"Video saved to {shot.video_path}")
            elif shot.asset_mode == AssetMode.IMAGE_2F_VIDEO:
                # Future implementation - for now, treat as IMAGE_1F_VIDEO
                self.logger.warning("IMAGE_2F_VIDEO not fully implemented, using IMAGE_1F_VIDEO logic")
                vid_url = self.video_client.generate(shot.image_path, shot.prompt_video)
                shot.video_path = self.fs.save_video(shot, vid_url)
                self.logger.info(f"Video saved to {shot.video_path}")
            
            # State transition: EN_PROCESO -> COMPLETADO
            shot.estado = ShotEstado.COMPLETADO
            
            # 4. Save metadata
            self.fs.save_metadata(shot)
            
        except Exception as e:
            shot.estado = ShotEstado.ERROR
            shot.error_message = str(e)
            self.logger.error(f"Error processing shot: {e}")
            self.logger.error(traceback.format_exc())
            # Save metadata even on error for debugging
            try:
                self.fs.save_metadata(shot)
            except:
                pass 
        
        return shot
