
import sys
import cv2 as cv
from geometry import Point
from transformer import FrameTransformer, DisplayContext
from video_player import VideoPlayer

class WriteInFrame(FrameTransformer):
    def __init__(self, text, position, color=(0,0,0)):
        super().__init__()
        self.text = text
        self.position = position
        self.color = color
        
    def apply(self, frame, context):
        font = cv.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        thickness = 2
        cv.putText(frame, self.text, self.position.tuple(), font, fontScale, self.color, thickness, cv.LINE_AA)
        return frame

class SaveRectangle(FrameTransformer):
    def __init__(self, filename, haut_droite: Point, bas_gauche: Point):
        super().__init__()
        self.filename = filename
        self.haut_gauche = haut_droite
        self.bas_droit = bas_gauche
        
    def apply(self, frame, context):  
        x_min=self.haut_gauche.x
        y_min=self.haut_gauche.y
        x_max=self.bas_droit.x
        y_max=self.bas_droit.y
        cv.imwrite(self.filename, frame[y_min:y_max, x_min:x_max])
        return frame
    
class DrawRectangle(FrameTransformer):
    def __init__(self, haut_droite: Point, bas_gauche: Point, color=(200, 0, 0)):
        super().__init__()
        self.haut_droite = haut_droite
        self.bas_gauche = bas_gauche
        self.color = color
        
    def apply(self, frame, context):
        cv.rectangle(frame, self.haut_droite.tuple(), self.bas_gauche.tuple(), self.color, 3)
        return frame

import time
class DrawRectangleFromInput(DrawRectangle):
    def __init__(self, input_filename):
        self.input_filename = input_filename
        self.set_rectangle_values()
        super().__init__(self.haut_droite, self.bas_gauche)
        
    def set_rectangle_values(self):        
        with open(self.input_filename, 'r') as file:
            content = file.readlines()
            self.haut_droite = Point(int(content[0]), int(content[1]))
            self.bas_gauche = Point(int(content[2]), int(content[3]))
            
    def apply(self, frame, context=None):        
        while True:
            self.set_rectangle_values()
            cv.imshow('frame', super().apply(frame.copy(), context))
            time.sleep(0.5)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
                
            
        return super().apply(frame, context)

class FrameByFrame(FrameTransformer):
    def apply(self, frame, context=None):        
        cv.waitKey(0)
        return frame
    


class SelectZone(FrameTransformer):
    def __init__(self,filename, pattern_haut_droit=Point(0, 0),pattern_bas_gauche=Point(0, 0)):
        super().__init__()
        self.filename = filename
        self.pattern_haut_droit = pattern_haut_droit
        self.pattern_bas_gauche = pattern_bas_gauche
        self.button_down = False

    def drawfunction(self, event,x,y,flags,param):
        if event == cv.EVENT_LBUTTONDBLCLK:
            print(f"Double Click {x}, {y}")
            
        if event == cv.EVENT_RBUTTONDOWN:
            print(f"Right click {x}, {y}")
            
        if event == cv.EVENT_LBUTTONDOWN:
            print(f"Left click down {x}, {y}")
            self.pattern_haut_droit = Point(x, y)
            self.button_down = True
            
        if event == cv.EVENT_LBUTTONUP:
            print(f"Left click up {x}, {y}")
            self.pattern_bas_gauche = Point(x, y)
            self.button_down = False
            
            self.frame_to_draw = self.current_frame.copy()
            DrawRectangle(self.pattern_haut_droit, self.pattern_bas_gauche,  (200, 200, 0)).apply(self.frame_to_draw, self.current_context),            
            SaveRectangle(self.filename, self.pattern_haut_droit, self.pattern_bas_gauche).apply(self.current_frame, None)
            cv.imshow('frame', self.frame_to_draw)
        
        if event == cv.EVENT_MOUSEMOVE:
            if self.button_down:
                print(f"Mouse move {x}, {y}")
                self.pattern_bas_gauche = Point(x, y)
                
                self.frame_to_draw = self.current_frame.copy()
                DrawRectangle(self.pattern_haut_droit, self.pattern_bas_gauche,  (200, 200, 0)).apply(self.frame_to_draw, self.current_context),            
                
                cv.imshow('frame', self.frame_to_draw)


    def apply(self, frame, context=None):      
        print(self.pattern_bas_gauche)  

        self.current_frame = frame
        self.current_context = context
        
        self.frame_to_draw = self.current_frame.copy()
        DrawRectangle(self.pattern_haut_droit, self.pattern_bas_gauche,  (200, 200, 0)).apply(self.frame_to_draw, context),
        
        cv.setMouseCallback('frame',self.drawfunction)

        return self.frame_to_draw
    

class OneFrame(FrameTransformer):
    def apply(self, frame, context=None):
        cv.imshow('frame', frame)
        cv.waitKey(0)
        return frame

if __name__ == "__main__":
    args = sys.argv
    filename = args[1]
        
    # pattern_haut_droit = Point(440, 157)
    # pattern_bas_gauche = Point(620, 301)
    # pattern_color = (200, 0, 0)
    
    # basket_into_haut_droit = Point(85,25)
    # basket_into_bas_gauche = Point(165,130)

    pattern_haut_droit = Point(1056, 157)
    pattern_bas_gauche = Point(1229, 301)
    pattern_color = (200, 0, 0)
    
    basket_into_haut_droit = Point(5,30)
    basket_into_bas_gauche = Point(115,115)
    
    basket_haut_droit = Point(pattern_haut_droit.x+basket_into_haut_droit.x, 
                              pattern_haut_droit.y+basket_into_haut_droit.y)
    basket_bas_gauche = Point(pattern_haut_droit.x+basket_into_bas_gauche.x, 
                              pattern_haut_droit.y+basket_into_bas_gauche.y)
    basket_color = (0, 200, 0)
    
    search_area_haut_droit = Point(0, 80)
    search_area_bas_gauche = Point(5000, 370)
    search_area_color = (0, 0, 200)
    
    area_in_video = [
                        DrawRectangle(pattern_haut_droit, pattern_bas_gauche, pattern_color),
                        WriteInFrame("Pattern", Point(pattern_haut_droit.x, pattern_haut_droit.y-10), pattern_color),
                        
                        DrawRectangle(basket_haut_droit, basket_bas_gauche, basket_color),
                        WriteInFrame("Basket", Point(basket_haut_droit.x, basket_haut_droit.y-10), basket_color),
                        
                        DrawRectangle(search_area_haut_droit, search_area_bas_gauche, search_area_color),
                        WriteInFrame("Search zone", Point(search_area_haut_droit.x, search_area_haut_droit.y-10), search_area_color),
                        
                        DisplayContext(),
                        SelectZone("tmp/pattern.jpg", pattern_haut_droit, pattern_bas_gauche) # Le select zone fait l'enregistrement de l'image
                        # SaveRectangle("tmp/pattern.jpg", select_zone.pattern_haut_droit, select_zone.pattern_bas_gauche),
                        # FrameByFrame(),
                    ] 
    
    area_in_image = [
        DrawRectangleFromInput("tmp/basket.txt"),
    ]
    
    # First choose frame with area_in_video => file pattern.jpg
    # Second set zone with area_in_image 
    VideoPlayer().play(filename, 
                    area_in_video,
                    # area_in_image,
                    show_video=True,
                    start_at_frame=615,
                    # start_at_frame=1771,
                    # end_at_frame=1950
                )