#Online documentation
https://www.gear-genomics.com/docs/tracy/cli/#deconvolution-of-heterozygous-mutations

#tracy example command for alignment works
tracy align -o outprefix -r reference.fa input.ab1  

#Variant calling to get alignment files (runs successfully); seems to give better information and alignment (see file vaiant.align1)
tracy decompose -v -r reference.fa -o results/variant EF73244592_EF73244592.ab1

#Ajusting trimming length (might be necessary to eavoid aligning bad quality of sequencing read at the end of the sequence) --> shown here trimRight=200 (trimLeft IS SET TO 50 BY DEFAULT)
tracy decompose -v -r reference.fa -o results/variant_trim --trimRight 200 EF73244592_EF73244592.ab1 