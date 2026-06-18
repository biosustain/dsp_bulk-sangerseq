# Installing prerequisites

## Install Ubuntu via Windows Subsystems for Linux (WSL) on Windows machine
Open PowerShell by ```Run as administrator```. To install WSL on your machine, use the following command: 
```
wsl --install
```  
When completed, reboot your computer. Installing WSL does not install a specific Linux distribution yet.  
A list of available Linux distributions is available by executing the following command in Powershell (```Run as administrator```):  
```
wsl --list --online
```  
Install the desired version using command by replacing ```<distribution name>``` with the desired Ubuntu release name 
```
wsl --install -d <distribution name>
```  

For example, all initial tests of the bulk-sangerseq tool were conducted using ```Ubuntu 22.04.5 LTS``` which can be installed using command  
```
wsl --install -d Ubuntu-24.04
```  
When completed, you will be prompted to choose a default Unix user account and a password.  

For further details, please refer to these [instructions](https://learn.microsoft.com/en-gb/windows/wsl/install).  


To open the Ubuntu terminal, right-click on the PowerShell icon and select ```Ubuntu-<distribution name>```.  
The installed Ubuntu version can be checked using command  
```
lsb_release -a
```

## Create GitHub account and install git
[Create a GitHub account](https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home) or sign in to your existing account.  
Check if git is already installed on your system by typing into your terminal 
```
git version
```
If not already installed on your computer, follow the [installation instructions](https://github.com/git-guides/install-git) in section "Install Git on Linux".

## Install  Visual Studio code [*optional*]
Installing Visual Studio (VS) code is not a requirement but it facilitates while working with the tool. VS Code can be downloaded [here](https://code.visualstudio.com/download).