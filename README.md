# dyson-orbital_generator
Using the MO in a fchk file and a file with the Feynman-Dyson amplitudes (FDA) in the M.O. basis this script generate a new fchk file where the M.O. are replaced by the Dyson orbitals for which the the FDA were given in the file.  

This script needs python 3 and the getopt, numpy, and sys libraries.
You can run this script in terminal as follows:

dyson_orbitals.py MO.fchk FDA.log 1

the output generated in this case is dyson_orbs_MO.fchk
