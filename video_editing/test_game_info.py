from doc_as_test_pytest import DocAsTest, doc, doc_module # type: ignore

from game_info import GameInfo

class TestGameInfo:
    """
    Information of the game is retrieve from the file.
    """
    
    def test_extract_info_from_file(self, doc: DocAsTest, tmp_path: str) -> None: 
        file_content = """Date: 22/02/2025
Locaux: Paris
Visiteurs: Cholet
"""
        filepath = f"{tmp_path}/{GameInfo.FILENAME}"
        with open(filepath, "w") as file:
            file.write(file_content)

        doc.write(f"Game information can be retrieve from the text file `{GameInfo.FILENAME}`.\n")
        doc.write("\n.file content:\n")
        doc.write("----\n")
        doc.write(file_content)
        doc.write("----\n")

        info = GameInfo.load(filepath)
        doc.write(f"\n.info extracted\n")
        doc.write(f"- Date: *{info.date}*\n")
        doc.write(f"- Locaux: *{info.locaux}*\n")
        doc.write(f"- Visiteurs: *{info.visiteurs}*\n")
        