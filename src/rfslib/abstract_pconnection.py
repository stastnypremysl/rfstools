from abc import ABC, abstractmethod
from typing import List

import tempfile
import os
import os.path
import shutil
import codecs

from rfslib import pconnection_settings
from rfslib.path_utils import path_normalize

import random

import logging, sys

import re
re_public_var = re.compile(r'^[^_].*')
#re_not_dot_dotdot = re.compile(r'^[^.][^.]*.*


class p_stat_result():
  '''Representation of the attributes of a file (or proxied file). It attemps to mirror the object returned by os.stat as closely as possible.'''

  st_mode:int = None
  ''' This field contains the file type and mode.'''
  st_size:int = None
  '''This field gives the size of the file (if it is a regular file or a symbolic link) in bytes. The size of a symbolic link is the length of the pathname it contains, without a terminating null byte.'''

  st_mtime:int = None
  '''This is the time of last modification of file data.'''
  st_atime:int = None
  '''This is the time of the last access of file data.'''

  st_uid:int = None
  '''This field contains the user ID of the owner of the file.'''
  st_gid:int = None
  '''This field contains the ID of the group owner of the file.'''

  st_nlink:int = None
  '''This field contains the number of hard links to the file.'''


def _stat_unpack(pk_stat) -> p_stat_result:
  '''This function tries to translate arbitrary stat object to p_stat_result object.'''
  stat = p_stat_result()
  
  def aliases(*kw, default_value=None):
    default = kw[0]
    lstat = stat

    for alias in kw:
      if hasattr(pk_stat, alias):
        exec(f'lstat.{default} = pk_stat.{alias}')
        return
    
    if default_value is not None:
      exec(f'lstat.{default} = default_value')


  aliases('st_mode', 'st_mode_smb12')
  aliases('st_size', 'file_size')

  aliases('st_mtime', 'last_write_time')
  aliases('st_atime', 'last_access_time', default_value=stat.st_mtime)
  
  aliases('st_uid', default_value=0)
  aliases('st_gid', default_value=0)

  aliases('st_nlink', default_value=0)

  return stat


