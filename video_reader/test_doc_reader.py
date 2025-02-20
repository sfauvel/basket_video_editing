import subprocess

from doc_as_test_pytest import DocAsTest, doc, doc_module

from reader import *

class TestDocReader:
    """
    Le `reader` permet lire une vidéo et de noter les moments importants (paniers, sequences, ...).
    """
    
    def test_utilisation(self, doc):
        
        result = subprocess.run(['python3', 'reader.py', '--help'], capture_output=True, text=True)
        
        output = result.stdout
        
        doc.write('\n'.join([
            "----",
            output,
            "----",
        ]))   