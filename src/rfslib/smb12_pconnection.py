from smb.SMBConnection import SMBConnection

from rfslib import abstract_pconnection, pconnection_settings
import socket
from os.path import split

class Smb12PConnection(abstract_pconnection.PConnection):
  '''Class for SMB connection version 1 or 2. Public interface with an exception of __init__ and close is inherited from PConnection.'''
  def __init__(self, settings: abstract_pconnection.pconnection_settings, 
    host: str, service_name: str, username: str, password: str, 
    port: int = 139, use_direct_tcp: bool = False, client_name: str = "RFS", use_ntlm_v1: bool = False):
    '''The constructor of Smb12PConnection. Opens SMB connection version 1 or 2, when called.
    
    Args:
      settings: The settings for the super class PConnection.
      host: Remote address of the server.
      service_name: Name of a shared folder.
      port: Port for the SMB connection.
      username: Remote username.
      password: Remote password.
      use_direct_tcp: Activates direct tcp mode for SMB.
      client_name: Name of this client, which will be sent to a server.
      use_ntlm_v1: Enables NTLM version 1 instead of NTLM version 2.
    '''
    super().__init__(settings)

    self.__service_name = service_name
    self.__smb = SMBConnection(username, password, client_name, host,
      use_ntlm_v2=not use_ntlm_v1, is_direct_tcp=use_direct_tcp)

    if not self.__smb.connect(host, port=port):
      raise ConnectionError("Can't connect to SMB host {}:{}.".format(host, port))

    if self.__smb.isUsingSMB2:
      self.__version = 2
    else:
      self.__version = 1

  def close(self):
    self.__smb.close()
  
  def _listdir(self, remote_path):
    l = self.__smb.listPath(self.__service_name, remote_path)
    return map (lambda x: x.filename, l)

  def _rename(self, old_name, new_name):
    self.__smb.rename(self.__service_name, old_name, new_name) 

  def _push(self, local_path, remote_path):
    with open(local_path, "rb") as local_file:
      self.__smb.storeFile(self.__service_name, remote_path, local_file)

  def _pull(self, remote_path, local_path):
    with open(local_path, "wb") as local_file:
      self.__smb.retrieveFile(self.__service_name, remote_path, local_file)
  
  def _isdir(self, remote_path):
    attr = self.__smb.getAttributes(self.__service_name, remote_path)
    return attr.isDirectory
  
  def _mkdir(self, remote_path):
    self.__smb.createDirectory(self.__service_name, remote_path)

  def _rmdir(self, remote_path):
    self.__smb.deleteDirectory(self.__service_name, remote_path)

  def _unlink(self, remote_path):
    self.__smb.deleteFiles(self.__service_name, remote_path)

  def _exists(self, remote_path):
    if remote_path == '/':
      return True

    dirname, basename = split(remote_path)
    return basename in self._listdir(dirname)
  
  def _lexists(self, remote_path):
    # Yes, this is wrong.
    return self._exists(remote_path)

  def __get_mask(self, attr):
    if attr.isDirectory:
      mask = self.get_default_dmask()

    else:
      mask = self.get_default_fmask()

    if attr.isReadOnly:
      mask = 0o222 & mask

    return mask

  def __get_mode(self, attr):
    mask = self.__get_mask(attr)
    pmode = (~ mask) & 0o777

    if attr.isDirectory:
      return pmode | 0o0040000

    else:
      return pmode | 0o0100000


  def _stat(self, remote_path):
    attr = self.__smb.getAttributes(self.__service_name, remote_path)

    attr.st_mode_smb12 = self.__get_mode(attr)
    return attr

  def _lstat(self, remote_path):
    # Yes, this is also wrong.
    return self._stat(remote_path)


