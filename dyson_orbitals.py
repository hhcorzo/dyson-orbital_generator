#!/usr/bin/python3

import sys
import getopt
import numpy as np

def st_to_sci(n):
    return '%.8E' % float(n)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def orbital_split(lts,nbasis,nbuse):
     orbs={}
     for i,x in enumerate(chunks(lts,nbasis),1):
        if len(x)==nbasis:
            orbs[i]=x
        else:
             sys.exit('Orbital', i, 'has less elements than nbasis')
     if len(orbs)!= nbuse:
        sys.exit('Number of orbitals extracted no equal to Nbuse')
     return orbs

def orb_extraction_info(filename1):
    NBasis = 0
    NBuse=0
    with open(filename1,'r') as fila:
        for line in fila:
            if  "Number of basis functions" in line:
              words = line.split()
              for i in words:
                  for letter in i:
                      if(letter.isdigit()):
                          NBasis = NBasis*10 + int(letter)
            elif  "Number of independent functions" in line:
              words = line.split()
              for i in words:
                  for letter in i:
                      if(letter.isdigit()):
                          NBuse = NBuse*10 + int(letter)
            if NBasis >0 and NBuse>0:
               return  NBasis,NBuse


def amp_extraction_info(filename2):
    '''This routine extracts the basis and orbital information from the  file with the  Feynman-Dyson'''
    NBasis = 0
    NBuse=0
    with open(filename2,'r') as origin:
        for line in origin:
            if  "NBasis=" in line:
              words = line.split()
              #print(words)
              NBasis = int(words[1])
              if  words[6]=='NFC=':
                  NFC=int(words[7])
            elif  "NROrb=" in line:
              words = line.split()
              NBuse = int(words[1])
            if NBasis >0 and NBuse>0:
               return  NBasis,NBuse,NFC

def extract_orbitals(filename1):
    '''This routine extracts the M.O. from the fchk file'''
    NBasis,NBuse=orb_extraction_info(filename1)
    print ("Number of Basis Functions used = ", NBuse, "\n")
    print ("Number of Basis Functions = ", NBasis, "\n")
    MOElements = NBasis * NBasis
    print ("The code will look for ", MOElements, " elements of the MO Coeffient matrix\n")
    PElements = int(NBasis*(NBasis+1)/2)
    MOlines = int(MOElements/5) + 1
    if (MOElements % 5 ==0):
       MOlines = int(MOElements/5)
    ## we reopen the file again but this is not necesary we can just keep going witht he first open and print the info latter
    MolOrbitals=[]
    with open(filename1,'r') as origin:
        orb=0
        j=0
        for i, line  in enumerate(origin):
            if orb==1:
               linelist = line.split()
               linelist=[np.float(x) for x in linelist]
               MolOrbitals.extend(linelist)
               if i==j: 
                   Orbital_Dict=orbital_split(MolOrbitals,NBasis,NBuse)
                   return Orbital_Dict,NBasis,NBuse
            elif  "Alpha MO coefficients" in line:
                  l=i+1
                  print("Alpha MO coefficients starts at line :", l)
                  j=l+MOlines-1
                  print("\nAlpha MO coefficients ends at line :", j)
                  orb=1

def extract_amplitudes(filename2):
    '''This routine extracts the Feynman-Dyson amplitudes'''
    NBasis,NBuse,NFC=amp_extraction_info(filename2)
    print ("Number of Basis Functions used = ", NBuse, "\n")
    print ("Number of Basis Functions = ", NBasis, "\n")
    print ("Number of frozen core = ", NFC, "\n")
    print ("The code will look for ", NBuse, "FEYNMAN-DYSON AMPLITUDES")
    ## we reopen the file again but this is not necesary we can just keep going witht he first open and print the info latter
    ps_orbs={}
    orb_amp=[]
    orb_num=0
    orb_ps=0
    orb_amp_dic={}
    with open(filename2,'r') as origin:
        orb=0
        j=0
        for i, line  in enumerate(origin):
            if orb==1:
               linelist = line.split()
               #print(linelist[1])
               val_am=linelist[1].replace('D','E')
               val_am=np.float(val_am)
               orb_amp.append(val_am)
               if i==(j+NBuse):
                  if len(orb_amp)!=NBuse:
                     sys.exit('Number of amplitudes extracted no equal to Nbuse')
                  orb_amp_dic[orb_num]=orb_amp
                  ps_orbs[orb_num]=orb_ps
                  orb=0
                  orb_amp=[]
                  orb_num=0
                  orb_ps=0
            elif "FEYNMAN-DYSON AMPLITUDES IN M.O. BASIS:" in line:
                orb=1
                j=i
            elif  "INDEX OF SPIN-ORBITAL:" in line:
                    words = line.split()
                    orb_num=int(words[3])
            elif "POLE STRENGTH  ="  in line:
                    words = line.split()
                    orb_ps=np.float(words[3])
    return orb_amp_dic,ps_orbs,NBasis,NBuse,NFC


