from pathlib import Path
import subprocess

from doc_as_test_pytest import doc, doc_module

from reader import *

class TestDocReader:
    """
    Le `reader` est un lecteur de vidéo permettant d'enregistrer les moments importants.
    Il est spécialisé dans les matchs de basket avec une interface simple pour enregistrer les paniers par équipe.
    """
    
    def test_utilisation(self, doc):
        current_path=Path(__file__).parent        
        result = subprocess.run(['python3', f'{current_path}/reader.py', '--help'], capture_output=True, text=True)
        
        output = result.stdout
        
        doc.write('\n'.join([
            "----",
            output,
            "----",
        ]))   