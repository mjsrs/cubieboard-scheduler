import json
import os


def getConfiguration(filePath):
    _json = {}
    if os.path.exists(filePath):
        with open(filePath) as f:
            data = f.read()
            try:
                _json = json.loads(data)
            except ValueError:
                _json = {}
    return _json