def dict_to_list(MO_Orb,Dy_Orb,Dy_lst):
    '''This routine transform a dictionary with orbitals coeff to a list with all the orbital coeff with the correct format for the fchk'''
    orb_lst=[]
    orb_ctr=0
    for n in range(1,len(MO_Orb)+1):
        if n in Dy_lst:
            Dy_elmt=Dy_Orb[n]
            for element in Dy_elmt:
                orb_lst.append(st_to_sci(element))
                orb_ctr=1+orb_ctr
        else:
           MO_elemts=MO_Orb[n]
           for element in MO_elemts:
               orb_lst.append(st_to_sci(element))
               orb_ctr=1+orb_ctr
    return orb_lst,orb_ctr



def writting_new_fchk(filename1,orbtochange,DysonMO,orbcoff,NBasisorb,NBuseorb,NBasisDy,NOrbDy):
    #filename1: fchk file with the info needed to build the M.O
    #orbtochange: Orbital that will be changed in the fchk
    #DysonMO : Dyson orbitals in the M.O. basis
    #orbcoff: original fchk orbital coeff C(Nbasis,NBuse)
    #NBasisorb:  original fchk NBasis
    #NBuseorb: original fchk NBused sometimes equal to NOrb but not always
    #NBasisDy: Nbasis reported in the output with the FEYNMAN-DYSON AMPLITUDES
    #NOrbDy:  Norb reported in the output with the FEYNMAN-DYSON AMPLITUDES

    #In the original fchk file there are NBuseorb orbitals
    orb_elems=(NBasisorb*NBasisorb)
    orb_lines=int(orb_elems/5)
    orb_extra=orb_elems-(orb_lines*5)
    #print(orb_lines,orb_extra)
    if (orb_extra) >0:
        orb_lines=orb_lines+1
    #transforming the orb to scientific notation
    orb_sc,orb_tl=dict_to_list(orbcoff,DysonMO,orbtochange)
    if (orb_tl!=(NBasisorb*NBuseorb)):
        sys.exit('The number of orbitals is not consistent\n','Transformed:',orb_tl,' fchk NBasis*NBsuse:',(NBasisorb*NBuseorb))
    dyson_file = "dyson_orbs_"+filename1
    orb=False
    with open(filename1,'r') as f1:
        with open(dyson_file, "w") as f2:
            for i,line in enumerate(f1):
                if orb:
                 line_ct=orb_lines-1
                 for i,x in enumerate(chunks(orb_sc,5),1):
                     for val in x:
                        if np.float(val) >= 0:
                            f2.write('  ')
                        else:
                            f2.write(' ')
                        f2.write(val)
                     f2.write('\n')
                     if line_ct >0:
                         line=next(f1)
                         line_ct=line_ct-1
                 orb=False
                elif "Alpha MO coefficients" in line:
                    f2.write(line)
                    orb=True
                else:
                    f2.write(line)
    return print('A new fchk file with Dyson orbitals was created')






def dyson_formation(filename1,filename2,normal):
    '''This routine generates the fchk with the Dyson orbitals'''
    #filename1: fchk file with the info needed to build the M.O
    #filename2: file with the Feynman-Dyson amplitudes in the M.O. basis
    #normal: The normalization of the Dyson orbital if equal to 0 the normalization will be the P.S; equal to 1 the normalization is the unity.
