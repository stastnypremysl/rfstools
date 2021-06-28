from rfslib import pglobber, pinstance, path_utils
import logging

import os, sys

import re

def __anonymize_formatted_values(values):
  head, *tail = values.splitlines()
  head = re.sub(r"-W(\s*)\S+", r"-W\1******", head)
  head = re.sub(r"--password(\s+)\S+", r"--password\1******", head)

  ret = []
  ret.append(head)
  ret.append("\n")

  t_regex = re.compile(r"(.*password.*:\s*).*", flags=re.IGNORECASE)

  for l in tail:
    ret.append(t_regex.sub(r"\1******", l))
    ret.append("\n")

  return "".join(ret)
    

def init(arg_parser, name, vars_to_pass):
  p = arg_parser

  args = vars(p.parse_args())
  ret = pinstance.PInstance()
  
  log_level = logging.WARNING
  if args["debug_mode"] == True:
    log_level = logging.DEBUG

  elif args["verbose"] == True:
    log_level = logging.INFO

  logging.basicConfig(format='%(asctime)s; {}; {}; %(message)s'.format(name, os.getpid()), level=log_level)

  logging.info("Starting rfstools version {}".format(sys.version))
  logging.info( __anonymize_formatted_values(p.format_values()) )
   
  logging.debug("Starting stage 1. (connection initialization)")

  c_type = args["connection_type"]

  def check_arg_existence(name):
    if not name in args or args[name] == None:
      error = "Connection type {} needs optional argument {}.".format(c_type, name)
      raise ValueError(error)
  
  def default_nonexistent_arg(name, default):
    if not name in args or args[name] == None:
      logging.debug("No {} is given. Defaulting to {}.".format(name, default))
      args[name] = default

  if not c_type == "FS":
    check_arg_existence('host')
    check_arg_existence('username')

    if not c_type == "SFTP":
      check_arg_existence('password')
 
  
  if c_type == "FS":
    logging.debug("Initiating FS (direct file system pseudo) connection.")
    from rfslib import fs_pconnection

    ret.connection = fs_pconnection.FsPConnection(**args)

  elif c_type == "SFTP":
    logging.debug("Initiating SFTP connection.")
    from rfslib import sftp_pconnection

    default_nonexistent_arg('port', 22)
    ret.connection = sftp_pconnection.SftpPConnection(**args)

  elif c_type == "SMB12":
    logging.debug("Initiating SMB12 connection.")
    from rfslib import smb12_pconnection

    check_arg_existence('service_name')
    default_nonexistent_arg('port', 139)
    ret.connection = smb12_pconnection.Smb12PConnection(**args)

  elif c_type == "SMB23":
    logging.debug("Initiating SMB23 connection.")
    from rfslib import smb23_pconnection

    check_arg_existence('service_name')
    default_nonexistent_arg('port', 445)

    smb23_pconnection.config_smb23(**args)
    ret.connection = smb23_pconnection.Smb23PConnection(**args)

  elif c_type == "FTP":
    logging.debug("Initiating FTP connection.")
    from rfslib import ftp_pconnection

    default_nonexistent_arg('port', 21)
    ret.connection = ftp_pconnection.FtpPConnection(**args)

  elif c_type == "FTPS":
    logging.debug("Initiating FTPS connection.")
    from rfslib import ftp_pconnection

    default_nonexistent_arg('port', 990)
    ret.connection = ftp_pconnection.FtpPConnection(tls=True, **args)

  else:
    raise ValueError("Connection type {} is unknown.".format(c_type))

  logging.debug("Connection successfully initiated.")

  logging.debug("Starting stage 2. (path processing)")

  def pass_variable(var_name):
    if var_name in args:
      setattr(ret, var_name, args[var_name])

  pass_variable('verbose')

  for var in vars_to_pass:
    pass_variable(var)


  ret.no_host_key_checking = args['no_host_key_checking']
  
  glob = pglobber.PGlobber(ret.connection).glob
  
  def add_remote_prefix(path):
    if path_utils.is_remote(path):
      path = path_utils.remove_r_prefix(path)
      path = args['remote_prefix'] + path
      path = path_utils.add_r_prefix(path)

      return path

    else:
      return path
  
  def expand_wildcards(i_list):
    logging.debug("Expanding wildcards...")

    o_list = []
    for wpath in i_list:

      if path_utils.is_remote(wpath):
        wpath = path_utils.remove_r_prefix(wpath)

        expanded = glob(wpath)
        expanded = map(path_utils.add_r_prefix, expanded)

        o_list.extend(expanded)
       
      else:
        o_list.append(wpath)

    return o_list
  
  def process_paths(p_list):
    p2_list = map(add_remote_prefix, p_list)

    w_list = expand_wildcards(p2_list)
    return [*map(path_utils.GenericPath, w_list)]

  def process_single_path(path):
    p2 = add_remote_prefix(path)

    return path_utils.GenericPath(path)
  
  if 'source_files' in args:
    ret.source_files = process_paths(args['source_files'])

  if 'files' in args:
    ret.files = process_paths(args['files'])

  if 'target_file' in args:
    ret.destination_file = process_single_path(args['target_file'])
  elif 'destination_file' in args:
    ret.destination_file = process_single_path(args['destination_file'])

  if 'file' in args:
    ret.file = process_single_path(args['file'])

  logging.debug("Stage 2 done.")
  logging.debug("Starting stage 3. (file operations)")

  return ret

