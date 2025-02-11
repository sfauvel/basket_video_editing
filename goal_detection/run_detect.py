import sys

from geometry import Area, Point
from transformer import FrameTransformer, DisplayContext
from video_player import VideoPlayer
from potential_score import ExtractMatchingZone, FastImageRecognition, SearchPattern

if __name__ == "__main__":
    args = sys.argv
    filename = args[1]
        
    extractor = ExtractMatchingZone([
                                ("../../Match_2025_02_01/panier_gauche.jpg", Area(Point(105,70), Point(245,190))),
                                ("../../Match_2025_02_01/panier_droit.jpg", Area(Point(30,70), Point(170,190))),
                            ])
    
    search = SearchPattern([
                ("../../Match_2025_02_01/panier_gauche.jpg", Area(Point(105,70), Point(245,190))),
                ("../../Match_2025_02_01/panier_droit.jpg", Area(Point(30,70), Point(170,190))),
            ])
    
    VideoPlayer().play(filename, 
                        [
                            # FastImageRecognition(extractor),
                            extractor,
                            # search,
                            DisplayContext()
                       ],
                       show_video=True,
                       start_at_frame=700,
                    #    end_at_frame=1630
                      # by_step=30,
                    )
    
# With ShortImageRecognition(extractor) => csv_auto_1,
# time . ./run.sh ../../Match_2025_02_01/video ../../Match_2025_02_01/csv_auto
# ../../Match_2025_02_01/video/VID_20250201_160247.mp4
# VID_20250201_160247.mp4
# Processing VID_20250201_160247

# real    9m44,827s
# user    16m23,129s
# sys     0m22,428s
# ../../Match_2025_02_01/video/VID_20250201_161431.mp4
# VID_20250201_161431.mp4
# Processing VID_20250201_161431

# real    5m14,702s
# user    8m38,269s
# sys     0m15,001s
# ../../Match_2025_02_01/video/VID_20250201_162208.mp4
# VID_20250201_162208.mp4
# Processing VID_20250201_162208

# real    10m2,719s
# user    16m56,162s
# sys     0m25,939s
# ../../Match_2025_02_01/video/VID_20250201_163459.mp4
# VID_20250201_163459.mp4
# Processing VID_20250201_163459

# real    5m38,552s
# user    9m24,266s
# sys     0m15,081s
# ../../Match_2025_02_01/video/VID_20250201_164237.mp4
# VID_20250201_164237.mp4
# Processing VID_20250201_164237

# real    1m0,985s
# user    1m43,344s
# sys     0m3,008s
# ../../Match_2025_02_01/video/VID_20250201_165929.mp4
# VID_20250201_165929.mp4
# Processing VID_20250201_165929

# real    12m18,640s
# user    20m44,211s
# sys     0m31,062s
# ../../Match_2025_02_01/video/VID_20250201_171501.mp4
# VID_20250201_171501.mp4
# Processing VID_20250201_171501

# real    9m56,577s
# user    16m29,569s
# sys     0m23,658s
# ../../Match_2025_02_01/video/VID_20250201_172736.mp4
# VID_20250201_172736.mp4
# Processing VID_20250201_172736

# real    10m49,842s
# user    18m9,217s
# sys     0m24,984s
# ../../Match_2025_02_01/video/VID_20250201_174039.mp4
# VID_20250201_174039.mp4
# Processing VID_20250201_174039

# real    4m54,759s
# user    8m15,069s
# sys     0m12,433s

# real    69m41,851s
# user    116m43,415s
# sys     2m53,657s


# With closed area with ShortImageRecognition
# ../../Match_2025_02_01/video/VID_20250201_160247.mp4
# VID_20250201_160247.mp4
# Processing VID_20250201_160247

# real    3m32,700s
# user    10m6,701s
# sys     0m20,320s
# ../../Match_2025_02_01/video/VID_20250201_161431.mp4
# VID_20250201_161431.mp4
# Processing VID_20250201_161431

# real    1m40,782s
# user    5m3,759s
# sys     0m11,636s
# ../../Match_2025_02_01/video/VID_20250201_162208.mp4
# VID_20250201_162208.mp4
# Processing VID_20250201_162208

# real    3m29,371s
# user    10m20,432s
# sys     0m20,601s
# ../../Match_2025_02_01/video/VID_20250201_163459.mp4
# VID_20250201_163459.mp4
# Processing VID_20250201_163459

# real    1m48,025s
# user    5m32,386s
# sys     0m11,399s
# ../../Match_2025_02_01/video/VID_20250201_164237.mp4
# VID_20250201_164237.mp4
# Processing VID_20250201_164237

# real    0m18,800s
# user    0m59,968s
# sys     0m2,668s
# ../../Match_2025_02_01/video/VID_20250201_165929.mp4
# VID_20250201_165929.mp4
# Processing VID_20250201_165929

# real    4m8,945s
# user    12m31,925s
# sys     0m19,565s
# ../../Match_2025_02_01/video/VID_20250201_171501.mp4
# VID_20250201_171501.mp4
# Processing VID_20250201_171501

# real    3m9,238s
# user    9m28,618s
# sys     0m24,054s
# ../../Match_2025_02_01/video/VID_20250201_172736.mp4
# VID_20250201_172736.mp4
# Processing VID_20250201_172736

# real    3m41,021s
# user    10m54,142s
# sys     0m21,078s
# ../../Match_2025_02_01/video/VID_20250201_174039.mp4
# VID_20250201_174039.mp4
# Processing VID_20250201_174039

# real    1m40,211s
# user    4m54,154s
# sys     0m12,239s

# real    23m29,321s
# user    69m52,239s
# sys     2m23,631s