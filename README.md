# rfstools
Remote file system tools for data manipulation between remote /and local host/ (cp, mv, ls, rm,..) written in Python3. 
This package provides you executables `pcp`, `pls`, `pmv`,..., which enables you to do painless data operations on remote/between remote and local host using SFTP/FTP/FTPS/SMB/FS(local file system) protocols.

Furthermore you can enable data reencoding during data transfer (CRLF/LF and character reencoding). 

In future, it should be possible to do atomical transaction transfers between many hosts so you are sure, that after failure (eg. connection loss), no change is made on any host.

## Examples
TODO

## Installation
We recommend, that you upgrade your pip version before doing any further step.

    pip3 install -U pip

    # If there is no pip3
    pip install -U pip3       

Be sure, that your `pip` installation folder/bin is correctly in your `PATH` enviroment variable. 
For example, if you are on Debian and you are not installing under root, you have `~/.local/bin` in $PATH.
If it is not present, you will not able to call `rfstools` from command line.

Packages `rfslib` and `rfstools` are private and therefore it is needed, that you add extra indexes to `pip` configuration.
For example this can be done by adding TODO

Be aware, that if private pypi repository on Gitlab doesn't work correctly, the useless dummy public version of this package (squatting-attack prevension) might be downloaded.

### From wheel
TODO
### From wheelhouse
TODO

## Configuration
TODO

## Documentation
TODO

## TODO
* Transactions 

