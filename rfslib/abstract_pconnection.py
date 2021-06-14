from abc import ABC, abstractmethod

#import pysmb

import tempfile
import os
import os.path
import shutil
import codecs

from rfslib.path_utils import path_normalize

import random

import logging

class PConnection(ABC):
  def __init__(self, **args):
    if 'text_transmission' in args:
      self.__text_transmission = args['text_transmission']
    else:
      self.__text_transmission = False

    if 'remote_encoding' in args:
      self.__remote_encoding = args['remote_encoding']
    else:
      self.__remote_encoding = "UTF8"

    if 'remote_crlf' in args:
      self.__remote_crlf = args['remote_crlf']
    else:
      self.__remote_crlf = False

  @abstractmethod
  def close(self):
    pass

  @abstractmethod
  def _listdir(self, remote_path): 
    pass

  @abstractmethod
  def _rename(self, old_name, new_name):
    pass

  @abstractmethod
  def _push(self, local_path, remote_path):
    pass

  @abstractmethod
  def _pull(self, remote_path, local_path):
    pass
  
  @abstractmethod
  def _isdir(self, remote_path):
    pass
  
  @abstractmethod
  def _mkdir(self, remote_path):
    pass

  @abstractmethod
  def _rmdir(self, remote_path):
    pass

  @abstractmethod
  def _unlink(self, remote_path):
    pass

  @abstractmethod
  def _exists(self, remote_path):
    pass

  @abstractmethod
  def _lexists(self, remote_path):
    pass

  def exists(self, remote_path):
    logging.debug("Does remote file {} exist?".format(remote_path))

    remote_path = path_normalize(remote_path)
    ret = self._exists(remote_path)

    logging.debug("Remote file {} exists: {}".format(remote_path, ret))
    return ret

  def lexists(self, remote_path):
    logging.debug("Does remote file {} lexist?".format(remote_path))

    remote_path = path_normalize(remote_path)
    ret = self._lexists(remote_path)

    logging.debug("Remote file {} lexists: {}".format(remote_path, ret))
    return ret

  def __check_file_existance(self, remote_path):
    if not self.lexists(remote_path):
      raise FileNotFoundError("Remote file {} not found.".format(remote_path))

    if not self.exists(remote_path):
      raise FileNotFoundError("Remote file {} is a broken symlink.".format(remote_path))

  def __check_file_nonexistance(self, remote_path):
    if self._lexists(remote_path):
      raise InterruptedError("Remote destination file {} exists.".format(remote_path))

  def __check_not_folder(self, remote_path):
    self.__check_file_existance(remote_path)

    if self._isdir(remote_path):
      raise IsADirectoryError("Remote file {} is a directory.".format(remote_path))

  def __check_potencial_not_folder(self, remote_path):
    if self._lexists(remote_path) and self._isdir(remote_path):
      raise IsADirectoryError("Remote file {} is a directory.".format(remote_path))
  
  def __check_is_folder(self, remote_path):
    self.__check_file_existance(remote_path)

    if not self._isdir(remote_path):
      raise NotADirectoryError("Remote file {} is not a directory.".format(remote_path))


  def __check_local_file_existance(self, local_path):
    if not os.path.lexists(local_path):
      raise FileNotFoundError("Local file {} not found.".format(local_path))
    
    if not os.path.exists(local_path):
      raise FileNotFoundError("Local file {} is a broken symlink.".format(local_path))
    
  def __check_local_file_nonexistance(self, local_path):
    if os.path.lexists(local_path):
      raise InterruptedError("Local destination file {} exists.".format(local_path))

  def __check_local_file_not_folder(self, local_path):
    self.__check_local_file_existance(local_path)
    if os.path.isdir(local_path):
      raise IsADirectoryError("Local file {} is a directory.".format(local_path))
      
  def __check_local_potencial_file_not_folder(self, local_path):
    if os.path.lexists(local_path) and os.path.isdir(local_path):
      raise IsADirectoryError("Local file {} is a directory.".format(local_path))

  def __encode(self, from_lpath, to_lpath):
    if self.__text_transmission:

      with open(from_lpath, 'rb') as inp, open(to_lpath, 'wbx') as out:
        inp = inp.read()
        decoded = codecs.decode(binp, encoding="utf8")

        if self.__remote_crlf:
          decoded = decoded.replace('\n', '\r\n')
        
        bout = codecs.encode(decoded, encoding=__remote_encoding)
        out.write(bout)

    else:
      shutil.copyfile(from_lpath, to_lpath)

  def __decode(self, from_lpath, to_lpath):
    if self.__text_transmission:
      with open(from_lpath, 'rb') as inp, open(to_lpath, 'wbx') as out:
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
    

  def push(self, local_path, remote_path):
    logging.debug("Pushing local file {} to the remote file {}.".format(local_path, remote_path))

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)
    
    self.__check_local_file_not_folder(local_path)
    self.__check_potencial_not_folder(remote_path)

    _tmp_file = tempfile.NamedTemporaryFile()
    tmp_file = _tmp_file.name
    
    self.__encode(local_path, tmp_file)

    tmp_file2 = self.__infolder_tmp_file(remote_path)
    self._push(tmp_file, tmp_file2)
    self.fmv(tmp_file2, remote_path)

    logging.debug("Pushing local file {} to the remote file {} is completed.".format(local_path, remote_path))

  #recursive push
  def rpush(self, local_path, remote_path):
    logging.debug("Recursive pushing of local file {} to the remote file {}.".format(local_path, remote_path))

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)

    self.__check_local_file_existance(local_path)

    if os.path.isdir(local_path):
      if self.lexists(remote_path): 
        if not self.isdir(remote_path):
          raise InterruptedError("Cannot upload a folder {} to a non-folder path {}".format(local_path, remote_path))
        else:
          self.mkdir(remote_path)
        
      for l_file in os.listdir(local_path):
        self.rpush(os.path.join(local_path, l_file), os.path.join(remote_path, l_file))
        
    else:
      if self.lexists(remote_path): 
        if self.isdir(remote_path):
          raise InterruptedError("Cannot upload a non-folder {} to a folder path {}".format(local_path, remote_path))

      self.push(local_path, remote_path)

    logging.debug("Recursive pushing of local file {} to the remote file {} is completed.".format(local_path, remote_path))


  def pull(self, remote_path, local_path):
    logging.debug("Pulling remote file {} to the local file {}.".format(remote_path, local_path))

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)

    self.__check_not_folder(remote_path)
    self.__check_local_potencial_file_not_folder(local_path)

    _tmp_file = tempfile.NamedTemporaryFile()
    tmp_file = _tmp_file.name
       
    self._pull(remote_path, tmp_file)

    tmp_file2 = self.__infolder_tmp_file(local_path)
    self.__decode(tmp_file, tmp_file2)

    shutil.move(tmp_file2, local_path)

    logging.debug("Pulling remote file {} to the local file {} is completed.".format(remote_path, local_path))

  #recursive pull
  def rpull(self, remote_path, local_path):
    logging.debug("Recursive pulling of remote file {} to the local file {}.".format(remote_path, local_path))

    remote_path = path_normalize(remote_path)
    local_path = path_normalize(local_path)

    self.__check_file_existance(remote_path)
    
    if self.isdir(remote_path):
      if os.path.lexists(local_path):
        if not os.path.isdir(local_path):
          raise InterruptedError("Cannot download a folder {} to a non-folder path {}".format(remote_path, local_path))
      else:
        os.mkdir(local_path)
      
      for r_file in self.ls(remote_path):
        self.rpull(os.path.join(remote_path, r_file), os.path.join(local_path, r_file))
        
    else:
      if os.path.lexists(local_path):
        if os.path.isdir(local_path):
          raise InterruptedError("Cannot download a non-folder {} to a folder path {}".format(remote_path, local_path))
      
      self.pull(remote_path, local_path)
      
    logging.debug("Recursive pulling of remote file {} to the local file {} is completes.".format(remote_path, local_path))
  
  def listdir(self, remote_path):
    logging.debug("Listing file {}.".format(remote_path))

    remote_path = path_normalize(remote_path)
    self.__check_is_folder(remote_path)
    
    return self._listdir(remote_path)


  def find(self, remote_path, child_first=False):
    logging.debug("Finding (making a tree) of file {}.".format(remote_path))

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

  def mkdir(self, remote_path):
    logging.debug("Making a directory file {}.".format(remote_path))

    remote_path = path_normalize(remote_path)
    Rself.__check_file_nonexistance(remote_path)

    self._mkdir(remote_path)

    logging.debug("Making a directory file {} is completed.".format(remote_path))

  # Recursive mkdir
  def pmkdir(self, remote_path):
    logging.debug("Recursive making of a directory file {}.".format(remote_path))

    remote_path = path_normalize(remote_path)

    if self.lexists(remote_path):
      if self.isdir(remote_path):
        return
      else:
        raise InterruptedError("File {} is not a folder.".format(remote_path))

    dirname, basename = os.path.split(remote_path)
    self.pmkdir(dirname)
    self.mkdir(remote_path)

    logging.debug("Recursive making of a directory file {} is completed.".format(remote_path))
    

  def rmdir(self, remote_path):
    logging.debug("Removing remote empty directory file {}.".format(remote_path))

    remote_path = path_normalize(remote_path)
    self.__check_is_folder(remote_path)

    if not self.ls(remote_path) == []:
      raise InterruptedError("Remote folder is not empty.")

    self._rmdir(remote_path)

    logging.debug("Removing remote empty directory file {} is completed".format(remote_path))

  def rename(self, old_name, new_name):
    logging.debug("Renaming remote file {} to {}.".format(old_name, new_name))

    old_name = path_normalize(old_name)
    new_name = path_normalize(new_name)

    self.__check_file_existance(old_name)
    self.__check_file_nonexistance(new_name)

    self._rename(old_name, new_name)

    logging.debug("Renaming remote file {} to {} is completed.".format(old_name, new_name))

  # mv one non-dircetory file to a non-directory file
  def fmv(self, old_name, new_name):
    logging.debug("Moving remote non-directory file {} to a remote non-directory file {}.".format(old_name, new_name))

    self.__check_not_folder(old_name)
    self.__check_potencial_not_folder(old_name)

    if self.exists(new_name):
      self.rm(new_name)
    
    self.rename(old_name, new_name)

    logging.debug("Moving remote non-directory file {} to a remote non-directory file {} is completed.".format(old_name, new_name))
  
  # mv to dir
  def dmv(self, old_names, target_dir):
    logging.debug("Moving remote file {} inside a remote directory {}.".format(old_name, new_name))

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
            raise InterruptedError("Cannot overwrite remote non-directory {} with remote directory {}.".format(newname, name))
          self.dmv(self.xls(name), newname)

        else:
          self.rename(name, newname)          
     
      else:
        if basename in target_dir_ls:
          if self.isdir(newname):
            raise InterruptedError("Cannot overwrite remote directory {} with remote non-directory {}.".format(newname, name))
        
        self.fmv(name, newname)

    logging.debug("Moving remote file {} inside a remote directory {} is completed.".format(old_name, new_name))


  def mv(self, old_names, new_name):
    logging.debug("Moving remote file {} to a remote destination {}.".format(old_name, new_name))

    if self.lexists(new_name) and self.isdir(new_name):
      self.dmv(old_names, new_name)

    else:
      if len(old_names) == 0:
        return
      elif len(old_names) > 1:
        if self.exists(new_name):
          raise InterruptedError("Cannot move more than 1 file to non-directory {}.".format(new_name))
        else:
          raise InterruptedError("Cannot move more than 1 file to non-existent location {}.".format(new_name))
      else:
        self.fmv(old_names[0], new_name)

    logging.debug("Moving remote file {} to a remote destination {} is completed.".format(old_name, new_name))
          

  def fcp(self, old_name, new_name):
    logging.debug("Copying remote non-directory file {} to a remote non-directory file {}.".format(old_name, new_name))

    self.__check_not_folder(old_name)
    self.__check_potencial_not_folder(old_name)
    
    _tmp_file = tempfile.NamedTemporaryFile()
    tmp_file = _tmp_file.name
    self.pull(old_name, tmp_file)
    
    if self.exists(new_name):
      self.rm(new_name)
    self.push(tmp_file, new_name)

    logging.debug("Copying remote non-directory file {} to a remote non-directory file {} is completed.".format(old_name, new_name))

  def dcp(self, old_names, target_dir, recursive=False):
    logging.debug("Copying remote file {} inside a remote directory {}. (recursive={})".format(old_names, target_dir, recursive))

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

      logging.debug("New name of remote file {} will be {}.".format(name, newname))

      if recursive and self.isdir(name):
        if basename in target_dir_ls:
          if not self.isdir(newname):
            raise InterruptedError("Cannot overwrite remote non-directory {} with remote directory {}.".format(newname, name))

        else:
          self.mkdir(newname)   
       
        self.dcp(self.xls(name), newname)
     
      else:
        if basename in target_dir_ls:
          if self.isdir(newname):
            raise InterruptedError("Cannot overwrite remote directory {} with remote non-directory {}.".format(newname, name))
        
        self.fcp(name, newname)

    logging.debug("Copying remote file {} inside a remote directory {} is completed. (recursive={})".format(old_names, target_dir, recursive))



  def cp(self, old_names, new_name, recursive=False):
    logging.debug("Copying remote files {} to destination {} (recursive={}).".format(old_names, new_name, recursive))

    if self.exists(new_name) and self.isdir(new_name):
      self.dcp(old_names, new_name, recursive=recursive)

    else:
      if len(old_names) == 0:
        return
      elif len(old_names) > 1:
        if self.exists(new_name):
          raise InterruptedError("Cannot copy more than 1 file to non-directory {}.".format(new_name))
        else:
          raise InterruptedError("Cannot copy more than 1 file to non-existent location {}.".format(new_name))
      else:
        self.fcp(old_names[0], new_name)

    logging.debug("Copying remote files {} to destination {} is completed (recursive={}).".format(old_names, new_name, recursive))
 
  
  def unlink(self, remote_path):
    logging.debug("Unlinking remote non-directory file {}".format(remote_path))     

    remote_path = path_normalize(remote_path)
    self.__check_not_folder(remote_path)

    self._unlink(remote_path)

    logging.debug("Unlinking remote non-directory file {} is completed".format(remote_path))     

  def isdir(self, remote_path):
    logging.debug("Is remote file {} a directory?".format(remote_path))     

    remote_path = path_normalize(remote_path)
    self.__check_file_existance(remote_path)

    ret = self._isdir(remote_path)
    logging.debug("Remote file {} is a directory: {}".format(remote_path, ret)) 

    return ret    

  def rm(self, remote_path, recursive=False):
    logging.debug("Deleting remote non-directory file {} (recursive={})".format(remote_path, recursive))     

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

    logging.debug("Deleting remote non-directory file {} is completed (recursive={})".format(remote_path, recursive))     
       

  def ls(self, remote_path):
    logging.debug("Listing remote directory file {}".format(remote_path))     

    remote_path = path_normalize(remote_path)
    self.__check_file_existance(remote_path)
    
    ret = []
    
    if self.isdir(remote_path):
      ret = self.listdir(remote_path)
    else:
      ret = [os.path.basename(remote_path)]

    logging.debug("Remote directory file {} contains {}.".format(remote_path, ret))
    return ret

  # xls returns list of children with dirname
  def xls(self, remote_path):
    remote_path = path_normalize(remote_path)

    def prepend_d(lfile):
      return os.path.join(remote_path, lfile)

    if self.isdir(remote_path):
      return map(prepend_d, self.ls(remote_path))
    else: 
      return [remote_path]
  
  def __enter__(self):
      return self

  def __exit__(self, exc_type, exc_val, exc_tb):
      self.close()




