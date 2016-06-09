
AlmostSignificant
=====

AlmostSignificant is a platform to simplifying the quality control checks of Illumina HiSeq and
NextSeq sequencing runs. More detailed information is available in the docs folder.

Requires python 2.7, the illuminate package (available via pip install illuminate), and django >1.7 and pdflatex.
The install script requires the python package virtualenv as well. 

Start
-----------
Download the AlmostSignificant.tar.gz file and extract it:
	`tar -xvf AlmostSignificant.tar.gz`
then move to the directory created:
	`cd AlmostSignificant-*`

Run the install script, installAlmostSignificant.sh, with the arguement being the folder you want to create the AlmostSignificant server in, for example: 
	`bash installAlmostSignificant.sh AlmostSignificantServer`

This should run through, creating a virtual environment for the server, setting up django and any required dependencies, and lovating the dataLoading scripts into the bin folder of the virtual environment. 

When finished, the django server can be launched by running the runAlmostSignificant.sh script located in the bin folder, e.g.:
	`bash bin/runAlmostSignificant.sh` 
and then navigating to 127.0.0.8000 in a browser (though this may be different. The script should inform you of it's address.
DataLoading
----------

The dataloading script is supplied with the almostSignificant install, or can be downloaded from the github page. It is worth copying the dataLoading script and pdfGenerator.sh scripts into somewhere on your python path and path, respectively. The default location for a sudo install on ubuntu is::
    `/usr/local/lib/python2.7/dist-packages/almostSignificant/dataLoading/`

You'll also need the pocation of the django project in your python path, eg:
    `export PYTHONPATH=/home/User/Public/ASTest/ASTest/:/usr/local/lib/python2.7/dist-packages/almostSignificant/dataLoading/:$PYTHONPATH`

Usage:
    `python dataLoading.py <runLocation> <rawLocation> <qcFolder>` 

where runLocation is the folder produced by bcl2fastq or bcl2fastq2
rawLocation is the folder produced by the sequencing machine, and contains the sample sheet for the run, named SampleSheet.csv
qcFolder is a folder containing all of the fastQC and/or fastQScreen output for all of the fastq files that are in the runLocation. 
Tip: If you don't normally keep all of the QC output in a single folder (subfolders within this folder are permitted), try hard or soft linking the files into a single folder.

Optional arguements:
`-m, --machineType` takes either hiseq or nextseq. By default assumes runs are nextseq runs.
`-c, --checkUndets` signifies that the script is to check what indexes are in the undetermined index files. By default it doesn't do this as it can take some time, depending on the total number of undetermined indexes. 

example:
    '''
	python dataloading.py /data/nextseq/processed/160127_NS500001_0001_ARUNIDENT/ /data/nextseq/raw/160127_NS500001_0001_ARUNIDENT/ /data/nextseq/processed/160127_NS500001_0001_ARUNIDENT/QC_Data -c
	'''
This would load in the data for a nextseq run and gather information on the undetermined indexes.