class PConnection(ABC):
  def set_settings(self, settings: pconnection_settings):
    '''The procedure sets all generic settings for PConnection.

    Args:
      settings: A pconnection_settings object with all generic settings for PConnection. If some attribute in object is missing, no operation will be done with it.
    '''

    for attr in filter(re_public_var.match, dir(pconnection_settings)):
      if hasattr(settings, attr):
        logging.debug(f"Setting self.__{attr} to {getattr(settings, attr)}.")
        exec(f'self._PConnection__{attr} = settings.{attr}')



  def get_settings(self) -> pconnection_settings:
    '''The procedure sets all generic settings for PConnection.

    Returns:
      A pconnection_settings object with all generic settings of PConnection.
    '''
    ret = pconnection_settings()

    for attr in filter(re_public_var.match, dir(pconnection_settings())):
      exec(f'ret.{attr} = self._PConnection__{attr}')

    return ret


  def get_default_fmask(self) -> int:
    '''Returns default_fmask settings. For more details see pconnection_settings.'''
    return self.__default_fmask


  def get_default_dmask(self) -> int:
    '''Returns default_dmask settings. For more details see pconnection_settings.'''
    return self.__default_dmask
 

  def __init__(self, settings: pconnection_settings):
    """The constructor of a abstract class. If it is not called from child class, the behavior is undefined.

    If local_encoding and remote_encoding have same values, no recoding is done. Analogically if local_crlf and remote_crlf is same, no substitution between LF and CRLF is done.

    Args:
      settings: A pconnection_settings object with all generic settings for PConnection. Be sure, that all needed attributes are present, or AttributeError will be raised.

    :meta public:
    """

    for attr in filter(re_public_var.match, dir(pconnection_settings())):
      if not hasattr(settings, attr):
        raise AttributeError(f"Parameter settings argument doesn't have attribute {attr}")

    self.set_settings(settings)
    

  @abstractmethod
  def close(self):
    """Method to close the opened connection."""
    pass

  @abstractmethod
  def _stat(self, remote_path: str) -> os.stat_result:
    """Protected method which returns statistics of a file (eg. size, last date modified,...) Follows symlinks to a destination file.
    Undefined behavior if remote file doesn't exist or it is a broken symlink.
    
    Args:
      remote_path: Path of a remote file.

    Returns:
      The function returns os.stat_result like object, which is further parsed by _stat_unpack function. For more details please see source code. 

    :meta public:
    """
    pass

  @abstractmethod
  def _lstat(self, remote_path: str) -> os.stat_result:
    """Protected method which returns statistics of a file (eg. size, last date modified,...)  Doesn't follow symlinks.
    Undefined behavior if remote file doesn't exist.
    
    Args:
      remote_path: Path of a remote file.

    Returns:
      The function returns os.stat_result like object, which is further parsed by _stat_unpack function. For more details please see source code. 

    """
    pass

  @abstractmethod
  def _listdir(self, remote_path:str) -> List[str]: 
    """Protected method which returns a list of files in the folder including hidden files. It might contain '.' and '..'.
    Undefined if the remote file doesn't exist or isn't a folder.

    Args:
      remote_path: The remote path of a remote folder.

    Returns:
      A list of files in the remote folder.
      
    :meta public: 
    """
    pass

  @abstractmethod
  def _rename(self, old_name:str, new_name:str):
    """Protected method which renames/moves a file. Behavior is undefined, if `new_name` file exists or `old_name` file doesn't exist.

    Args:
      old_name: Remote path a file to move.
      new_name: Remote path to which move the file.
      
    :meta public: 
    """

    pass

  @abstractmethod
  def _push(self, local_path:str, remote_path:str):
    """Protected method which uploads/pushes a nondirectory file from a local storage to a remote storage in the binary form. Behavior is undefined if destination folder or source file doesn't exist, source is directory or remote file already exists.

    Args:
      local_path: Path of a local file to upload.
      remote_path: Path on the remote storage, where to upload/push a local file.
      
    :meta public: 
    """
    pass

  @abstractmethod
  def _pull(self, remote_path:str, local_path:str):
    """Protected method which downloads/pulls a nondirectory file from a remote storage to a local storage in the binary form. Behavior is undefined if source file or destination folder doesn't exist.

    Args:
      remote_path: Path of a remote file to download.
      local_path: Path of a local file, where to download/pull a remote file or local file already exists.
      
    :meta public: 
    """
    pass
  
  @abstractmethod
  def _isdir(self, remote_path:str) -> bool:
    """Protected method which checks, whether a remote file is a directory.
    The function is DEPRECATED and will be substituted using stat or lstat.

    Args:
      remote_path: A path of a directory.

    Returns:
      True, if remote file is folder. False, if it isn't a folder. Undefined if the file doesn't exist.

    :meta public: 
    """

    pass
  
  @abstractmethod
  def _mkdir(self, remote_path:str):
    """Protected method which creates a new directory. Behavior is undefined if remote folder already exist, or destination folder doesn't exist.

    Args:
      remote_path: A path of a new remote directory.

    :meta public: 
    """
    pass

  @abstractmethod
  def _rmdir(self, remote_path:str):
    """Protected method which removes an empty remote directory. Behavior is undefined if remote directory doesn't exist or it isn't empty.

    Args:
      remote_path: Path of an empty remote directory to delete.

    :meta public: 
    """   
    pass

  @abstractmethod
  def _unlink(self, remote_path:str):
    """Protected method which removes a nondirectory file. Behavior is undefined if remote file doesn't exist or is a directory.

    Args:
      remote_path: Path of a remote regular file to delete.

    :meta public: 
    """
    pass

  @abstractmethod
  def _exists(self, remote_path:str) -> bool:
    """Protected method which checks, whether a remote file exist. If the remote file is a broken symlink, it returns False.

    Args:
      remote_path: Path of a remote file.

    Returns:
      True, if remote file is exist. False, if remote file doesn't exist

    :meta public: 
    """
    pass

  @abstractmethod
  def _lexists(self, remote_path:str) -> bool:
    """Protected method which checks, whether a remote file exist. If the remote file is a broken symlink, it returns True.
    
    KNOWN BUG: Behavior is undefined in case of broken symlinks. 

    Args:
      remote_path: Path of a remote file.

    Returns:
      True, if remote file is exist. False, if remote file doesn't exist

    :meta public: 
    """
 
    pass

  def exists(self, remote_path:str) -> bool:
    """Method which checks, whether a remote file exist. Returns False for broken symlinks.
    
    Args:
      remote_path: Path of a remote file.

    Returns:
      True, if remote file exists. False, if remote file doesn't exist.

    """

    logging.debug("Does remote file {} exist?".format(remote_path))

    remote_path = path_normalize(remote_path)
    ret = self._exists(remote_path)

    logging.debug("Remote file {} exists: {}".format(remote_path, ret))
    return ret

  def lexists(self, remote_path):
    """Method which checks, whether a remote file exist. Returns True for broken symlinks.
    
    Args:
      remote_path: Path of a remote file.

    Returns:
      True, if remote file exists. False, if remote file doesn't exist.

    """
    logging.debug(f"Does remote file {remote_path} lexist?")

    remote_path = path_normalize(remote_path)
    ret = self._lexists(remote_path)

    logging.debug(f"Remote file {remote_path} lexists: {ret}")
    return ret

  def __check_link_existance(self, remote_path):
    if not self.lexists(remote_path):
      raise FileNotFoundError(f"Remote file {remote_path} not found.")

  def __check_file_existance(self, remote_path):
    self.__check_link_existance(remote_path)

    if not self.exists(remote_path):
      raise FileNotFoundError(f"Remote file {remote_path} is a broken symlink.")


  def __check_file_nonexistance(self, remote_path):
    if self._lexists(remote_path):
      raise InterruptedError(f"Remote destination file {remote_path} exists.")

  def __check_not_folder(self, remote_path):
    self.__check_file_existance(remote_path)

    if self._isdir(remote_path):
      raise IsADirectoryError(f"Remote file {remote_path} is a directory.")

  def __check_potencial_not_folder(self, remote_path):
    if self._lexists(remote_path) and self._isdir(remote_path):
      raise IsADirectoryError("Remote file {} is a directory.".format(remote_path))
  
  def __check_is_folder(self, remote_path):
    self.__check_file_existance(remote_path)

    if not self._isdir(remote_path):
      raise NotADirectoryError(f"Remote file {remote_path} is not a directory.")


  def __check_local_file_existance(self, local_path):
    if not os.path.lexists(local_path):
      raise FileNotFoundError(f"Local file {local_path} not found.")
    
    if not os.path.exists(local_path):
      raise FileNotFoundError(f"Local file {local_path} is a broken symlink.")
    
  def __check_local_file_nonexistance(self, local_path):
    if os.path.lexists(local_path):
      raise InterruptedError(f"Local destination file {local_path} exists.")

  def __check_local_file_not_folder(self, local_path):
    self.__check_local_file_existance(local_path)
    if os.path.isdir(local_path):
      raise IsADirectoryError(f"Local file {local_path} is a directory.")
      
  def __check_local_potencial_file_not_folder(self, local_path):
    if os.path.lexists(local_path) and os.path.isdir(local_path):
      raise IsADirectoryError(f"Local file {local_path} is a directory.")

  def stat(self, remote_path: str) -> p_stat_result:
    """Returns statistics of a file (eg. size, last date modified,...) Follows symlinks to a destination file.
    
    Args:
      remote_path: Path of a remote file.

    Returns:
      An object whose attributes correspond to the attributes of Python’s stat structure as returned by os.stat, except that it contains fewer fields.

    """
    self.__check_file_existance(remote_path)
    return _stat_unpack( self._stat(remote_path) )

  def lstat(self, remote_path: str) -> p_stat_result:
    """Returns statistics of a file (eg. size, last date modified,...)  Doesn't follow symlinks.
    
    Args:
      remote_path: Path of a remote file.

    Returns:
      An object whose attributes correspond to the attributes of Python’s stat structure as returned by os.stat, except that it contains fewer fields.

    """
    self.__check_link_existance(remote_path)
    return _stat_unpack( self._lstat(remote_path) )

  def __encode(self, from_lpath, to_lpath):
    if self.__text_transmission:

      with open(from_lpath, 'rb') as inp, open(to_lpath, 'wb') as out:
        inp = inp.read()
        decoded = codecs.decode(inp, encoding="utf8")

        if self.__remote_crlf:
          decoded = decoded.replace('\n', '\r\n')
        
        bout = codecs.encode(decoded, encoding=self.__remote_encoding)
        out.write(bout)

    else:
      shutil.copyfile(from_lpath, to_lpath)

  def __decode(self, from_lpath, to_lpath):
    if self.__text_transmission:
      with open(from_lpath, 'rb') as inp, open(to_lpath, 'wb') as out:
        binp = inp.read()
        decoded = codecs.decode(binp, encoding=self.__remote_encoding)

        if self.__remote_crlf:
          decoded = decoded.replace('\r\n', '\n')
        
        bout = codecs.encode(decoded, encoding="utf8")
        out.write(bout)
    else:
      shutil.copyfile(from_lpath, to_lpath)

  def __infolder_tmp_file(self, path):
    dirname, basename = os.path.split(path)
    return os.path.join(dirname, '.' + basename + '.tmp' + str(random.randint(10000,65555)))
    

  def push(self, local_path: str, remote_path: str):
    """Uploads/pushes a file from a local storage to a remote storage in the binary form.

    Args:
      local_path: Path of a local file to upload.
      remote_path: Path on the remote storage, where to upload/push a local file.
      
    :meta public: 
    """

    logging.debug(f"Pushing local file {local_path} to the remote file {remote_path}.")

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)
    
    self.__check_local_file_not_folder(local_path)
    self.__check_potencial_not_folder(remote_path)

    with tempfile.NamedTemporaryFile() as _tmp_file:
      tmp_file = _tmp_file.name
    
      self.__encode(local_path, tmp_file)

      tmp_file2 = self.__infolder_tmp_file(remote_path)
      self._push(tmp_file, tmp_file2)
      self.fmv(tmp_file2, remote_path)

    logging.debug(f"Pushing local file {local_path} to the remote file {remote_path} is completed.")

  #recursive push
  def rpush(self, local_path: str, remote_path: str):
    logging.debug(f"Recursive pushing of local file {local_path} to the remote file {remote_path}.")

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)

    self.__check_local_file_existance(local_path)

    if os.path.isdir(local_path):
      if self.lexists(remote_path): 
        if not self.isdir(remote_path):
          raise InterruptedError(f"Cannot upload a folder {local_path} to a non-folder path {remote_path}.")
        else:
          self.mkdir(remote_path)
        
      for l_file in os.listdir(local_path):
        self.rpush(os.path.join(local_path, l_file), os.path.join(remote_path, l_file))
        
    else:
      if self.lexists(remote_path): 
        if self.isdir(remote_path):
          raise InterruptedError(f"Cannot upload a non-folder {local_path} to a folder path {remote_path}")

      self.push(local_path, remote_path)

    logging.debug(f"Recursive pushing of local file {local_path} to the remote file {remote_path} is completed.")


  def pull(self, remote_path: str, local_path: str):
    logging.debug(f"Pulling remote file {remote_path} to the local file {local_path}.")

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)

    self.__check_not_folder(remote_path)
    self.__check_local_potencial_file_not_folder(local_path)

    with tempfile.NamedTemporaryFile() as _tmp_file:
      tmp_file = _tmp_file.name
       
      self._pull(remote_path, tmp_file)

      tmp_file2 = self.__infolder_tmp_file(local_path)
      self.__decode(tmp_file, tmp_file2)

      shutil.move(tmp_file2, local_path)

    logging.debug(f"Pulling remote file {remote_path} to the local file {local_path} is completed.")

  #recursive pull
  def rpull(self, remote_path: str, local_path: str):
    logging.debug(f"Recursive pulling of remote file {remote_path} to the local file {local_path}.")

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)

    self.__check_file_existance(remote_path)
    
    if self.isdir(remote_path):
      if os.path.lexists(local_path):
        if not os.path.isdir(local_path):
          raise InterruptedError(f"Cannot download a folder {remote_path} to a non-folder path {local_path}.")
      else:
        os.mkdir(local_path)
      
      for r_file in self.ls(remote_path):
        self.rpull(os.path.join(remote_path, r_file), os.path.join(local_path, r_file))
        
    else:
      if os.path.lexists(local_path):
        if os.path.isdir(local_path):
          raise InterruptedError(f"Cannot download a non-folder {remote_path} to a folder path {local_path}.")
      
      self.pull(remote_path, local_path)
      
    logging.debug(f"Recursive pulling of remote file {remote_path} to the local file {local_path} is completed.")
  
  def listdir(self, remote_path: str):
    '''
    Public method which returns a list of files in the folder including hidden files. It never returns '.' or '..'.

    Args:
      remote_path: The remote path of a remote folder.

    Returns:
      A list of files in the remote folder.

    '''
    logging.debug(f"Listing file {remote_path}.")

    remote_path = path_normalize(remote_path)
    self.__check_is_folder(remote_path)
    
    raw_list = self._listdir(remote_path)
    
    ret = []
    for el in raw_list:
      if (not el == '.') and (not el == '..'):
        ret.append(el)

    return ret


  def find(self, remote_path: str, child_first: bool = False) -> List[str]:
    '''
    A public method which returns DFS (depth-first search) of remote_path including hidden files. It never returns '.' or '..'.

    Args:
      child_first: If True, childs of a directory will be returned before the directory itself.

    Returns:
      The result of DFS as a list of remote_paths.
    
    '''
    logging.debug(f"Finding (making a tree) of file {remote_path}.")

    remote_path = path_normalize(remote_path)
    self.__check_file_existance(remote_path)

    if self._isdir(remote_path):
      ret = []
      for f in self.xls(remote_path):
        if not child_first:
          ret.append(remote_path)

        ret.extend( dfs_find(self, f) )

        if child_first:
          ret.append(remote_path)
        
    else:
      return [remote_path]

  def mkdir(self, remote_path: str):
    '''
    A public method, which creates a folder. If directory can't be created, because a file already exist, an exception is raised.
    No other directories on path will be created and if any of them is missing, an exception is raised.

    Args:
      remote_path: A path, where to create a new directory.
    '''
    logging.debug(f"Making a directory file {remote_path}.")

    remote_path = path_normalize(remote_path)
    dirname, _ = os.path.split(remote_path)

    self.__check_is_folder(dirname)
    self.__check_file_nonexistance(remote_path)

    self._mkdir(remote_path)

    logging.debug(f"Making a directory file {remote_path} is completed.")

  # Recursive mkdir
  def pmkdir(self, remote_path: str):
    logging.debug(f"Recursive making of a directory file {remote_path}.")

    remote_path = path_normalize(remote_path)

    if self.lexists(remote_path):
      if self.isdir(remote_path):
        return
      else:
        raise InterruptedError(f"File {remote_path} is not a folder.")

    dirname, _ = os.path.split(remote_path)
    self.pmkdir(dirname)
    self.mkdir(remote_path)

    logging.debug(f"Recursive making of a directory file {remote_path} is completed.")
    

  def rmdir(self, remote_path: str):
    logging.debug(f"Removing remote empty directory file {remote_path}.")

    remote_path = path_normalize(remote_path)
    self.__check_is_folder(remote_path)

    if not self.ls(remote_path) == []:
      raise InterruptedError("Remote folder is not empty.")

    self._rmdir(remote_path)

    logging.debug(f"Removing remote empty directory file {remote_path} is completed.")

  def rename(self, old_name: str, new_name: str):
    logging.debug(f"Renaming remote file {old_name} to {new_name}.")

    old_name = path_normalize(old_name)
    new_name = path_normalize(new_name)

    self.__check_file_existance(old_name)
    self.__check_file_nonexistance(new_name)

    self._rename(old_name, new_name)

    logging.debug(f"Renaming remote file {old_name} to {new_name} is completed.")

  # mv one non-dircetory file to a non-directory file
  def fmv(self, old_name: str, new_name: str):
    logging.debug(f"Moving remote non-directory file {old_name} to a remote non-directory file {new_name}.")

    self.__check_not_folder(old_name)
    self.__check_potencial_not_folder(old_name)

    if self.exists(new_name):
      self.rm(new_name)
    
    self.rename(old_name, new_name)

    logging.debug(f"Moving remote non-directory file {old_name} to a remote non-directory file {new_name} is completed.")
  
  # mv to dir
  def dmv(self, old_names: List[str], target_dir: str):
    logging.debug(f"Moving remote file {old_names} inside a remote target directory {target_dir}.")

    old_names = [*map(path_normalize, old_names)]
    target_dir = path_normalize(target_dir)
    
    self.__check_is_folder(target_dir)
    for name in old_names:
      self.__check_file_existance(name)   

    target_dir_ls = self.ls(target_dir)

    for name in old_names:
      dirname, basename = os.path.split(name)
      newname = os.path.join(target_dir, basename)

      if self.isdir(name):
        if basename in target_dir_ls:
          if not self.isdir(newname):
            raise InterruptedError(f"Cannot overwrite remote non-directory {newname} with remote directory {name}.")
          self.dmv(self.xls(name), newname)

        else:
          self.rename(name, newname)          
     
      else:
        if basename in target_dir_ls:
          if self.isdir(newname):
            raise InterruptedError(f"Cannot overwrite remote directory {newname} with remote non-directory {name}.")
        
        self.fmv(name, newname)

    logging.debug(f"Moving remote files {old_names} inside a remote directory {new_name} is completed.")


  def mv(self, old_names: List[str], new_name: str):
    logging.debug(f"Moving remote file {old_names} to a remote destination {new_name}.")

    if self.lexists(new_name) and self.isdir(new_name):
      self.dmv(old_names, new_name)

    else:
      if len(old_names) == 0:
        return
      elif len(old_names) > 1:
        if self.exists(new_name):
          raise InterruptedError(f"Cannot move more than 1 file to non-directory {new_name}.")
        else:
          raise InterruptedError(f"Cannot move more than 1 file to non-existent location {new_name}.")
      else:
        if self.isdir(old_names[0]):
          self.rename(old_names[0], new_name)
        else:
          self.fmv(old_names[0], new_name)

    logging.debug(f"Moving remote file {old_names} to a remote destination {new_name} is completed.")
          

  def fcp(self, old_name: str, new_name: str):
    logging.debug(f"Copying remote non-directory file {old_name} to a remote non-directory file {new_name}.")

    self.__check_not_folder(old_name)
    self.__check_potencial_not_folder(old_name)
    
    with tempfile.NamedTemporaryFile() as _tmp_file:
      tmp_file = _tmp_file.name
      self.pull(old_name, tmp_file)
    
      if self.exists(new_name):
        self.rm(new_name)
      self.push(tmp_file, new_name)

    logging.debug(f"Copying remote non-directory file {old_name} to a remote non-directory file {new_name} is completed.")

  def dcp(self, old_names: List[str], target_dir: str, recursive: bool = False):
    logging.debug(f"Copying remote file {old_names} inside a remote directory {target_dir}. (recursive={recursive})")

    old_names = [*map(path_normalize, old_names)]
    target_dir = path_normalize(target_dir)

    self.__check_is_folder(target_dir)
    for name in old_names:
      if not recursive:
        self.__check_not_folder(name)
      else:
        self.__check_file_existance(name)   
    
    target_dir_ls = self.ls(target_dir)


    for name in old_names:
      dirname, basename = os.path.split(name)
      newname = os.path.join(target_dir, basename)

      logging.debug(f"New name of remote file {name} will be {newname}.")

      if recursive and self.isdir(name):
        if basename in target_dir_ls:
          if not self.isdir(newname):
            raise InterruptedError(f"Cannot overwrite remote non-directory {newname} with remote directory {name}.")

        else:
          self.mkdir(newname)   
       
        self.dcp(self.xls(name), newname)
     
      else:
        if basename in target_dir_ls:
          if self.isdir(newname):
            raise InterruptedError(f"Cannot overwrite remote directory {newname} with remote non-directory {name}.")
        
        self.fcp(name, newname)

    logging.debug(f"Copying remote file {old_names} inside a remote directory {target_dir} is completed. (recursive={recursive})")



  def cp(self, old_names: List[str], new_name: str, recursive: bool = False):
    logging.debug(f"Copying remote files {old_names} to destination {new_name} (recursive={recursive}).")

    if self.exists(new_name) and self.isdir(new_name):
      self.dcp(old_names, new_name, recursive=recursive)

    else:
      if len(old_names) == 0:
        return
      elif len(old_names) > 1:
        if self.exists(new_name):
          raise InterruptedError(f"Cannot copy more than 1 file to non-directory {new_name}.")
        else:
          raise InterruptedError(f"Cannot copy more than 1 file to non-existent location {new_name}.")
      else:
        self.fcp(old_names[0], new_name)

    logging.debug(f"Copying remote files {old_names} to destination {new_name} is completed (recursive={recursive}).")
 
  
  def unlink(self, remote_path: str):
    logging.debug(f"Unlinking remote non-directory file {remote_path}.")     

    remote_path = path_normalize(remote_path)
    self.__check_not_folder(remote_path)

    self._unlink(remote_path)

    logging.debug(f"Unlinking remote non-directory file {remote_path} is completed.")     

  def isdir(self, remote_path: str):
    '''
    A public method, which checks, whether there is an folder on remote_path. If yes, true is returned. Otherwise false.

    Args:
      remote_path: A path, where to check, whether there is an folder.
    '''
    logging.debug(f"Is remote file {remote_path} a directory?")     

    remote_path = path_normalize(remote_path)

    if self.exists(remote_path):
      ret = self._isdir(remote_path)
    else:
      ret = False

    logging.debug(f"Remote file {remote_path} is a directory: {ret}") 
    return ret    

  def rm(self, remote_path: str, recursive: bool = False):
    logging.debug(f"Deleting remote non-directory file {remote_path} (recursive={recursive}).")     

    remote_path = path_normalize(remote_path)
    self.__check_file_existance(remote_path)

    if not recursive:
      self.unlink(remote_path)
    
    else:
      for f in self.find(remote_path, child_first=True):
        if self.isdir(f):
          self.rmdir(f)
        else: 
          self.unlink(f)

    logging.debug(f"Deleting remote non-directory file {remote_path} is completed (recursive={recursive}).")     
       

  def ls(self, remote_path: str):
    logging.debug(f"Listing remote directory file {remote_path}.")     

    remote_path = path_normalize(remote_path)
    self.__check_file_existance(remote_path)
    
    ret = []
    
    if self.isdir(remote_path):
      ret = self.listdir(remote_path)
    else:
      ret = [os.path.basename(remote_path)]

    logging.debug(f"Remote directory file {remote_path} contains {ret}.")
    return ret

  # xls returns list of children with dirname
  def xls(self, remote_path: str):
    remote_path = path_normalize(remote_path)

    def prepend_d(lfile):
      return os.path.join(remote_path, lfile)

    if self.isdir(remote_path):
      return [*map(prepend_d, self.ls(remote_path))]
    else: 
      return [remote_path]

  def touch(self, remote_path: str):
    with tempfile.NamedTemporaryFile() as _tmp_file:
      tmp_file = _tmp_file.name
      self.push(tmp_file, remote_path)    
  
  def __enter__(self):
      return self

  def __exit__(self, exc_type, exc_val, exc_tb):
      self.close()





