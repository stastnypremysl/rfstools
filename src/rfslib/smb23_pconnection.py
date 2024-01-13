import smbclient as smb
import smbclient.path as spath

from rfslib import abstract_pconnection, pconnection_settings
import socket
from os.path import split

import shutil, stat

def config_smb23(username: str = None, password: str = None, no_dfs: bool = False, disable_secure_negotiate: bool = False, dfs_domain_controller: str = None, auth_protocol: str = 'negotiate'):
  '''The procedure changes global setting for SMB version 2 or 3 across all connection. Don't change value, if any SMB connection version 2 or 3 is active.

  Args:
    username: Optional default username used when creating a new SMB session.
    password: Optional default password used when creating a new SMB session.
    no_dfs: Disables DFS support - useful as a bug fix.
    disable_secure_negotiate: Disables secure negotiate requirement for a SMB connection.
    dfs_domain_controller: The DFS domain controller address. Useful in case, when rfstools fails to find it themself.
    auth_protocol: The protocol to use for authentication. Possible values are 'negotiate', 'ntlm' or 'kerberos'. Defaults to 'negotiate'.
  '''
  smb.ClientConfig(
    username=username,
    password=password,
    skip_dfs=no_dfs, 
    require_secure_negotiate=not disable_secure_negotiate,
    domain_controller=dfs_domain_controller,
    auth_protocol=auth_protocol
  )


def _contain_toxic_char(remote_path):
  for char in "?<>\:*|":
    if char in remote_path:
      return True
  
  return False


class Smb23PConnection(abstract_pconnection.PConnection):
  '''Class for SMB connection version 2 or 3. Public interface with an exception of __init__ and close is inherited from PConnection.'''

  def __init__(self, settings: pconnection_settings, host: str, service_name: str, username: str, password: str, port: int = 445, enable_encryption: bool = False, dont_require_signing: bool = False):
    '''The constructor of Smb23PConnection. Opens SMB connection version 2 or 3, when called.

    Args:
      settings: The settings for the super class PConnection.
      service_name: Name of a shared folder.
      host: Remote address of the server.
      port: Port for a SMB connection.
      username: Remote username
      password: Password for a SMB connection.
      enable_encryption: Enables encryption for a SMB3 connection.
      dont_require_signing: Disables signing requirement.
    '''
    super().__init__(settings)

    self.__service_name = service_name
    self.__host = host

    smb.register_session(host, username=username, password=password,
      port=port, encrypt=enable_encryption, require_signing=not dont_require_signing)


  def close(self):
    pass

  def __prefix_path(self, path):
    return '\\\\' + self.__host + '\\' + self.__service_name + '\\' + path

  def _listdir(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)
    return smb.listdir(p_remote_path)

  def _rename(self, old_name, new_name):
    p_old_name = self.__prefix_path(old_name)
    p_new_name = self.__prefix_path(new_name)
    
    smb.rename(p_old_name, p_new_name)

  def _push(self, local_path, remote_path):
    p_remote_path = self.__prefix_path(remote_path)

    with open(local_path, "rb") as local_file, smb.open_file(p_remote_path, "wb") as remote_file:
      shutil.copyfileobj(local_file, remote_file)

  def _pull(self, remote_path, local_path):
    p_remote_path = self.__prefix_path(remote_path)

    with smb.open_file(p_remote_path, "rb") as remote_file, open(local_path, "wb") as local_file:
      shutil.copyfileobj(remote_file, local_file)
  
  def _isdir(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)

    return spath.isdir(p_remote_path)
  
  def _mkdir(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)

    smb.mkdir(p_remote_path)

  def _rmdir(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)

    smb.mkdir(p_remote_path)

  def _unlink(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)

    smb.unlink(p_remote_path)

  def _exists(self, remote_path):
    if remote_path == '' or _contain_toxic_char(remote_path):
      return False

    p_remote_path = self.__prefix_path(remote_path)

    return spath.exists(p_remote_path)
  
  def _lexists(self, remote_path):
    if remote_path == '' or _contain_toxic_char(remote_path):
      return False

    p_remote_path = self.__prefix_path(remote_path)

    return spath.lexists(p_remote_path)

  def _stat(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)

    return smb.stat(p_remote_path)

  def _lstat(self, remote_path):
    p_remote_path = self.__prefix_path(remote_path)
    
    return smb.lstat(p_remote_path)


