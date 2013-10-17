#!/usr/bin/env python

################################################
#
# Submit limits calculating codes by lxplus Batch
#
# Coding is based on submit_condor.py
#
# Jinzhong Zhang, Nov 2011
#
################################################

import sys
import os

#-------> parameters ----------------------------------------------------
#
# channel: dimuon, dielectron, dilepton,
#          mumu-ee-gg-xsec
#
#    mode: observed,
#          expected,
#          mass_cteq
#          mass_graviton
#

simulate = False

cfg_file="dimuon_ratio.cfg"
#channel = 'dilepton'
channel = 'dimuon'
#channel = 'dielectron'
#mode = 'observed'
mode = 'observed'
#mode = 'mass_cteq'
#mode = 'mass_graviton'

mass_min  =    300.0
mass_max  =    1500.1
mass_inc  =     25.0
n_iter    =    10000
n_burn_in =      500

exp_ntoys_per_job = 10           # these params are now used for observed as well
exp_ntoys_per_mass_point = 10

#
#------------------------------------------------------------------------
                            
legend = '[submit_condor]:'

#os.system("source ../../setup/lxplus_standalone_setup.sh")
os.system("exost -a workspace -c dimuon_ratio.cfg")
os.system('mv myWS.root ws_dimuon_ratio.root')
os.system('ls -lh ws_dimuon_ratio.root;date')
print "=========ws_dimuon_ratio.root should be updated====="
os.system('root -l -b -q -n dimuon.C++')
_dir=os.getcwd()

_nsubmit_per_mass_point = int((exp_ntoys_per_mass_point+1)/exp_ntoys_per_job)

_peak = mass_min
while _peak < mass_max:
    for JID in range(0, _nsubmit_per_mass_point):
        SHNAME=channel+"_limit_m"+str(_peak)+"_"+str(mode)+"_"+str(JID)+".sh"
        TMPDIR=channel+"_limit_m"+str(_peak)+"_"+str(mode)+"_"+str(JID)
        if not os.path.exists(TMPDIR):
            os.system('mkdir '+TMPDIR);
        else:
            print TMPDIR, " exists. It may contains unfinished jobs."
            continue
        os.system('cp run_limit.C '+TMPDIR+';cp dimuon_C.so '+TMPDIR+';cp ws_dimuon_ratio.root '+TMPDIR )
        SHFILE="#!/bin/bash\n"+          \
            "cd "+_dir+"\n"+\
            "source ../../setup/lxplus_standalone_setup.sh\n"+\
            "cd "+TMPDIR+"\n"
        SHFILE+='root -l -b -q -n run_limit.C\\(' + \
            '\\"'+channel+'\\",' + \
            '\\"'+mode+'\\",' + \
            str(_peak)+',' + \
            '\\"'+"m"+str(_peak)+"_"+str(JID)+'\\",' + \
            str(exp_ntoys_per_job)+',' + \
            str(n_iter)+',' + \
            str(n_burn_in)+',' + \
            '\\"\\",' + \
            '\\"\\"' + \
            '\\)\n'+\
            'rm ../'+SHNAME+'\n'+\
            'cp *.ascii ../;cd ..\n'+\
            'rm -rf '+TMPDIR+'\n'
        open(SHNAME, 'wt').write(SHFILE)
        os.system("chmod +x "+SHNAME)
        if not simulate:
            if JID==0 and _peak == mass_min:
                #os.system("bsub "+SHNAME)
                os.system("./"+SHNAME)
                print SHNAME," has output (LSFxxxxxx)"
            else:
                os.system("./"+SHNAME)
                #os.system("bsub -o /dev/null -e /dev/null -q 8nh "+SHNAME)#Here I turned off the email notification coming from LSF
    _peak += mass_inc
