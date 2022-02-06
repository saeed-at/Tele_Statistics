import json 

def read_json(file_path : str) -> dict:
    """Reads json file and returns a dictionary
    """
    with open(file_path) as f :
        return json.load(f)
    
    
def read_file(file_path : str) -> str :
    """Read a file and returns the content
    """
    with open(file_path) as f:
        return f.read()
    