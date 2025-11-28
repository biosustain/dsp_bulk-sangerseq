# Test data set 1

## Source
The data set "test_data_1" was obtained from the [geargenomics Pearl software repository](https://github.com/gear-genomics/pearl/tree/main/server).  
It is suitable to test the ```tracy assemble``` as well as the ```tracy decompose``` and ```tracy align``` command.  

## Mofifications

### Reference file
The reference file was renames to references.fa and was extended by a mutated sample for testing multi-fasta-reference file reading. Also, reference names were modified.

### Samplesheets

**samplesheet_test_data_1.csv:**  
Align and assemble each of the nine sequences against a single reference. No mutation detection is expected.

**samplesheet_test_data_1_multi_ref.csv:**  
Align and assemble five sequences against a reference (no mutation detection expected) and four sequences agaisnt a mutated reference.

**samplesheet_test_data_1_multi_ref_grouping.csv:**  
Align and assemble five sequences against a reference (no mutation detection expected) and four sequences against a mutated reference. Here, grouping in the samplesheet is introduced.

## Usage
Use sample_{x}.abi files for testing against the reference file sample.fa.  
The sample sheet "samplesheet_test_data_1.csv" is ready to use.