#
#
    orb_coff,NBasis_orb,NBuse_orb= extract_orbitals(filename1)
    orb_amp,orb_ps,NBasis_dy,NOrb_dy,NFC=extract_amplitudes(filename2)
#
######Forming arrays:
#
    #Molecular orbitals
    MO_array=[]
    for key in range(NFC+1,NOrb_dy+2):
        orb_x=orb_coff[key]
        MO_array.append(orb_x[NFC:])
    MO_array=np.array(MO_array)
    MO_array_T=MO_array.transpose()
#
    #FEYNMAN-DYSON AMPLITUDES
    for key in orb_amp:
        FDA_x=np.array(orb_amp[key])
        FDA_x=FDA_x.reshape(NOrb_dy,1)
        orb_amp[key]=FDA_x
#
########### Forming Dyson orbitals adding the frozen orbitals coeff as zeros
    Dyson_MO={}
    orb_to_change=[]
    orb_NFC_indx=[]
    for key in orb_amp:
          all_orb=np.zeros(NFC)
          FDA_v=orb_amp[key]
          DMO=np.matmul(MO_array_T, FDA_v)
          #Normalization:
          if normal==1: # to the unity 
              allorb=np.append(all_orb,(DMO.transpose()/np.sqrt(orb_ps[key])))
          else: # to the P.S.
               allorb=np.append(all_orb,DMO.transpose())
##### we add + NFC to the key because I think the calculation set's as orbital 1 the NFC+1 but someone need to check how the propagation code set the orbital index
          Dyson_MO[key+NFC]=allorb
          orb_to_change.append(key+NFC)
          orb_NFC_indx.append(key)
######## Forming the new fchk file

    writting_new_fchk(filename1,orb_to_change,Dyson_MO,orb_coff,NBasis_orb,NBuse_orb,NBasis_dy,NOrb_dy)
    print('with Dyson orbitals instead of the M.O.', ', '.join(map(str,orb_to_change)))
    print('Dyson orbitals for the orbitals: ',', '.join(map(str,orb_NFC_indx )),' were mapped to the M.O.', ', '.join(map(str,orb_to_change )))
#
    return print('\n***  =^-_-^= ***=^-_-^=***=^-_-^=***=^-_-^=***=^-_-^= ***\n\n          Ich habe eine murrisch grosse Katze\n\n***  =^-_-^= ***=^-_-^=***=^-_-^=***=^-_-^=***=^-_-^= ***\n  ')
#



###test#################################
#filename1="h2o_test_orbitals.fchk"
#filename2="h2o.log"
#dyson_formation(filename1,filename2,1)
##########################################



def main(argv):
   inputfile = ''
   outputfile = ''
   normalization=''
   try:
      opts, args = getopt.getopt(argv,"h")
   except getopt.GetoptError:
      print ('dyson_obitals.py  <MOs> <FDA> <normalization>')
      sys.exit(2)
   for opt, arg in opts: 
      if opt == '-h':
         print('Using a fchk with M.O and a file with the Feynman-Dyson amplitudes,  this script generate and fchk with the Dyson orbitals') 
         print ('To run the script: dyson_orbitals.py  <MOs> <FDA> <N> ')
         print('MOs: fchk file with the HF M.Os (file.fchk) ')
         print('FDA: Feynman-Dyson amplitudes file with P.S (file.log) ')
         print('N: Normalization for the Dyson orbitals, if P.S N=0 if unity N=1 (0 or 1) ')
         sys.exit()
   if len(args)==3:
    print ('M.O. file is: ', args[0])
    print ('Feynman-Dyson amplitude file is: ',args[1])
    if args[2]==1:
        print('Orbital normalization will be equal to 1')
    else:
        print('Orbital normalization will be equal to P.S.')
    print('\n ******************** \n')
    dyson_formation(args[0],args[1],args[2])
   else:
      print ('dyson_obitals.py  <MOs> <FDA> <normalization>')
      print('type dyson_obitals.py -h for help')
      sys.exit(2)


if __name__ == "__main__":
   main(sys.argv[1:])
