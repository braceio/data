

class GSCredentials (object):
  def __init__ (self, access_token=None):
    self.access_token = access_token

  def refresh (self, http):
    print "REFRESH!!"
