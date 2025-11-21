import os 
from pathlib import Path
from subprocess import CompletedProcess
import subprocess

from doc_as_test_pytest import DocAsTest, doc, doc_module

from reader import *

class TestDocReader:
    """
    Le `reader` est un lecteur de vidéo permettant d'enregistrer les moments importants.
    Il est spécialisé dans les matchs de basket avec une interface simple pour enregistrer les paniers par équipe.
    """
    
    def test_utilisation(self, doc: DocAsTest):
        current_path=Path(__file__).parent        
        result: CompletedProcess  = subprocess.run(['python3', f'{current_path}/reader.py', '--help'], capture_output=True, text=True)
        
        output = result.stdout
        
        doc.write('\n'.join([
            "----",
            output,
            "----",
        ]))   