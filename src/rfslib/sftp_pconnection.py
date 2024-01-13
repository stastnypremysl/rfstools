import paramiko
from rfslib import abstract_pconnection, pconnection_settings

from stat import S_ISDIR
import logging

class SftpPConnection(abstract_pconnection.PConnection):
  '''Class for SFTP connection. Public interface with an exception of __init__ and close is inherited from PConnection.'''

  def __init__(self, settings: pconnection_settings, host: str, username: str, password: str = None, keyfile : str = '~/.ssh/id_rsa', port: int = 22, no_host_key_checking: bool = False):
    '''The constructor of SftpPConnection. Opens SFTP connection, when called. If None password is specified, the key authentication will be used. Otherwise the password authentication will be used.
    
    Args:
      settings: The settings for the super class PConnection.
      host: Remote address of the server.
      port: Port for the SFTP connection.
      username: Remote username
      password: Password for a SFTP connection. If None is provided, key authentication will be used.
      keyfile: A path to key file.
      no_host_key_checking: Specifies, whether remote host key should be verified or not.
    '''
    super().__init__(settings)

    client = paramiko.SSHClient()    

    host_key_policy = None
    if no_host_key_checking == True:
      logging.warning("DANGER! Strict host key checking is disabled.")

      # This policy just ignore everything
      host_key_policy = paramiko.client.MissingHostKeyPolicy

    else:
      client.load_system_host_keys()
      host_key_policy = paramiko.client.RejectPolicy

    client.set_missing_host_key_policy(host_key_policy)
      
    if password == None:
      client.connect(hostname=host, port=port, username=username, key_filename=keyfile)
    else:
      client.connect(hostname=host, port=port, username=username, password=password)

    self.__sftp = client.open_sftp()

  def close(self):
    self.__sftp.close()
  
  def _listdir(self, remote_path):
    return self.__sftp.listdir(path=remote_path)

  def _rename(self, old_name, new_name):
    self.__sftp.rename(old_name, new_name) 

  def _push(self, local_path, remote_path):
    self.__sftp.put(local_path, remote_path)

  def _pull(self, remote_path, local_path):
    self.__sftp.get(remote_path, local_path)
  
  def _isdir(self, remote_path):
    result = False
    try:
      result = S_ISDIR(self.__sftp.stat(remote_path).st_mode)
    except IOError:     # no such file
      result = False
    return result
  
  def _mkdir(self, remote_path):
    self.__sftp.mkdir(remote_path)

  def _rmdir(self, remote_path):
    self.__sftp.rmdir(remote_path)

  def _unlink(self, remote_path):
    self.__sftp.unlink(remote_path)

  def _exists(self, remote_path):
    try:
      self.__sftp.stat(remote_path)
    except IOError:
      return False

    return True
  
  def _lexists(self, remote_path):
    try:
      self.__sftp.lstat(remote_path)
    except IOError:
      return False
    return True

  def _stat(self, remote_path):
    return self.__sftp.stat(remote_path)

  def _lstat(self, remote_path):
    return self.__sftp.lstat(remote_path)


