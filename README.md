# rfstools
Remote file system tools for data manipulation between remote /and local host/ (cp, mv, ls, rm,..) written in Python3. 
This package provides you executables pcp, pls, pmv,..., which enables you to do painless data operations on remote/between remote and local host using SFTP/FTP/FTPS/SMB/FS(local file system) protocols.

Furthermore you can enable data reencoding during data transfer (CRLF/LF and character reencoding). 

In future, it should be possible to do atomical transaction transfers between many hosts so you are sure, that after failure (eg. connection loss), no change is made on any host.

## Examples
TODO

## Installation
### From source code - nonstrict dependencies
If you want to install this package without strict package dependencies or you just want to develop it, this aproach should be good for you.

In this approach you have to install these private dependencies manually: https://git.profinit.eu/rfs/rfslib

After that download the repository (if you want a concrete version, you have to change the address to it), cd it:

    git clone https://git.profinit.eu/rfs/rfstools
    cd rfstools

and install it by using pip3 or ./setup.py

    pip3 install .

### From source code - strict dependencies
This tool is tested on a given version of dependencies and you might consider to use them strictly because you are guaranted, that they passed the CI/CD tests.

In this approach you don't have to install private dependencies manually, but you have to have git and access to git repository.

Analogically as in section before, we need to download it and cd it:

    git clone https://git.profinit.eu/rfs/rfstools
    cd rfstools

and install it using pip3

    pip3 install . -r requirements.txt


### From wheel
TODO
### From wheelhouse
TODO

## Configuration

## Documentation
TODO

## TODO
* Transactions 

