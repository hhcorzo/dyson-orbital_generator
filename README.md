# dyson-orbital_generator
Using the MO in a fchk file and a file with the Feynman-Dyson amplitudes (FDA) in the M.O. basis this script generate a new fchk file where the M.O. are replaced by the Dyson orbitals for which the the FDA were given in the file.  

This script needs python 3 and the getopt, numpy, and sys libraries.
You can run this script in terminal as follows:
$ python dyson_orbitals.py \<arg1\> \<arg2\> \<arg3\> <br>
\<arg1\>: .fchk file with the HF canonical. <br>
\<arg2\>: .log file with the Dyson-Feynman amplitudes and poles <br>
\<arg3\>: Normalization factor 1 or 0 <br>
<b>Example</b> <br>
$ python dyson_orbitals.py MO.fchk FDA.log  1 <br>
the output generated in this case is dyson_orbs_MO.fchk
