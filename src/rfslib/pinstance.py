
class PInstance():
  def __init__(self):
    self.connection = None

  def close(self):
    if self.connection != None:
      self.connection.close()

  def __enter__(self):
    return self

  def __exit__(self, x, y, z):
    self.close()
