# Installing prerequisites

## Install Ubuntu-24.04 via Windows Subsystem for Linux (WSL) on Windows machine
Open ```PowerShell``` by selecting ```Run as administrator```. If running PowerShell as administrator is not permitted, open the ```Windows Command Prompt``` instead by selecting ```Run as administrator```.  
To install WSL and Ubuntu-24.04 on your machine, use the following command: 
```
wsl --install -d Ubuntu-24.04
```   

When completed, you will be prompted to choose a user account and a password.  
**IMPORTANT: Once completed, reboot your computer.**

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

## Install  Visual Studio code [*optional, but recommended*]
Installing Visual Studio (VS) code is not a requirement but it facilitates while working with the tool. VS Code can be downloaded [here](https://code.visualstudio.com/download).