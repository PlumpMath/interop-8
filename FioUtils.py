#!/usr/bin/env python
import os
import time
import csv
import platform


class Constant:
    WINDOWS_OS = 'Windows'
    LINUX_OS = 'Linux'
    OS_PLATFORM_32 = '32bit'
    OS_PLATFORM_64 = '64bit'

    # FIO related arguments
    OUTPUT_TERSE = 'terse'
    OUTPUT_NORMAL = 'normal'
    OUTPUT_JSON = 'json'

    FIO_MINIMAL = '--minimal'
    FIO_OUTPUT_FORMAT = '--output-format'
    FIO_OUTPUT = '--output'
    FIO_INTERVAL = '--status-interval'
    FIO_FILE_NAME = "/dev/sda1"

   
    if platform.system() == LINUX_OS:
        FIO_PROGRAM_NAME = 'fio'
    elif platform.system() == WINDOWS_OS:
        FIO_PROGRAM_NAME = 'fio.exe'
        if platform.architecture()[0] == OS_PLATFORM_32:
            FIO_FOLDER = '\\Exec\\fio-2.1.10-x86'
        elif platform.architecture()[0] == OS_PLATFORM_64:
            FIO_FOLDER = '\\Exec\\fio-2.1.10-x64'
        else:
            FIO_FOLDER = ''
            print 'Error: Unknown OS Platform, not currently supported'
    else:
        FIO_PROGRAM_NAME = ''
        print 'Error: Unknown OS, not currently supported'
    # -----------------------------------------------



    ONE_HUNDRED_PERCENT = '100%'
    DOUBLE_BACKSLASH = r'\\'
    ESCAPE_SEQUENCE = r'\:'
    PERCENT = '%'
    UNDERSCORE = '_'
    EQUALS = '='
    SPACE = ' '
    COLON = ':'
    COMMA = ','
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    CHAR_C = 'C'



    OFF = 'OFF'
    ON = 'ON'

    BYTE = 'b'
    KILOBYTE = 'kb'
    MEGABYTE = 'mb'
    GIGABYTE = 'gb'

    XXX = 'xxx'
    U_XXX = '_xxx'

    DEF_TEMPERATURE = '+25C'
    DEF_BLOCK_ALIGNMENT = '4kb'
    DEF_DATA_PATTERN = 'random'
    DATA_PATTERN_ZERO = 'zero'

    CFG_FOLDER_NAME = 'Config'
    LOG_FOLDER_NAME = 'Logs'
    CFG_FILE_EXTENSION = '.fio'
    LOG_FILE_EXTENSION = '.log'

    PRECON_CFG_FILENAME = 'PreconCfg'
    PRECON_LOG_FILENAME = 'Precon'
    JOB_CFG_FILENAME = 'JobCfg'
    JOB_LOG_FILENAME = 'Job'
    ALL_JOB_LOG_FILENAME = 'All'

    CSV_FILE_HEADER = 'Test No'
    WORKLOAD_FOLDER_NAME = 'Workload'
    DEF_WORKLOAD_FILENAME = 'Workload.csv'

    REGEX_EXPRESSION = r"[^\W\d_]+|\d+"
    RESPONSE_LIST = ('yes', 'y')

    WIN_PHYSICAL_DEV = r'\\.\PhysicalDrive'
    WIN_LOGICAL_DEV = r'\\.\L:'

    def __setattr__(self, *_):
        pass


def util_create_job_fio_cfg_new():
    # instantiate fio dictionary needed for executing fio program
    fio_dict = {}

    # check if 'Config' folder exists
    curr_dir = os.getcwd()
    cfg_dir = curr_dir + os.sep + Constant.CFG_FOLDER_NAME
    if os.path.exists(cfg_dir) is False:    # does the 'Config' dir exists?
        os.mkdir(cfg_dir)

    # check if 'Log' folder exists
    job_log_folder = curr_dir + os.sep + Constant.LOG_FOLDER_NAME
    if os.path.exists(job_log_folder) is False:
        os.mkdir(job_log_folder)

    # Get the workload file and open it for parsing

    workload_folder = curr_dir + os.sep + Constant.WORKLOAD_FOLDER_NAME
    workload_filename = workload_folder + os.sep + Constant.DEF_WORKLOAD_FILENAME

    # separate the filename and file extension into two separate variables
    filename, extension = os.path.splitext(Constant.DEF_WORKLOAD_FILENAME)

    # Crawl the given workload line by line and then parse its data
    with open(workload_filename, 'rb') as csvreader:
        reader = csv.reader(csvreader, delimiter=',', quotechar='|')
        for row in reader:
            if Constant.CSV_FILE_HEADER in row:
                # skip the first line(header) of the csv file
                continue
            else:   # process succeeding line
                # CSV format description:
                # col1 = Test No.    || col2 = File Size    || col3 = Block Size
                # col4 = Access Type || col5 = Run Time     || col6 = Threads
                # col7 = IoDepth 

                # parse each row to get the FIO config file job 
                testnum = row[0]                    # Test No.
		filesize = str(row[1]).lower()       # File Size
                blocksize = str(row[2]).lower()      # Block Size
                access_type = row[3]               # Access Type
                runtime = row[4]                    # Run Time
                threads = row[5]                   # Number of Jobs or Thread
                iodepth = row[6]                   # Outstanding IO or IOdepth

                # get the time and date then append to job config file and log file
                now = time.strftime("%m%d%Y") + Constant.UNDERSCORE + \
                      time.strftime("%H%M")

                # set the initial job filename of the fio config file
                job_filename = Constant.JOB_CFG_FILENAME + Constant.UNDERSCORE + filename + \
                               Constant.UNDERSCORE + now

                # we now create the job file for the fio program
                job_filename = job_filename + Constant.UNDERSCORE + testnum + Constant.CFG_FILE_EXTENSION
                job_dir_n_file = cfg_dir + os.sep + job_filename

                # set the initial job log filename
                job_log_filename = Constant.JOB_LOG_FILENAME + Constant.UNDERSCORE + filename + \
                                   Constant.UNDERSCORE + now

                # we set the job log filename based on the test number
                job_log_filename = job_log_filename + Constant.UNDERSCORE + testnum + Constant.LOG_FILE_EXTENSION
                job_log_dir_n_file = job_log_folder + os.sep + job_log_filename

                with open(job_dir_n_file, 'wb') as writer:
                    writer.write('[job-no.%s,%s,%s]\n' % (testnum, str(blocksize), str(access_type)))
                    writer.write('description=%s {%s}\n' % (access_type, blocksize))

                    if platform.system() == Constant.LINUX_OS:
                        writer.write('ioengine=posixaio\n')
                    else:
                        writer.write('ioengine=windowsaio\n')
                        writer.write('thread\n')

                    writer.write('direct=1\n')
                    writer.write('bs=%s\n' % blocksize)

                    # check if file size were define from the workload
                    if filesize and not filesize.isspace():
                        writer.write('size=%s\n' % filesize)

                    writer.write('iodepth=%s\n' % iodepth)
                    writer.write('numjobs=%s\n' % threads)
                    writer.write('runtime=%s\n' % runtime)
                    writer.write('time_based\n')
                    writer.write('group_reporting\n')
                    writer.write('filename=%s\n' % Constant.FIO_FILE_NAME)

            # we update the list and dictionary needed for executing fio program
            fio_list = (job_dir_n_file,access_type,blocksize,threads,iodepth)
            fio_dict[int(testnum)] = fio_list
    return fio_dict
