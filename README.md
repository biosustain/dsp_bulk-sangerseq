# Sanger sequencing tool for bulk analysis

## Background
Sanger sequencing ([Sanger *et al.*, 1977](https://doi.org/10.1073/pnas.74.12.5463)) remains an important approach for targeted DNA sequencing in molecular biology. With the substantial increase of throughput in biological experimentation like in microbial genome engineering campaigns in industrial biotechnology, the manual evaluation of Sanger sequencing results becomes a very time-consuming task.  
This **Bulk Sanger Sequencing Tool** was developed to reduce this time investment while maintaining a high quality of results evaluation. The tool uses established software that is specifically arranged to handle Sanger sequencing data in bulk. At its core, [Tracy] (https://github.com/gear-genomics/tracy), [Sage] (https://github.com/gear-genomics/sage) and [Indigo](https://github.com/gear-genomics/indigo) are used for the analysis and visualisation of Sanger sequencing data ([Rausch *et al.*, 2020](https://doi.org/10.1186/s12864-020-6635-8)).

## Applicability
Sanger sequencing results with one or multiple sequencing files can be analysed. This can be either forward or reverse sequencing. For reverse sequencing, the reference sequence is automatically reverse-complemented by tracy without the need of manual intervention (in the alignment file output, the fasta header of the refernece sequence indicates it it was used in forward direction or reverse-complemented for the alignment).  
Combined analyses by assembling forward and reverse sequencing results is possible. A summary of all tracy functionalities can be found [here](https://www.gear-genomics.com/docs/tracy/cli/).

## Installations instructions and prerequisites
To be able to use the bulk-sangerseq tool, several installations steps need to be performed and a GitHub account need to be created.  

### Create GitHub account
[Create a GitHub account](https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home) or sign in to your existing account.   

### Install all prerequisites

The installation instructions are specifically for users of WSL (Windows Subsystems for Linux).

#### Install Ubuntu via WSL on Windows machine
Open PowerShell by right-clicking on the icon and select "Run as administrator". To install WSL on your machine, use the following command: 
```
wsl --install
```  
For further details, please refer to these [instructions](https://learn.microsoft.com/en-gb/windows/wsl/install). The default Linux distribution installed is Ubuntu. Please keep that and do not change the distribution.  
To open the Ubuntu terminal, right-click on the PowerShell icon and select "Ubuntu 22.04.5 LTS".

#### Update package manager
In the following sections multiple installations carried out using the linux package manager ```apt-get```. Update the package manager using the following command in the Ubuntu terminal:  

```
sudo apt-get update
```  

#### Generate SSH key and add it to the ssh-agent
SSH connections are secure connections that work with a private and a public key pair.  
To generate an ssh-keygen pair, please follow the [instructions](https://docs.github.com/en/enterprise-cloud@latest/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) until section "Adding your SSH key to the ssh-agent".  
The public key has to be added to your github account. Please follow [these instructions](https://docs.github.com/en/enterprise-cloud@latest/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account?platform=linux).  
Now, a secure ssh connection between your computer and github can be established.  

**NOTE:** Every time you restart your computer, you have to add the ssh key to the ssh agent.

#### Install git
Check if git is already installed on your system by typing into your terminal 
```
git version
```
If not already installed on your computer, follow the [installation instructions](https://github.com/git-guides/install-git) in section "Install Git on Linux".

#### Install Python 3.12.12
The bulk-sangerseq tool requires python version 3.12. All tests on WSL were performed using python version 3.12.12 which can be installed using the following command. More details can be found [here](https://docs.python-guide.org/starting/install3/linux/). 

```
sudo apt-get install python3.12.12
```

#### Install pipenv
Pipenv is a virtual environment management tool. You can install it from the command line using the following command. Further details can be found [here](https://pypi.org/project/pipenv/).  

```
pip install --user pipenv
``` 

#### Install Docker
The tool makes use of Docker images for containerization of software applications. Follow the [installation instructions](https://docs.docker.com/engine/install/ubuntu/). 

#### Install  Visual Studio code [*optional*]
Installing Visual Studio (VS) code is not a requirement but it facilitates while working with the tool. VS Code can be downloaded [here](https://code.visualstudio.com/download).

## Cloning the dsp_bulk_sangerseq repository from GitHub
Open the terminal and perform the following steps consecutively:

1. Change to the desired directory using ```cd </absolute/path/to/project/folder>```.
2. Clone the github repository using ```git clone git@github.com:biosustain/dsp_bulk-sangerseq.git```.
3. Change to the project directory using ```cd </dsp_bulk-sangerseq>```.
4. Install all dependencies from the Pipfile.lock using ```pipenv sync```.

## Usage of the tool

### Prepare data and a samplesheet  
The tool requires Sanger sequencing (.ab1) and reference files stored in a multifasta file (.fa) files.  

Deposit all .ab1 files and the multifasta file into the folder **data**. 

Prepare a **samplesheet** according to the template below and save it as .csv file. It is recommended to deposit the samplesheet.csv in the **data** folder. Here you can also find three templates in subfolder ```data/test_data_1```. The tool will read the samplesheet file automatically after specifying the path to it in the ```config.yaml``` file (see instructions below).  
**Note**: 
The tool analyses samples that were sequenced in either forward or reverse direction. Reverse sequencing is **automatically** detected by the tracy software, *i.e.* any input sequences do **not** need to be reverse-complemented prior to analysis. The output files will indicate if reverse-complementation was performed.  

In the ```sample_id``` column, fill in the sample names. In the ```ab1_file``` column, fill in the name of the sequencing file including the .ab1 file extension.   
The tool uses references stored in a multifasta file. Fill the ```reference_id``` column with reference names which **must be the fasta header in the provided multifasta file**. 

The ```assembly_group``` column is used for sequence assembly, e.g. assembling DNA sequencing from forward and reverse sequencing of a gene of interest. A minimum of two sequences can be assembled, however, assembling more sequences is possible. Currently, only reference-guided assembly is implemented, *i.e.* a reference file must be provided. In the ```assembly_group```column the user has to specify which sequences should be assembled. This is done here using a ```1``` or ```2```. In the example below, samples_3 and sample_4 (assembly_group 1) will be assembled using reference_C whereas sample_5 and sample_6 (assembly_group 2) will be assembled separately using reference_D.  
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
Change the following **variables to update the paths**. In general, the use of absolute paths is recommmended but relative paths can be used too.  

```data_host``` (dtype: string): relative or absolute path to the data directory on your computer.    
```outdir_host``` (dtype: string): relative or absolute path to the outdir directory on your computer. Default is ```./outdir```.  
```samplesheet``` (dtype: string): relative or absolute path to the samplesheet on your computer.  
```reference_fasta``` (dtype: string): relative or absolute path to the multi-fasta reference file on your computer.  


Change the following **variables to update tracy trimming parameters**.  

Trimming of sequences can be adjusted using hardcoded values.  
```trim_left``` (dtype: integer): number of DNA bases to trim at the 5'-end. Default is ```50```.   
```trim_right``` (dtype: integer): number of DNA bases to trim at the 3'-end. Default is ```50```.

Trimming stringency can be used in combination with ```trim_left``` and ```trim_right``` to determine sequence trimming length automatically based on the sequencing quality.  Trimming stringency ranges from 1:9 with 1 being the lowest and 9 the highest stringency, 0: disable.  
Trimming stringency is handled separately for each of he tracy commands ```decompose```, ```align``` and ```assemble```.
Note, that for standard analyses workflows, trimming stringency for ```decompose``` and ```align``` should be identical values.  

```trimming_stringency_decompose``` (dtype: integer): Default is ```0```.  
```trimming_stringency_align``` (dtype: integer): Default is ```0```.  
```trimming_stringency_assemble``` (dtype: integer): Default is ```4```.  


### Run the dsp_bulk_sangerseq tool   

Perform the following three steps consecutively.

1. Start the Docker daemon  
Sequence analysis using tracy is done in Docker containers for which the Docker daemon has to be started using the following command. Further information can be found in the [docker documentation](https://docs.docker.com/engine/daemon/start/).  

```
sudo systemctl start docker
```  

Alternatively, Docker Desktop can be started instead (if installed).

2. In the project directory, activate the virtual environment using command  
```
pipenv shell
```

3. Perform Sanger sequencing analysis using command  
```
bash main.sh
```
