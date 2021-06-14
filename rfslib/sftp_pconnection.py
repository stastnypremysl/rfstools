import pysftp
from rfslib import abstract_pconnection

class SftpPConnection(abstract_pconnection.PConnection):
  def __init__(self, **arg):
    super().__init__(**arg)

    if arg["password"] == None:
      self.__sftp = pysftp.Connection(host=arg["host"], username=arg["username"], private_key=arg["keyfile"], port=arg["port"])
    else:
      self.__sftp = pysftp.Connection(host=arg["host"], username=arg["username"], password=arg["password"], port=arg["port"])

  def close(self):
    self.__sftp.close()
  
  def _listdir(self, remote_path):
    return self.__sftp.listdir(remotepath=remote_path)

  def _rename(self, old_name, new_name):
    self.__sftp.rename(old_name, new_name) 

  def _push(self, local_path, remote_path):
    self.__sftp.put(local_path, remotepath=remote_path)

  def _pull(self, remote_path, local_path):
    self.__sftp.get(remote_path, localpath=local_path)
  
  def _isdir(self, remote_path):
    return self.__sftp.isdir(remote_path)
  
  def _mkdir(self, remote_path):
    self.__sftp.mkdir(remote_path, mode=744)

  def _rmdir(self, remote_path):
    self.__sftp.rmdir(remote_path)

  def _unlink(self, remote_path):
    self.__sftp.unlink(remote_path)

  def _exists(self, remote_path):
    return self.__sftp.exists(remote_path)
  
  def _lexists(self, remote_path):
    return self.__sftp.lexists(remote_path)


