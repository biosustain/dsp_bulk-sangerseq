# script to explore the content of an ab1 file

from Bio import SeqIO
from collections import defaultdict
import matplotlib.pyplot as plt

# %% Plot electropherogram traces
# see Biopython documentation: https://biopython.org/wiki/ABI_traces
# and the reference therein: http://www.appliedbiosystem.com/support/software_community/ABIF_File_Format.pdf 
# possible alternative: https://github.com/ponnhide/sangerseq_viewer
# geargenomics teal is another viewer: https://github.com/gear-genomics/teal
record = SeqIO.read(f'{cfg['paths']['data_host']}/EF73244592_EF73244592.ab1', 'abi')

print(list(record.annotations.keys()))
print(list(record.annotations['abif_raw'].keys()))


channels = ['DATA9', 'DATA10', 'DATA11', 'DATA12']
trace = defaultdict(list)
for c in channels:
    trace[c] = record.annotations["abif_raw"][c]

# plot data 
plt.plot(trace['DATA9'], color='blue')
plt.plot(trace['DATA10'], color='red')
plt.plot(trace['DATA11'], color='green')
plt.plot(trace['DATA12'], color='yellow')
plt.show()