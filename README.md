# Sanger sequencing tool for bulk analysis
The manual evaluation of Sanger sequencing results from medium- to high throughput experiments is time-consuming. This bulk Sanger sequencing tool was developed to reduce the the time investment while keeping a high quality of results evaluation. The tool uses established software that is specifically arranged to handle Sanger sequencing data in bulk. At its core, [tracy](https://github.com/gear-genomics/tracy) is used for the analysis of Sanger sequencing data ([Rausch et al, 2020](https://doi.org/10.1186/s12864-020-6635-8)).

## Prerequisites

### Github account and git
[Create a github account](https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home) or sign in to your existing account.  
Check if git is already installed on your system by typing into your terminal ```git version```. If not already installed on your computer, you can follow the installation instructions [here](https://github.com/git-guides/install-git).

### Install all prerequisites

#### Python 3.7 or higher
You can install the latest Python 3.x version by following the instructions [here](https://www.python.org/downloads/).  
Add Python 3.x to your system's PATH.


#### pipenv
Pipenv is a virtual environment management tool that requires Python version 3.7 or higher. You can install it from the command line using ```pip install --user pipenv```. Further details can be found [here](https://pypi.org/project/pipenv/).  
Add pipenv to your system's PATH.


#### Docker
The tool makes use of Docker images for containerization of software applications. Follow the installation instructions [here](https://docs.docker.com/engine/install/). Alternatively, you can install the Docker engine via [Docker Desktop](https://docs.docker.com/desktop/).

#### Visual Studio code [*optional*]
Installing Visual Studio (VS) code is not a requirement but it facilitates while working with the tool. VS Code can be dowloaded [here](https://code.visualstudio.com/download).

## Installation of dsp_bulk_sangerseq
***Add details here incl. env creation***
Open the terminal and perform the following steps consecutively:
1. Change to the desired directory using ```cd </absolute/path/to/project/folder>```.
2. Clone the github repository using ```git clone https://github.com/biosustain/dsp_bulk-sangerseq.git```.
3. Change to the project directory using ```cd </dsp_bulk-sangerseq>```.
4. Install all dependencies from the Pipfile.lock using ```pipenv sync```.

## Usage

**Data preparation**
Input data requirements: .ab1 sdequencing and reference .fasta files.
Copy all .ab1 files into the folder **data**

**Modify the configuration file (config.yaml)**
Change the data_host variable to become the absolute path to the data directory on your computer.
Change the outdir_host variable to become the absolute path to the outdir directory on your computer.
In general, the use of absolute paths is recommmended but relative paths can be used too.

**Start the Docker engine**
- On MacOS and Windows, start Docker desktop.
- On Linux: command goes here

**Run scripts of dsp_sangerseq consecutively**  
1. In the project directory, activate the environment using ```pipenv shell```. ALternatively, activate the environment from within the code editor, e.g. VS code.
2. Perform Sanger sequencing analysis using tracy by running command ```python tracy_bulk_docker.py```.
3. Once finished, perform post-processing of results by running command ```python tracy_postprocessing.py```.
