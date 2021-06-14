#!/usr/bin/env python3
from rfslib import arg_parser, arg_processor


def get_instance():
  p = arg_parser.one_arg_parser(description='This command list a given remote folder, or returns a file name, if it is not a folder.')
  p.add('-p', '--prepend-dirname', action='store_true', help='Enables prepending dirnames.')
  return arg_processor.init(p, "pls")

with get_instance() as ic:
  if ic.file.remote == False:
    raise ValueError("A given file must be remote.")

  ls = None
  if ic.prepend_dirname:
    ls = ic.connection.xls(ic.file.path)
  else:
    ls = ic.connection.ls(ic.file.path)

  for name in ls:
    print(name)
