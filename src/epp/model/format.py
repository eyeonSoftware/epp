
# -------------------------------------------------------------------------------------
def format_from_dict(format_dict):
    """docstring for from_dict"""
    
    formatobj = Format( 
        int(format_dict["width"]),
        int(format_dict["height"]),
        float(format_dict["framerate"] ),
        float(format_dict["aspectx"] ),
        float(format_dict["aspecty"] ),
        str(format_dict["name"]),
        )

    return formatobj

# #############################################################################################
class Format(object):
    """Video Format"""
    # -------------------------------------------------------------------------------------
    # Attributes
    # -------------------------------------------------------------------------------------
    def name():
        doc = "The name property."
        def fget(self):
            return self._name
        def fset(self, value):
            self._name = value
        return locals()
    name = property(**name())

    # -------------------------------------------------------------------------------------
    def width():
        doc = "The width property."
        def fget(self):
            return self._width
        def fset(self, value):
            self._width = value
        return locals()
    width = property(**width())

    # -------------------------------------------------------------------------------------
    def height():
        doc = "The height property."
        def fget(self):
            return self._height
        def fset(self, value):
            self._height = value
        return locals()
    height = property(**height())

    # -------------------------------------------------------------------------------------
    def framerate():
        doc = "The framerate property."
        def fget(self):
            return self._framerate
        def fset(self, value):
            self._framerate = value
        return locals()
    framerate = property(**framerate())

    # -------------------------------------------------------------------------------------
    def aspectx():
        doc = "The aspectx property."
        def fget(self):
            return self._aspectx
        def fset(self, value):
            self._aspectx = value
        return locals()
    aspectx = property(**aspectx())

    # -------------------------------------------------------------------------------------
    def asepecty():
        doc = "The asepecty property."
        def fget(self):
            return self._asepecty
        def fset(self, value):
            self._asepecty = value
        return locals()
    asepecty = property(**asepecty())


    # -------------------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------------------
    def __init__(self, width, height, framerate, aspectx, aspecty, name="Custom"):
        super(Format, self).__init__()

        self.width = width
        self.height = height
        self.framerate = framerate
        self.aspectx = aspectx
        self.aspecty = aspecty
        self.name = name
    
    # -------------------------------------------------------------------------------------
    def __unicode__(self):
        """docstring for __unicode__"""
        return "{0} Format ({1}x{2} @ {3:03}fps - {4:02}:{5:02})".format(self.name, self.width, self.height, self.framerate, self.aspectx, self.aspecty)

    # -------------------------------------------------------------------------------------
    def __str__(self):
        return unicode(self).encode('utf-8')
    

    # -------------------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------------------
    def to_dict(self, keyprefix=""):
        """Return a dict of the format"""
        
        format_dict = {
                keyprefix+"width": self.width,
                keyprefix+"height": self.height,
                keyprefix+"framerate": self.framerate,
                keyprefix+"aspectx": self.aspectx,
                keyprefix+"aspecty": self.aspecty,
                keyprefix+"name": self.name,
                }

        return format_dict

