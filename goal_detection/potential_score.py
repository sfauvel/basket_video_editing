import cv2 as cv
import os
import numpy as np
from datetime import timedelta

from geometry import Area, Point
from transformer import FrameTransformer, BufferedFrameTransformer

def enlarge_shapes(self, frame):
    blur=15
    frame = self.threshold(frame)
    frame = cv.GaussianBlur(frame, (blur, blur), 0)
    frame = cv.dilate(frame, None, iterations=5)
    return frame

import time

class COLOR:
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)

class FastImageRecognition(BufferedFrameTransformer):
    """
    Bufferize frames and check on the last one if we detect the pattern.
    If we detect the pattern, we apply the transformation on all the buffered frames.
    """
    def __init__(self, transformer):
        super().__init__(buffer_size=20)
        self.transformer = transformer
        self.counter = 0
        self.last_computed = None

    def apply(self, frame, context=None):
        super().apply(frame, context)
        self.counter += 1

        if self.counter == self.buffer_size: # Buffer is full
            (best_area, _) = self.transformer.find_basket_area(self.transformer.blur(frame))
            if best_area:
                for (buffered_frame, context) in self.frames_buffer:
                    self.last_computed = self.transformer.apply(buffered_frame, context)
            else:
                self.last_computed = frame

            self.counter = 0
            self.clear_buffer()

        return frame if self.last_computed is None else self.last_computed.copy()

class CheckMove(FrameTransformer):
    def __init__(self):
        self.last_frame = None

    def apply(self, frame, context=None):
        last_frame = self.last_frame
        self.last_frame = frame

        if last_frame is None:
            return frame
        elif last_frame.shape != frame.shape:
            print("!!! Not same shape")
            return frame
        else:
            frame_diff = cv.absdiff(last_frame, frame)
            # frame_diff = cv.cvtColor(frame_diff, cv.COLOR_BGR2GRAY)
            frame_diff = cv.GaussianBlur(frame_diff, (15, 15), 0)
            frame_diff = cv.threshold(frame_diff, 25, 255, cv.THRESH_BINARY)[1]
            return frame_diff

class LookingForPattern():
    def __init__(self, image_pattern, y_start_search=100, y_end_search=400):
        self.frame_pattern_blur = image_pattern
        self.pattern_height = self.frame_pattern_blur.shape[0]
        self.pattern_width = self.frame_pattern_blur.shape[1]

        self.y_start_search = y_start_search
        self.y_end_search = y_end_search
        self.last_area = None

    def increase_area(self, area, margin):
        return Area(
                Point(
                    max(0,self.last_area.up_left.x-margin),
                    max(0,self.last_area.up_left.y-margin )
                ),
                Point(
                    self.last_area.bottom_right.x + margin,
                    self.last_area.bottom_right.y + margin
                ))
        
    def search_in_area(self, frame, search_area):
        frame_part = search_area.extract(frame)
        area = self.matching_in_frame_part(frame_part)
        if area:
            area = area.shift(search_area.up_left.x, search_area.up_left.y)
            
        self.last_area = area
            
        return area
        
    def best_matching_area(self, frame):

        margin = 20
        if self.last_area is not None:
            search_area = self.increase_area(self.last_area, margin)
            area = self.search_in_area(frame, search_area)
            if area:
                return area
            
        search_area = Area(Point(0, self.y_start_search), Point(frame.shape[1], self.y_end_search))
        return self.search_in_area(frame, search_area)
            
    def matching_in_frame_part(self, frame_part):

        res = cv.matchTemplate(frame_part, self.frame_pattern_blur, cv.TM_CCOEFF_NORMED)
        if res is None:
            return None

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        if max_val < 0.6:
            return None

        area = Area(Point(0,0), Point(self.pattern_width, self.pattern_height))
        area = area.shift(*max_loc)
        return area

def build_time_str(seconds):
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)

