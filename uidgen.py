

#Unique ID Generator
#Guaranteed to return a unique string ID, though not across multiple runnings of the program (IE don't save these)
#
#pass something convertable to a string to add it to the generated ID,
#if you want to store data in it for debugging/etc

BASE_UNIQUE_STRING = "_UNIQUE_ID_"
UNDERSCORE_CHAR = "_"
DEFAULT_ID = "DEFAULT_TYPE"

id_counters = {}

def generateUniqueID(identifier = DEFAULT_ID):
    identifier = str(identifier) #be sure it's a string
    try:
        id_counters[identifier] += 1
    except KeyError:
        id_counters[identifier] = 0
    return BASE_UNIQUE_STRING + identifier + UNDERSCORE_CHAR + str(id_counters[identifier])

class IdentifiedObject(object):

    '''Provide child objects with unique IDs.'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = generateUniqueID(self.__class__.__name__)
        
    def combineID(self, *args):
        '''consistently combine multiple ids for a unique ID'''
        returnstr = self.id[:]
        for arg in args:
            returnstr += str(arg)
        return returnstr
        

GenerateUniqueID = generateUniqueID #deprecated function name
