from smb.SMBConnection import SMBConnection

from rfslib import abstract_pconnection
import socket
from os.path import split

class SmbPConnection(abstract_pconnection.PConnection):
  def __init__(self, **arg):
    super().__init__(**arg)
    my_hostname = socket.gethostname()

    self.__service_name = arg["service_name"]
    self.__smb = SMBConnection(arg["username"], arg["password"], my_hostname, arg["host"])

    if not self.__smb.connect(arg["host"], port=arg["port"]):
      raise ConnectionError("Can't connect to SMB host {}:{}.".format(arg["host"], arg["port"]))

  def close(self):
    self.__smb.close()
  
  def _listdir(self, remote_path):
    l = self.__smb.listPath(self.__service_name, remote_path)
    return map (lambda x: x.filename, l)

  def _rename(self, old_name, new_name):
    self.__smb.rename(self.__service_name, old_name, new_name) 

  def _push(self, local_path, remote_path):
    local_file = open(local_path, "rb")
    self.__smb.storeFile(self.__service_name, remote_path, local_file)

  def _pull(self, remote_path, local_path):
    local_file = open(local_path, "wbx")
    self.__smb.retrieveFile(self.__service_name, remote_path, local_file)
  
  def _isdir(self, remote_path):
    attr = self.__smb.getAttributes(self.__service_name, remote_path)
    return attr.isDirectory()
  
  def _mkdir(self, remote_path):
    self.__smb.createDirectory(self.__service_name, remote_path)

  def _rmdir(self, remote_path):
    self.__smb.deleteDirectory(self.__service_name, remote_path)

  def _unlink(self, remote_path):
    self.__smb.deleteFiles(self.__service_name, remote_path)

  def _exists(self, remote_path):
    dirname, basename = split(remote_path)
    return basename in self._listdir(dirname)
  
  def _lexists(self, remote_path):
    return self._exists(remote_path)


