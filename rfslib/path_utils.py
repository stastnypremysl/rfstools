import re
import os, os.path
import shutil

import logging


__remote_path_re = re.compile(r'^r:')

def is_remote(path):
  return __remote_path_re.match(path) is not None

def remove_r_prefix(path):
  return __remote_path_re.sub('', path)

def add_r_prefix(path):
  return 'r:' + path

__p_normalize_re1 = re.compile(r'\\')
__p_normalize_re2 = re.compile(r'/$')

def path_normalize(path):
  path = __p_normalize_re1.sub('/', path)
  path = __p_normalize_re2.sub('', path)
  return path

def generic_path_normalize(path):
  path.path = path_normalize(path.path)
  return path
  

class GenericPath():

  def __init__(self, path):
    if is_remote(path):
      self.remote = True
      self.path = remove_r_prefix(path)

    else:
      self.remote = False
      self.path = path

def _split_list_local_remote(gpaths):
  local = []
  remote = []

  for p in gpaths:
    if p.remote:
      remote.append(p.path)
    else:
      local.append(p.path)

  return (local, remote)

def generic_cp(conn, sources, dest, recursive=False):
  logging.debug("Starting generic_cp. (recursive={})".format(recursive))

  sources = map(generic_path_normalize, sources)
  dest = generic_path_normalize(dest)

  local_src_paths, remote_src_paths = _split_list_local_remote(sources)
  
  push, pull, lcopy = None, None, None
  if recursive:
    push = conn.rpush
    pull = conn.rpull

    lcopy = shutil.copytree
  else:
    push = conn.push
    pull = conn.pull
    
    lcopy = shutil.copy

  if dest.remote:
    dest_dir = conn.lexists(dest.path) and conn.isdir(dest.path)
    logging.debug("generic_cp: Destination {} is remote. It is a folder: {}".format(dest.path, dest_dir))

    logging.debug("generic_cp: Dealing with remote files. ")
    conn.cp(remote_src_paths, dest.path, recursive=recursive)

    logging.debug("generic_cp: Dealing with local files. ")
    for l_file in local_src_paths:
      if dest_dir:
        l_dirname, l_basename = os.path.split(l_file)
        push(l_file, os.path.join(dest.path, l_basename))
      else:
        push(l_file, dest.path)
    
  else:
    dest_dir = os.path.lexists(dest.path) and os.path.isdir(dest.path)
    logging.debug("generic_cp: Destination {} is local. It is a folder: {}".format(dest.path, dest_dir))
    
    logging.debug("generic_cp: Dealing with local files. ")
    for l_file in local_src_paths:

      logging.debug("generic_cp, local: Coping {}.".format(l_file) )
      if dest_dir:
        l_dirname, l_basename = os.path.split(l_file)
        lcopy(l_file, os.path.join(dest.path, l_basename))
      else:
        lcopy(l_file, dest.path)

    logging.debug("generic_cp: Dealing with remote files. ")
    for r_file in remote_src_paths:
      if dest_dir:
        r_dirname, r_basename = os.path.split(r_file)
        pull(r_file, os.path.join(dest.path, r_basename))
      else:
        pull(r_file, dest.path)

  logging.debug("generic_cp: done")
    

def generic_mv(conn, sources, dest):
  logging.debug("Starting generic_mv. (recursive={})".format(recursive))

  sources = map(generic_path_normalize, sources)
  dest = generic_path_normalize(dest)
    
  local_src_paths, remote_src_paths = _split_list_local_remote(sources)

  if dest.remote:
    dest_dir = conn.lexists(dest.path) and conn.isdir(dest.path)
    logging.debug("generic_mv: Destination {} is remote. It is a folder: {}".format(dest.path, dest_dir))

    logging.debug("generic_mv: Dealing with remote files. ")
    conn.mv(remote_src_paths, dest.path, recursive=recursive)

    logging.debug("generic_mv: Dealing with local files. ")
    for l_file in local_src_paths:

      if dest_dir:
        l_dirname, l_basename = os.path.split(l_file)
        conn.rpush(l_file, os.path.join(dest.path, l_basename))
      else:
        conn.rpush(l_file, dest.path)
    
  else:
    dest_dir = os.path.lexists(dest.path) and os.path.isdir(dest.path)
    logging.debug("generic_mv: Destination {} is local. It is a folder: {}".format(dest.path, dest_dir))
    
    logging.debug("generic_mv: Dealing with local files. ")
    for l_file in local_src_path:
      logging.debug("generic_mv, local: Moving {}.".format(l_file) )

      if dest_dir:
        l_dirname, l_basename = os.path.split(l_file)
        shutil.move(l_file, os.path.join(dest.path, l_basename))
      else:
        shutil.move(l_file, dest.path)

    logging.debug("generic_mv: Dealing with remote files. ")
    for r_file in remote_src_path:
      if dest_dir:
        r_dirname, r_basename = os.path.split(r_file)
        conn.rpull(l_file, os.path.join(dest.path, l_basename))
      else:
        conn.rpull(l_file, dest.path)
      
      conn.rmtree(r_file)
  
  logging.debug("generic_mv: done")
   

