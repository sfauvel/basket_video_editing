
import cv2 as cv

class FrameTransformer:
    def apply(self, frame, context=None):
        return frame
    
class BufferedFrameTransformer(FrameTransformer):
    def __init__(self, buffer_size = 10):
        self.clear_buffer()
        self.buffer_size=buffer_size
    
    def clear_buffer(self):
        self.buffer=[]
        self.frames_buffer=[]
    
    def apply(self, frame, context=None):      
        if len(self.buffer) >= self.buffer_size:
            self.buffer=self.buffer[1:]            
            self.frames_buffer=self.frames_buffer[1:]            
        self.buffer.append(frame)     
        self.frames_buffer.append((frame, context))
        return frame


class Resize(FrameTransformer):
    def __init__(self, new_size):
        self.new_size = new_size    
        
    def apply(self, frame, context=None):
        return cv.resize(frame, self.new_size)  
       

import time
class RealTime(FrameTransformer):    
    """Display frames with a delay between each frame according to fps"""
    def __init__(self, fps):
        self.fps = fps
        self.frame_counter = 0
        self.last_time = None
    
    def apply(self, frame, context=None):
        self.frame_counter += 1
        
        if self.last_time is not None:
            elapsed_time = time.time() - self.last_time
            should_be = 1 / self.fps
            delay_before_next_frame = max(0, should_be - elapsed_time)
            time.sleep(delay_before_next_frame)
            
        self.last_time = time.time()
        return frame
    
class DisplayContext(FrameTransformer):
    def apply(self, frame, context=None):
        font = cv.FONT_HERSHEY_SIMPLEX
        bottom_left = (200, 40)
        fontScale = 1
        thickness = 2
        text = 'Frame: ??? Time: ???' if context is None else f'Frame: {context.frame_number} Time: {context.seconds:.2f}'
        cv.putText(frame, text, (bottom_left[0]+2, bottom_left[1]+2), font, fontScale, (0,0,0), thickness, cv.LINE_AA)
        cv.putText(frame, text, bottom_left, font, fontScale, (255,255,255), thickness, cv.LINE_AA)
    
    
        return super().apply(frame)