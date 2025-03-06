

import cv2 as cv
import time
from transformer import FrameTransformer

class VideoPlayer:
    class Context:
        def __init__(self, frame_number, seconds, show_video):
            self.frame_number = frame_number
            self.seconds = seconds
            self.show_video = show_video
            
    def _apply_transform(self, frame, transform, context):
        # TODO: Do we want to apply on a lambda ?
        
        # Si le transform est un array
        if isinstance(transform, list):
            for t in transform:
                frame = self._apply_transform(frame, t, context)
            return frame
        if isinstance(transform, FrameTransformer):
            return transform.apply(frame, context)
        else:
            return transform(frame)
        
    def log(self, message):
        print(message)
        
    def play(
        self,
        filename, 
        transform=lambda x: x,
        start_at_frame=0,
        end_at_frame=None,
        show_video=True,
        by_step=None
    ):
        videoCapture = cv.VideoCapture(filename)
        fps = videoCapture.get(cv.CAP_PROP_FPS)
        self.log(f"File: {filename}")
        self.log(f"FPS: {fps}")
        
        # Start at the given frame
        videoCapture.set(cv.CAP_PROP_POS_FRAMES, start_at_frame) 
        nb_frame=start_at_frame
            
        
        last_key = None
        while True:
            if end_at_frame is not None and nb_frame > end_at_frame:
                self.log(f"Last expected frame({end_at_frame}) reached. Stop video.")
                break
            
            nb_frame += 1
            ret, frame = videoCapture.read()
            if not ret:
                print("End of video.")
                break
            
            frame = self._apply_transform(frame, transform, VideoPlayer.Context(nb_frame, nb_frame/fps, show_video))
                    
            if show_video:
                cv.imshow('frame', frame)
                
            
            if last_key == ord('q'):
                break
            elif last_key == ord(' '):
                last_key = cv.waitKey(0)  & 0xFF
            else:
                last_key = cv.waitKey(1) & 0xFF
                
            if by_step:
                nb_frame += by_step
                videoCapture.set(cv.CAP_PROP_POS_FRAMES, nb_frame) 
            
        videoCapture.release()
        cv.destroyAllWindows()
