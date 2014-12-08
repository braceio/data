## ERRORS ---------------------------------------------------------------------

class GenericError(Exception):
    def __init__(self, msg=None, code=None):
        self.code = code
        self.msg = msg

    def __str__(self):
        return self.__unicode__().encode('UTF-8')

    def __unicode__(self):
        result = u""
        if hasattr(self, 'msg') and self.msg:
            result+= unicode(self.msg)
        if hasattr(self, 'code') and self.code:
            result+= u"(code %s)" % unicode(self.code)
        return result

    def toDict(self):
        result = {}
        if hasattr(self, 'msg') and self.msg:
            result.update('msg', self.msg)
        if hasattr(self, 'code') and self.code:
            result.update('code', self.code)
        return result


class UnexpectedError(GenericError):
    pass