class SearchPattern(FrameTransformer):
    def __init__(self, image_patterns):
        self.y_start_search = 0
        self.y_end_search = 400
        self.patterns = [(self.blur(cv.imread(pattern)), basket_area) for (pattern, basket_area) in image_patterns]
        self.patterns_search = [(LookingForPattern(self.blur(cv.imread(pattern)), self.y_start_search, self.y_end_search), basket_area) for (pattern, basket_area) in image_patterns]
        self.min_y = 0
        self.max_y = 10000

    def apply(self, frame, context=None):
        for (pattern, _) in self.patterns:

            # pattern_search = LookingForPattern(pattern, self.y_start_search, frame.shape[1] if self.min_y is None else self.min_y + pattern.shape[0])
            # pattern_search = LookingForPattern(pattern, self.y_start_search, self.y_end_search)
            pattern_search = LookingForPattern(pattern, self.y_start_search, self.max_y)

            found_area = pattern_search.best_matching_area(self.blur(frame))
            if found_area is not None:
                self.draw_rectangle(frame, found_area)
                self.min_y = min(self.min_y, found_area.up_left.y)
                self.max_y = max(self.max_y, found_area.bottom_right.y)
                print(f"Frame: {context.frame_number} y - min: {self.min_y} max: {self.max_y}")

                break

        # for (pattern_search, _) in self.patterns_search:
        #     found_area = pattern_search.best_matching_area(self.blur(frame))
        #     if found_area is not None:
        #         self.draw_rectangle(frame, found_area)
        #         self.min_y = found_area.up_left.y if self.min_y is None else min(self.min_y, found_area.up_left.y)
        #         self.max_y = found_area.bottom_right.y if self.max_y is None else max(self.max_y, found_area.bottom_right.y)
        #         print(f"Frame: {context.frame_number} y - min: {self.min_y} max: {self.max_y}")
        #         break
        self.draw_rectangle(frame, Area(Point(0, self.min_y), Point(frame.shape[1], self.max_y)), color=(0, 0, 255))
        return frame

    def draw_rectangle(self, frame, area, color=(0, 255, 0)):
        if area is not None:
            cv.rectangle(frame, area.up_left.tuple(), area.bottom_right.tuple(), color, 2)

    def blur(self, frame):
        blur_value = 7
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.GaussianBlur(frame, (blur_value, blur_value), 0)
        return frame

