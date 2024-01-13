from rfslib import abstract_pconnection, pconnection_settings
import ftplib
import ftputil

from os.path import split

class FtpPConnection(abstract_pconnection.PConnection):
  '''Class for FTP connection. Public interface with an exception of __init__ and close is inherited from PConnection.'''


  def __init__(self, settings: pconnection_settings, host: str, username: str, password: str, port: int = 21, tls: bool = False, passive_mode: bool = False, debug_level: int = 1, connection_encoding: str = 'UTF8', dont_use_list_a: bool = False):
    '''The constructor of FtpPConnection.
    
    Args:
      settings: The settings for the super class PConnection.
      host: Remote address of the server.
      port: Port for a connection.
      username: Remote username.
      password: Remote password.
      tls: Enables TLS.
      passive_mode: Enables passive mode of FTP connection.
      debug_level: Specifies how much logs should be generated. 0 - almost non, 1 - more, 2 - log almost everything
      connection_encoding: Encoding used for a connection.
      dont_use_list_a: Disables usage of LIST -a command and uses LIST command instead. You might consider using option direct_write when using dont_use_list_a.
    '''
    super().__init__(settings)

    if tls:
      factory_b_class = ftplib.FTP_TLS
    else:
      factory_b_class = ftplib.FTP

    session_factory = ftputil.session.session_factory(
      base_class = factory_b_class,
      port = port,
      encrypt_data_channel = tls,
      encoding = connection_encoding,
      use_passive_mode = passive_mode,
      debug_level = debug_level)

    self.__ftp = ftputil.FTPHost(host, username, password, session_factory=session_factory)
    self.__ftp.use_list_a_option = not dont_use_list_a


  def close(self):
    self.__ftp.close()
  
  def _listdir(self, remote_path):
    return self.__ftp.listdir(remote_path)

  def _rename(self, old_name, new_name):
    self.__ftp.rename(old_name, new_name) 

  def _push(self, local_path, remote_path):
    self.__ftp.upload(local_path, remote_path)

  def _pull(self, remote_path, local_path):
    self.__ftp.download(remote_path, local_path)
  
  def _isdir(self, remote_path):
    return self.__ftp.path.isdir(remote_path)
  
  def _mkdir(self, remote_path):
    self.__ftp.mkdir(remote_path)

  def _rmdir(self, remote_path):
    self.__ftp.rmdir(remote_path)

  def _unlink(self, remote_path):
    self.__ftp.unlink(remote_path)

  def _exists(self, remote_path):
    # Workaround
    if remote_path == '':
      return False

    return self.__ftp.path.exists(remote_path)
  
  def _lexists(self, remote_path):
    # To be fixed
    # Waiting for https://github.com/sschwarzer/ftputil/pull/1
    return self._exists(remote_path)

  def _stat(self, remote_path):
    return self.__ftp.stat(remote_path)

  def _lstat(self, remote_path):
    return self.__ftp.lstat(remote_path)
