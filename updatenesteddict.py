from collections import Mapping

def updateNestedDict(originalDict, updateDict):
    for key, value in updateDict.items():
        if isinstance(value, Mapping):
            result = updateNestedDict(originalDict.get(key, {}), value)
            originalDict[key] = result
        else:
            originalDict[key] = updateDict[key]
    return originalDict
