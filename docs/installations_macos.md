# Installation notes for Mac users  

## Install Homebrew
Homebrew is a package manager used to install software packages on e.g. MacOS. Follow these [instructions](https://brew.sh/) to install it.

## Install Python 3.12
The bulk-sangerseq tool requires python version 3.12 (most tests were performed using python patch release 3.12.12). Install Python 3.12 using homebrew:  

```
brew install python@3.12
```  
Verify the instalaltion using command:  
```
which python3.12
``` 

### Install pipenv
Pipenv is a virtual environment management tool that can be installed using the following commands. Further details can be found [here](https://pypi.org/project/pipenv/). ```pipenv```will be isntalled via ```pipx```.  

Install ```pipx``` first:  
```
brew install pipx
```  
To ensure it is in your path, use command:
```
pipx ensurepath
```  

Install ```pipenv``` via ```pipx``` using command
```
pipx install pipenv
``` 
**IMPORTANT: Close the terminal and open a new terminal. The changes to your PATH to use ```pipenv``` take only effect when a new terminal session is started.**

### Install Docker
The tool makes use of Docker images for containerization of software applications. An easy way to install Docker is to install [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/). **IMPORTANT: Make sure you select the right installer for your chip (Silicon or Intel).**