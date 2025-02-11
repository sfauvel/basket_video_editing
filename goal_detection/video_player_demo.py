

import cv2 as cv
from transformer import FrameTransformer, RealTime, Resize
from video_player import VideoPlayer

def demo_without_transformer(filename):
   """Call without transformer"""
   VideoPlayer().play(filename)

def demo_lambda(filename):
   """Call with a lambda"""
   VideoPlayer().play(filename, lambda frame: frame)

def demo_function(filename):
   """Call with a function"""
   def to_gray(frame):
      return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
       
   VideoPlayer().play(filename, to_gray)

def demo_single_frame_transformer(filename):
   """Call with a transformer"""
   VideoPlayer().play(filename, RealTime(30)) 
   
def demo_frame_transformer_array(filename):
   """Call with an array of transformer"""
   VideoPlayer().play(filename, [
      RealTime(30),
      Resize((700, 300))
   ])
   
class TransformerWithContext(FrameTransformer):
   def apply(self, frame, context=None):
      font = cv.FONT_HERSHEY_SIMPLEX
      bottom_left = (200, 40)
      fontScale = 1
      color = (255, 255, 0)
      thickness = 2
      text = 'Frame: ??? Time: ???' if context is None else f'Frame: {context.frame_number} Time: {context.seconds:.2f}'
      cv.putText(frame, text, bottom_left, font, fontScale, color, thickness, cv.LINE_AA)
  
      return super().apply(frame)
   
def demo_context(filename):
   """Call with a transformer"""
   VideoPlayer().play(filename, TransformerWithContext()) 

# Some examples of how to use the VideoPlayer class
if __name__ == "__main__":
   import sys
   args = sys.argv
   filename = args[1]
    
   demo_without_transformer(filename)
   demo_lambda(filename)
   demo_function(filename)
   demo_single_frame_transformer(filename)
   demo_frame_transformer_array(filename)
   demo_context(filename)