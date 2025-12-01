from doc_as_test_pytest import DocAsTest, doc, doc_module

import video_utils

class TestTimeMapping:
    """
    Utilities to map time to string.
    """
    
    def test_time_to_seconds(self, doc):
        """
        The function `time_to_seconds` transform the text of a time to the number of seconds. 
        """
        
        def text_time_to_seconds(time):
            try:
                seconds = video_utils.time_to_seconds(time)
                return f"- {time} -> {seconds}s"
            except Exception as e:
                return f"- {time} -> Exception: {e}"

        doc.write(' +\n'.join([
            text_time_to_seconds("0:05"),
            text_time_to_seconds("4:25"),
            text_time_to_seconds("134:25"),
            text_time_to_seconds("1:14:25"),
        ]))        
        doc.write("\n\nWhen text is mal formed, an exception is raised.\n\n")
        doc.write(' +\n'.join([
            text_time_to_seconds("5s"),
            text_time_to_seconds("1:02:14:25"),
        ]))
        
    def test_seconds_to_time(self, doc):
        """
        The function `seconds_to_time` transform a number of seconds to a time as text. 
        """
        
        def text_seconds_to_time(seconds):
            time = video_utils.seconds_to_time(seconds)
            return f"- {seconds}s -> {time}"

        doc.write(' +\n'.join([
            text_seconds_to_time(5),
            text_seconds_to_time(4*60+25),
            text_seconds_to_time(1*3600+14*60+25),
        ]))
import os
import shutil
class Folder:
    def recreate(folder):
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

class TestFiles:
    def test_sort(self, doc):
        folder = "tmp"
        Folder.recreate(folder)
        files = ["tmp3.csv", "tmp1.csv", "tmp2.csv", "tmp4.txt"]

        for file in files:
            open(f"tmp/{file}", 'a').close()
        

        patterns = ["tmp/*", "tmp/*.csv", "tmp/*.txt"]
        doc.write("\n".join([
            f"When creating, in folder `{folder}`, those files in this order: " + ", ".join([f"`{f}`" for f in files]),
            "",
            ".files_sorted",
            "|====",
            "| pattern | result",
            "",
        
            "\n".join([f"| {p} | " + ", ".join(video_utils.files_sorted(p)) for p in patterns]),
        
            "|===="
        ]))

    def test_files_before(self, doc):
        folder = "tmp"
        Folder.recreate(folder)
        files = ["tmp3.csv", "tmp1.csv", "tmp2.csv", "tmp4.txt"]

        for file in files:
            open(f"tmp/{file}", 'a').close()
        

        patterns = ["tmp/*", "tmp/*.csv", "tmp/*.txt"]

        files_xx = [f"tmp/{f}" for f in files]
        files_xx.sort()
        doc.write("\n".join([
            f"When creating, in folder `{folder}`, those files in this order: " + ", ".join([f"`{f}`" for f in files]),
            "We can find files before another file according to there name."
            "",
            "",
            ".files_sorted",
            "|====",
            "| file input | file before",
            "",
        
            "\n".join([f"| {f} | " + ", ".join(video_utils.files_before("tmp/*.csv", f)) for f in files_xx]),
        
            "|===="
        ]))