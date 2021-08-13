from rfslib import pglobber, pinstance, path_utils, abstract_pconnection
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

def __init_settings(args):
  settings = abstract_pconnection.p_connection_settings()

  settings.direct_write = args['direct_write']

  settings.local_crlf = args['local_crlf']
  settings.local_encoding = args['local_encoding']

  settings.remote_crlf = args['remote_crlf']
  settings.remote_encoding = args['remote_encoding']

  settings.skip_validation = args['skip_validation']
  settings.text_transmission = args['text_transmission']

  return settings


def __autofill_missing_arguments(args):
  c_type = args["connection_type"]

  def default_nonexistent_arg(name, default):
    if not name in args or args[name] == None:
      logging.debug("No {} is given. Defaulting to {}.".format(name, default))
      args[name] = default
  
  default_nonexistent_arg('text_transmission', False)

  default_nonexistent_arg('local_crlf', False)
  default_nonexistent_arg('remote_crlf', False)

  default_nonexistent_arg('local_encoding', 'UTF8')
  default_nonexistent_arg('remote_encoding', 'UTF8')

  if c_type == 'SMB12':
    default_nonexistent_arg('port', 139)

  elif c_type == 'SMB23':
    default_nonexistent_arg('port', 445)
    default_nonexistent_arg('dfs_domain_controller', None)

  elif c_type == 'SFTP':
    default_nonexistent_arg('port', 22)
    default_nonexistent_arg('password', None)

  elif c_type == 'FTP':
    if args['tls'] == True:
      default_nonexistent_arg('port', 990)
    else:
      default_nonexistent_arg('port', 21)


def __validate_arguments(args):
  c_type = args["connection_type"]

  def check_arg_existence(name):
    if not name in args or args[name] == None:
      error = "Connection type {} needs optional argument {}.".format(c_type, name)
      raise ValueError(error)

  if not c_type == "FS":
    check_arg_existence('host')
    check_arg_existence('username')
 
    if c_type == "SMB12" or c_type == "SMB23":
      check_arg_existence('service_name')

    if not c_type == "SFTP":
      check_arg_existence('password')



def __init_connection(args):
  c_type = args["connection_type"]
  settings = __init_settings(args)

  
  if c_type == "FS":
    logging.debug("Initiating FS (direct file system pseudo) connection.")
    from rfslib import fs_pconnection

    return fs_pconnection.FsPConnection(settings)

  elif c_type == "SFTP":
    logging.debug("Initiating SFTP connection.")
    from rfslib import sftp_pconnection

    return sftp_pconnection.SftpPConnection(settings, 
      host = args['host'], 
      username = args['username'],
      password = args['password'], 
      keyfile = args['keyfile'],
      port = args['port'], 
      no_host_key_checking = args['no_host_key_checking'])

  elif c_type == "SMB12":
    logging.debug("Initiating SMB12 connection.")
    from rfslib import smb12_pconnection

    return smb12_pconnection.Smb12PConnection(settings,
      host = args['host'], 
      service_name = args['service_name'], 
      username = args['username'], 
      password = args['password'],
      port = args['port'], 
      use_direct_tcp = args['use_direct_tcp'],
      use_ntlm_v1 = args['use_ntlm_v1'])

  elif c_type == "SMB23":
    logging.debug("Initiating SMB23 connection.")
    from rfslib import smb23_pconnection

    smb23_pconnection.config_smb23(
      no_dfs = args['no_dfs'],
      disable_secure_negotiate = args['disable_secure_negotiate'],
      dfs_domain_controller = args['dfs_domain_controller'])

    return smb23_pconnection.Smb23PConnection(settings, 
      host = args['host'], 
      service_name = args['service_name'], 
      username = args['username'], 
      password = args['password'],
      port = args['port'], 
      enable_encryption = args['enable_encryption'],
      dont_require_signing = args['dont_require_signing'])

  elif c_type == "FTP":
    logging.debug("Initiating FTP connection.")
    from rfslib import ftp_pconnection
    
    return ftp_pconnection.FtpPConnection(settings, 
      host = args['host'], 
      username = args['username'], 
      password = args['password'],
      port = args['port'], 
      tls = args['tls'], 
      passive_mode = args['passive_mode'],
      connection_encoding=args['connection_encoding'])

  else:
    raise ValueError("Connection type {} is unknown.".format(c_type))

  logging.debug("Connection successfully initiated.")
    

def init(arg_parser, name, vars_to_pass):
  p = arg_parser

  args = vars(p.parse_args())
  ret = pinstance.PInstance()
  
  log_level = logging.WARNING
  if args["debug_mode"] == True:
    log_level = logging.DEBUG

  elif args["verbose"] == True:
    log_level = logging.INFO


  logging_config = {}
  if args['log_file'] is not None:
    logging_config["filename"] = args['log_file']
    logging_config["filemode"] = 'a'
    
    with open(args['log_file'], 'a') as l:
      l.write("\n==================================================\n\n")

  logging.basicConfig(format='%(asctime)s; {}; {}; %(message)s'.format(name, os.getpid()), level=log_level, **logging_config)

  logging.info("Starting rfstools version {}".format(sys.version))
  logging.info( __anonymize_formatted_values(p.format_values()) )
   
  __autofill_missing_arguments(args)
  __validate_arguments(args) 

  logging.debug("Starting stage 1. (connection initialization)")
  ret.connection = __init_connection(args) 

  logging.debug("Starting stage 2. (path processing)")

  def pass_variable(var_name):
    if var_name in args:
      setattr(ret, var_name, args[var_name])

  pass_variable('verbose')

  for var in vars_to_pass:
    pass_variable(var)

  ret.no_host_key_checking = args['no_host_key_checking']
  
  glob = pglobber.PGlobber(ret.connection).glob
  
  def alter_path(path):
    if args["remote_only"] and not path_utils.is_remote(path):
      path = path_utils.add_r_prefix(path)

    if path_utils.is_remote(path):
      path = path_utils.remove_r_prefix(path)
      path = args['remote_prefix'] + path
      path = path_utils.add_r_prefix(path)    

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
    p2_list = map(alter_path, p_list)

    w_list = expand_wildcards(p2_list)
    return [*map(path_utils.GenericPath, w_list)]

  def process_single_path(path):
    p2 = alter_path(path)

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

