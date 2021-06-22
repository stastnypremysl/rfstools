import configargparse
from os.path import expanduser
from os import environ

import sys


def default_arg_parser(description:str='') -> configargparse.ArgParser:
  """A function, which is called in the beginning of all scripts in `bin`. 
     It generates a base parser sceleton, which is later altered by script itself.

     Args:
       description: The script description. Basically what the script do.

     Returns:
       A base parser sceleton. 
  """

  ret = configargparse.ArgParser(description=description, default_config_files=['/etc/rfstools.conf', '~/.rfstools.conf'])
  ret.add('-c', '--config-file', is_config_file=True, help='Configuration file path.', env_var='RFSTOOLS_CONFIG')

  ret.add('-U', '--username', help='Username, which is used to connect the file storage.', env_var='RFSTOOLS_USERNAME')
  ret.add('-W', '--password', help='Password, which is used to connect the file storage.', env_var='RFSTOOLS_PASSWORD')
  ret.add('-K', '--keyfile', help='A keyfile, which is used to connect the file storage. Not used if password is given. Defaults to ~/.ssh/id_rsa . Applicable only for SFTP.',
          default=expanduser("~/.ssh/id_rsa"), env_var='RFSTOOLS_KEYFILE')

  ret.add('-H', '--host', help='The address of server.', env_var='RFSTOOLS_HOST')
  ret.add('-P', '--port', help='The port for a connection to the file storage. Defaults to RFC standard port.', env_var='RFSTOOLS_PORT', type=int)
  ret.add('-T', '--connection-type', help='A connection type to the file storage. (SMB12/SMB23/SFTP/FTP/FS/FTPS) SMB12 is samba version 1 or 2 and SMB23 is samba version 2 or 3.', 
          env_var='RFSTOOLS_CONNECTION_TYPE', required=True)

  ret.add('-S', '--service-name', help='Contains a name of shared folder. Applicable only for SMB12/SMB23.', env_var='RFSTOOLS_SERVICE_NAME')
  ret.add('--client-name', help='Overrides a default RFSTOOLS client name. Applicable only for SMB12/SMB23.', env_var='RFSTOOLS_CLIENT_NAME', default='RFSTOOLS')

  ret.add('--use-ntlm-v1', help='Enables deprecated ntlm-v1 authentication. Applicable only for SMB12.', action='store_true', env_var="RFSTOOLS_USE_NTLM_V1")
  ret.add('--use-direct-tcp', help='Enables newer direct TCP connection over NetBIOS connection. Applicable only for SMB12. (don\'t forget to change port to 445)', 
          env_var="RFSTOOLS_USE_DIRECT_TCP", action='store_true')

  ret.add('--enable-encryption', help='Enables encryption for a SMB3 connection. Applicable only for SMB23.', action='store_true', env_var='RFSTOOLS_ENABLE_ENCRYPTION')
  ret.add('--disable-secure-negotiate', help='Disables secure negotiate requirement for a SMB connection. Applicable only for SMB23.', 
          action='store_true', env_var='RFSTOOLS_DISABLE_SECURE_NEGOTIATE')
  ret.add('--no-dfs', help='Disables DFS support - useful as a bug fix. Applicable only for SMB23.', action='store_true', env_var='RFSTOOLS_NO_DFS')
  ret.add('--dfs-domain-controller', help='The DFS domain controller address. Useful in case, when rfstools fails to find it themself. Applicable only for SMB23',
          env_var='RFSTOOLS_DFS_DOMAIN_CONTROLLER')

  ret.add('-Z', '--remote-prefix', help='Contains a prefix, which will be prepended to all remote addresses.', env_var='RFSTOOLS_REMOTE_PREFIX', default='')
  ret.add('-x', '--transaction', help='Specifies the name of transaction in which the command should be executed. Not implemented yet.', env_var='RFSTOOLS_TRANSACTION')

  ret.add('-v', '--verbose', help='Enables verbose mode.', action='store_true', env_var='RFSTOOLS_VERBOSE')
  ret.add('-D', '--debug-mode', help='Enables debug mode. Implies verbose mode.', action='store_true', env_var='RFSTOOLS_DEBUG')
  ret.add('-L', '--log-file', help='Redirect all log messages to a file.', env_var='RFSTOOLS_LOG_FILE')

  ret.add('--no-host-key-checking', env_var='RFSTOOLS_NO_HOST_KEY_CHECKING', action='store_true', default=False,
          help='Disables host SSH key knowledge requirements policy. Be aware, that using this option makes you volnerable to MITM attack. Applicable only for SFTP.')

  return ret

def oneplus_arg_parser(description:str=''): -> configargparse.ArgParser:
  ret = default_arg_parser(description=description)
  ret.add('files', nargs="+", help='File(s) to process. It may contain wildcards. Files must start with prefix r: - no other files than remote are supported.', metavar='FILE(S)')
    
  return ret


def one_arg_parser(description:str=''): -> configargparse.ArgParser:
  ret = default_arg_parser(description=description)
  ret.add('file', help='File to process. File must start with prefix r: - no other file than remote is supported.', metavar='FILE')

  return ret

def many_to_one_arg_parser(description:str=''): -> configargparse.ArgParser:
  ret = default_arg_parser(description=description)
  ret.add('source_files', nargs="+", help='Source file(s) to transmit. It may contain wildcards. Remote file(s) must start with prefix r:', metavar='SOURCE_FILE')

  ret.add('-t', '--target-folder', help='If target folder is specified, it will be used instead of DESTINATION FILE. DESTINATION FILE positional argument will be no longer parsed if used.', 
    env_var='RFSTOOLS_TARGET_FOLDER')

  if not('-t' in sys.argv or '--target-folder' in sys.argv) and (not 'RFSTOOLS_TARGET_FOLDER' in environ or environ['RFSTOOLS_TARGET_FOLDER']==""):
    ret.add('destination_file',  
          help='Destination file to be transmited to. If there is more than one source file, the destination file must be a folder. Remote file must start with prefix r:',
          metavar='DESTINATION_FILE')

  ret.add('-X', '--text-transmission', action='store_true', env_var="RFSTOOLS_TEXT_TRANSMISSION",
          help='Enable text transmission transformations to/from UTF8 and LF. ' +
               'Local files will be using this option always transformated to/from UTF8 and LF from/to remote encoding and remote line terminators. ' +
               'BE SURE NOT TO TRANSMIT BINARY DATA WITH THIS OPTION.')

  ret.add('-C', '--remote-crlf', action='store_true', help='Remote target uses CRLF instead of LF', env_var="RFSTOOLS_REMOTE_CRLF")
  ret.add('-E', '--remote-encoding', default='UTF8', help='The encoding of the remote target (eg. UTF8, UTF16). Defaults to UTF8. ', env_var="RFSTOOLS_REMOTE_ENCODING")

  return ret


