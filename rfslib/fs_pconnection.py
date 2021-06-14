from rfslib import abstract_pconnection

import os, sys, shutil

class FsPConnection(abstract_pconnection.PConnection):
  def __init__(self, **arg):
    super().__init__(**arg)

  def close(self):
    pass
  
  def _listdir(self, remote_path):
    return os.listdir(remote_path)

  def _rename(self, old_name, new_name):
    os.rename(old_name, new_name) 

  def _push(self, local_path, remote_path):
    shutil.copy(local_path, remote_path)

  def _pull(self, remote_path, local_path):
    shutil.copy(remote_path, local_path)
  
  def _isdir(self, remote_path):
    return os.path.isdir(remote_path)
  
  def _mkdir(self, remote_path):
    os.mkdir(remote_path, mode=744)

  def _rmdir(self, remote_path):
    os.rmdir(remote_path)

  def _unlink(self, remote_path):
    os.unlink(remote_path)

  def _exists(self, remote_path):
    return os.path.exists(remote_path)
  
  def _lexists(self, remote_path):
    return os.path.lexists(remote_path)


