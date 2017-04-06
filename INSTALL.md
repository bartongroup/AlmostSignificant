
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
	`bash AlmostSignificantServer/almostSignificant/bin/runAlmostSignificant.sh` 
and then navigating to 127.0.0.8000 in a browser (though this may be different. The script should inform you of it's address.

DataLoading
----------

Three folders are needed for loading data into AlmostSignificant. The processed output folder created by bcl2fastq, the raw folder produced by the sequencing machine and a folder containing all of the fastQC and/or fastQScreen output. 

The data loading script in installed into the bin folder of the virtual environment. To load the data in, activate the environment:
	`source path/to/environment/bin/activate`

Run the dataloading script. The first arguement is the run folder from bcl2fastq, the second is the raw sequencing folder and the third is the folder containing the quality control output, e.g.: 

python bin/dataLoading.py ~/processed/160523_NS500650_AFLOWCELLID/ ~/raw/160523_NS500650_AFLOWCELLID/ ~/QC/160523_NS500650_AFLOWCELLID/`

Optional flags are setting the machine type, -m. Currently only Nextseq and Hiseq machines are supported. 
Setting -c will check the undertermined reads for a run, which is reccommended, but can take some time. By default this does not happen. 


Usage:
    `python dataLoading.py <runLocation> <rawLocation> <qcFolder>` 

where runLocation is the folder produced by bcl2fastq or bcl2fastq2
rawLocation is the folder produced by the sequencing machine, and contains the sample sheet for the run, named SampleSheet.csv
qcFolder is a folder containing all of the fastQC and/or fastQScreen output for all of the fastq files that are in the runLocation. 
Tip: If you don't normally keep all of the QC output in a single folder (subfolders within this folder are permitted), try hard or soft linking the files into a single folder.

Optional arguements:
`-m, --machineType` takes either hiseq, miseq or nextseq. By default assumes runs are nextseq runs.
`-c, --checkUndets` signifies that the script is to check what indexes are in the undetermined index files. 

