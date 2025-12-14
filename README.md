# Sanger sequencing tool for bulk analysis

## Background
Sanger sequencing ([Sanger *et al.*, 1977](https://doi.org/10.1073/pnas.74.12.5463)) remains an important approach for targeted DNA sequencing in molecular biology. With the substantial increase of throughput in biological experimentation like in microbial genome engineering campaigns in industrial biotechnology, the manual evaluation of Sanger sequencing results becomes a very time-consuming task.  
This **Bulk Sanger Sequencing Tool** was developed to reduce this time investment while maintaining a high quality of results evaluation. The tool uses established software that is specifically arranged to handle Sanger sequencing data in bulk. At its core, [Tracy](https://www.gear-genomics.com/) ([GitHub](https://github.com/gear-genomics/tracy)) and [Sage](https://www.gear-genomics.com/) ([GitHub](https://github.com/gear-genomics/sage)) are used for the analysis and visualisation of Sanger sequencing data ([Rausch *et al.*, 2020](https://doi.org/10.1186/s12864-020-6635-8)).

## Applicability
Currently, Sanger sequencing results with one sequencing file can be analysed. This can be either forward or reverse sequencing. For reverse sequencing, the reference sequence is automatically reverse-complemented by tracy without the need of manual intervention (in the alignment file output, the fasta header of the refernece sequence indicates it it was used in forward direction or reverse-complemented for the alignment).  
Combined analyses by assembling forward and reverse sequencing results is currently not possible, albeit tracy offers this functionality (to be implemented soon). A summary of all tracy functionalities can be found [here](https://www.gear-genomics.com/docs/tracy/cli/).

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
Open the terminal and perform the following steps consecutively:
1. Change to the desired directory using ```cd </absolute/path/to/project/folder>```.
2. Clone the github repository using ```git clone https://github.com/biosustain/dsp_bulk-sangerseq.git```.
3. Change to the project directory using ```cd </dsp_bulk-sangerseq>```.
4. Install all dependencies from the Pipfile.lock using ```pipenv sync```.

## Usage

### Prepare data and a samplesheet  
The tool requires Sanger sequencing (.ab1) and reference files stored in a multifasta file (.fa) files.  

Copy all .ab1 files and the multifasta file into the folder **data**. 

Prepare a **samplesheet** according to the template below and save it as .csv file. It is recommended to deposit the samplesheet.csv in the **data** folder. Here you can also find three templates in subfolder ```data/test_data_1```. The tool will read the samplesheet file automatically after specifying the path to it in the ```config.yaml``` file (see instructions below).  
**Note**: 
The tool analyses samples that were sequenced in either forward or reverse direction. Reverse sequencing is automatically detected by the tracy software, i.e. any input sequences do not need to be reverse-complemented prior to analysis. The output files will indicate if reverse-complementation was performed.  

In the ```sample_id``` column, fill in the sample names. In the ```ab1_file``` column, fill in the name of the sequencing file including the .ab1 file extension.   
The tool uses references stored in a multifasta file. Fill the ```reference_id``` column with reference names which must be the fasta header in the provided multifasta file. 

The ```assembly_group``` column is used for sequence assembly, e.g. assembling DNA sequencing from forward and reverse sequencing of a gene of interest. A minimum of two sequences can be assembled, however, assembling more sequences is possible. Currently, only reference-guided assembly is implemented, i.e. a reference file must be provided. In the ```assembly_group```column the user has to specify which sequences should be assembled. This is done here using a ```1``` or ```2```. In the example below, samples_3 and sample_4 (assembly_group 1) will be assembled using reference_C whereas sample_5 and sample_6 (assembly_group 2) will be assembled separately using reference_D.  
If no assmebly of samples is desired, the fields in the ```assembly_group``` column have to be left blank (see sample_1 and sample_2 in below example).

| sample_id       | ab1_file     | assembly_group  | reference_id  |
|-----------------|--------------|-----------------|---------------|
| sample_name_1   | file_1.ab1   |                 | reference_A   |
| sample_name_2   | file_2.ab1   |                 | reference_B   |
| sample_name_3   | file_3.ab1   | 1               | reference_C   |
| sample_name_4   | file_4.ab1   | 1               | reference_C   |
| sample_name_5   | file_5.ab1   | 2               | reference_D   |
| sample_name_6   | file_6.ab1   | 2               | reference_D   |

### Modify the configuration file (config.yaml)  
Change the ```data_host``` variable to become the absolute path to the data directory on your computer.
Change the ```outdir_host``` variable to become the absolute path to the outdir directory on your computer.
In general, the use of absolute paths is recommmended but relative paths can be used too.

### Start the Docker engine  
- On MacOS and Windows, start Docker desktop.
- On Linux: command goes here

### Run scripts of dsp_bulk_sangerseq consecutively    
Perfrom all the following steps consecutively.
1. In the project directory, activate the environment using ```pipenv shell```. Alternatively, activate the environment from within the code editor, e.g. VS code.
2. Perform Sanger sequencing analysis using tracy by running command ```python tracy_bulk_docker_samplesheet.py```.
3. Perform post-processing of results by running command ```python tracy_postprocessing.py```.
4. Generate Sanger trace images (interactive html files) by running ```python tracy_render_align.py```.
