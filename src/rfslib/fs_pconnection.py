from rfslib import abstract_pconnection, pconnection_settings

import os, sys, shutil

class FsPConnection(abstract_pconnection.PConnection):
  '''Class for operating with local filesystem. Public interface with an exception of __init__ and close is inherited from PConnection.'''

  def __init__(self, settings: pconnection_settings):
    '''The constructor of FsPConnection.
    
    Args:
      settings: The settings for super class PConnection.
    '''
    super().__init__(settings)

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
  
  def _stat(self, remote_path):
    return os.stat(remote_path)

  def _lstat(self, remote_path):
    return os.lstat(remote_path)