class ExtractMatchingZone(FrameTransformer):
    def __init__(self, image_patterns):
        # !!! If pattern is outside this image, it will never be found.
        # The position could different between files.
        # If we increase the area, we increase the time.
        # If may do a pre-treatmeent to find values to use (search for the pattern at different moment in all the image)
        y_start_search = 50
        y_end_search = 400
        
        for (image, _) in image_patterns:
            if not os.path.isfile(image):
                raise ValueError(f"Pattern image file {image} does not exist")

        self.patterns_search = [(LookingForPattern(self.blur(cv.imread(pattern)), y_start_search, y_end_search), basket_area) for (pattern, basket_area) in image_patterns]

        self.check_move = CheckMove()

        self.consecutive_detection = 0
        self.consecutive_ballon = 0

    def blur(self, frame):
        blur_value = 7
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.GaussianBlur(frame, (blur_value, blur_value), 0)
        return frame

    def find_basket_area(self, frame):
        for (pattern_search, basket_area) in self.patterns_search:
            area = pattern_search.best_matching_area(frame)
            if area is not None:
                self.patterns_search.remove((pattern_search, basket_area))
                self.patterns_search.insert(0, (pattern_search, basket_area))

                # Restrict area to find basket panel which is always at the same height
                # WARNING: height seems to not be always the same probably because of the camera angle
                # pattern_search.y_start_search = area.up_left.y - 10
                # pattern_search.y_end_search =  area.bottom_right.y + 10
                # print(f"start y:{pattern_search.y_start_search}   end y:{pattern_search.y_end_search}")
                return (area, basket_area)
        return (None, None)

    def draw_rectangle(self, frame, area, color=(0, 255, 0), tickness=2):
        area and cv.rectangle(frame, area.up_left.tuple(), area.bottom_right.tuple(), color, tickness)
        
    def write(self, frame, text, bottom_left = (10, 10)):
        font = cv.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255, 255, 0)
        thickness = 2
        cv.putText(frame, text, bottom_left, font, fontScale, color, thickness, cv.LINE_AA)

        return super().apply(frame)

    def only_ballon(self, x,y,w,h):
        """ Chack there is only a small zone that could be a ballon"""
        return w < 100 and h < 100

    def apply(self, frame, context=None):
        pattern_color = (0, 255, 0)
        pattern_tickness = 2

        (best_area, basket_area) = self.find_basket_area(self.blur(frame))

        if best_area is None:
            self.check_move.last_frame = None
        else:
            area_extracted = best_area.extract(frame)
            frame_diff = self.check_move.apply(self.blur(area_extracted))

            # Pixels move in the area just around the basket
            # TODO depend on the basket image
            # basket_area = Area(Point(100, 50), Point(best_area.width()-30, best_area.height()-20))
            # basket_area = Area(Point(30, 30), Point(best_area.width()-30, best_area.height()-30)) # Just a margin that could be the same for all images
            pixels = np.sum(basket_area.extract(frame_diff))


            if context.show_video:
                # Display rectangle around the basket zone in which we check move
                frame_diff_bgr = cv.cvtColor(frame_diff, cv.COLOR_GRAY2BGR)
                self.draw_rectangle(frame_diff_bgr, basket_area)
          
                # incrust diff in the image
                y = 600
                x = 50
                self.write(frame, f"Pixels: {pixels}", (x, y-10))
                frame[y:y+best_area.height(),x:x+best_area.width()] = frame_diff_bgr[0:best_area.height(),0:best_area.width()]
                frame[y:y+best_area.height(),x+400:x+400+best_area.width()] = area_extracted[0:best_area.height(),0:best_area.width()]

            # import time
            # time.sleep(0.5)
            if pixels > 0:
                self.consecutive_detection += 1

                # Bounding rect around pixels should be in a small zone.
                # To avoid when camera move and all the basket panel seems moving
                (x,y,w,h) = cv.boundingRect(frame_diff)
                # moving_zone = cv.boundingRect(frame_diff)
                if self.only_ballon(x,y,w,h):
                    self.consecutive_ballon += 1

                    x += best_area.up_left.x
                    y += best_area.up_left.y
                    around_ballon_area = Area(Point(0,0), Point(w, h)).shift(x, y)
                    self.draw_rectangle(frame, around_ballon_area, COLOR.BLUE)
                    # self.draw_rectangle(frame, Area(Point(x,y), Point(x+w,y+h)), (255, 0, 0))
                    # cv.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)

                    # To avoid small noise !!!
                    # Sometime, there is one image not detected in sequence (4 frames detected, 1 not detected, 4 detected)
                    # When ballon hit the panel, the panel move  and it's not detected as a ballon move
                    # When ballon is on the basket, there is a move but not sure a ballon is detected
                    # We may have a condition that took 5 in 7 frames or something like that
                    # Or 5 consecutive move in which we detect almost 3 ballon moves
                    # if self.consecutive_detection > 5:

                    # Almost 3 ballon in 6 consecutive detection
                    if self.consecutive_detection >= 6 and self.consecutive_ballon >= 3:
                        # cv.waitKey(0)
                        pattern_color=COLOR.RED
                        pattern_tickness = 4

                        print(f"Frame: {context.frame_number} Time: {build_time_str(context.seconds)}")
            else:
                self.consecutive_ballon = 0
                self.consecutive_detection = 0

        if context.show_video and best_area is not None:
            cv.rectangle(frame, best_area.up_left.tuple(), best_area.bottom_right.tuple(), pattern_color, pattern_tickness)

        return frame

