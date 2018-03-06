
from kaiengine.debug import debugMessage

"""Container interface to allow something to access a contained objects methods and attributes
For when inheritance isn't a good idea for some reason, yet you want easy access to a class's stuff.
Note that this makes getting and setting attributes very slow! Use sparingly."""


class Container(object):
    """have a class inherit this to give it the setupContainer method"""

    _ContainerObjs = []

    def setupContainer(self, objname):
        if hasattr(self, objname):
            self._ContainerObjs = [objname] + self._ContainerObjs #done this way instead of insert to make sure it's a new list
        else:
            debugMessage("you misspelled the name of your attribute in a container, or it doesn't exist yet: " + objname)

    def subCall(self, method_name, *args, **kwargs):
        """Sorta the opposite of super, this calls routines with the name method_name and given arguments for all contained objs"""
        for objname in self._ContainerObjs:
            if hasattr(getattr(self, objname), method_name):
                getattr(getattr(self, objname), method_name)(*args, **kwargs)

    def removeContainer(self, objname):
        if objname in self._ContainerObjs:
            self._ContainerObjs.remove(objname)

    def removeContainers(self):
        for objname in self._ContainerObjs:
            self.removeContainer(objname)

    def __getattr__(self, name):
        for obj in self._ContainerObjs:
            try:
                return getattr(getattr(self, obj), name)
            except AttributeError:
                pass
            except RuntimeError: #infinite loop detected:
                self.removeContainer(obj)
                debugMessage("Infinite loop detected in container. " + obj + " key removed.")
        raise AttributeError("Attribute not found: " + name)

    def __setattr__(self,name, value):
        if name not in dir(self):
            for obj in self._ContainerObjs:
                if hasattr(getattr(self, obj), name):
                    setattr(getattr(self, obj), name, value)
                    return
        if Container is not None: #end of game error suppression
            super(Container, self).__setattr__(name, value)

    def destroy(self):
        if Container: #end of game error suppression
            if hasattr(super(Container, self), "destroy"):
                super(Container, self).destroy()
        self.removeContainers()
