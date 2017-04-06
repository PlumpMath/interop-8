#!/usr/bin/env python

import re
import os
import sys
import getopt
import platform
import subprocess
import FioUtils
import time

# fio --minimal hardcoded positions
fio_iops_pos=7
fio_slat_pos_start=9
fio_clat_pos_start=13
fio_lat_pos_start=37


def main():
    # instantiate the constant in this program
    const = FioUtils.Constant()

    kernel_version = os.uname()[2]
    columns="iotype;bs;njobs;iodepth;iops;slatmin;slatmax;slatavg;clatmin;clatmax;clatavg;latmin;latmax;latavg"

    #Fio execution summary stored in csv format
    f = open(kernel_version + time.strftime("%H%M%S") + "-fio.csv", "w+")
    f.write(columns+"\n")

   
    # we now create all jobs for fio based from the given workload in csv
    fio_dict = FioUtils.util_create_job_fio_cfg_new()

    # prepare fio related parameters
  
    fio_param0 = const.FIO_PROGRAM_NAME                                     # fio program name
    fio_param1 = const.FIO_MINIMAL                                              # use minimal for terse output

    # run fio program for all job listed in the workload file
    for entry_num, entry_list in fio_dict.items():
	fio_type_offset = 0
	iops = 0.0
        slat = [0.0 for i in range(3)]
        clat = [0.0 for i in range(3)]
        lat = [0.0 for i in range(3)]
	fio_params = entry_list[0] #fio params file
	access_type = entry_list[1]
	blocksize = entry_list[2]
	threads = entry_list[3]
	iodepth = entry_list[4]
	#if(access_type == "write"):
	#   fio_type_offset=41
       
	result = "" + str(access_type) + ";" + str(blocksize) + ";" + str(threads) + ";" + str(iodepth) + ";"

	command = fio_param0 + const.SPACE + fio_param1 + const.SPACE + fio_params
	
	print command
        output = subprocess.check_output(command, shell=True)      # execute the fio program
	print output
	
	iops = iops + float(output.split(";")[fio_type_offset + fio_iops_pos])
	
	for j in range (0, 3):
             slat[j] = slat[j] + float(output.split(";")[fio_type_offset+fio_slat_pos_start+j])
	for j in range (0, 3):
             clat[j] = clat[j] + float(output.split(";")[fio_type_offset+fio_clat_pos_start+j])
	for j in range (0, 3):
             lat[j] = lat[j] + float(output.split(";")[fio_type_offset+fio_lat_pos_start+j])
	# iops
        result = result+str(iops)
        # slat
        for i in range (0, 3):
          result = result+";"+str(slat[i])
        # clat
        for i in range (0, 3):
          result = result+";"+str(clat[i])
        # lat
        for i in range (0, 3):
          result = result+";"+str(lat[i])

        print (result)
        f.write(result+"\n")
        f.flush()
	
	
    f.closed	

    print '\n\nall done.'
    return


if __name__ == '__main__':
    # the entry point of the program
    main()
