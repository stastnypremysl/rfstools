class pconnection_settings():
  '''This object represents settings appliable for all PConnection instances (instances of class, which inherits from PConnection).'''
  def __init__(self):
    '''The constructor inicializes the class to default values.'''
    pass
  
  text_transmission:bool = False
  '''If true, all files, which will be transmitted, will be recoded from local_encoding to remote_encoding and from local_crlf to remote_crlf. If False, there will be no encoding done during transmission.'''

  local_encoding:str = 'UTF8'
  '''The encoding of local text files. (eg. 'UTF8')'''
  remote_encoding:str = 'UTF8'
  '''The encoding of remote text files. (eg. 'cp1250')'''

  local_crlf:bool = False
  '''Does local files use CRLF? If True, it is supposed, they do. If False, it is supposed, they use LF.'''
  remote_crlf:bool = False
  '''Does remote files use CRLF? If True, it is supposed, they do. If False, it is supposed, they use LF.'''

  direct_write:bool = False
  '''NOT IMPLEMENTED YET. If True, push will write output directly to file. If False all push operations on regular files will create firstly tmp file in target folder and then move result to file.'''

  skip_validation:bool = False
  '''NOT IMPLEMENTED YED. If True, all validations of input will be skipped. Undefined behavior may happen if input is wrong. Increses performance.'''

  default_fmask:int = 0o0133
  '''If mode (permissions) of a nondirectory file can't be fetched, this value will be used instead of it.'''
  default_dmask:int = 0o0022
  '''If mode (permissions) of a directory can't be fetched, this value will be used instead of it.'''


