#This script loads data from the relevant places into almostSignificant.

import os
import io
import sys
import xml.etree.ElementTree as ElementTree
import gzip
import re
from collections import Counter
import zipfile
import django
import datetime
import fnmatch
import subprocess
import shutil
import argparse


#load and import the models from django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import settings
from  almostSignificant.models import *

version = "0.051"


def openFileReadLines( targetFile ):
    """Opens the input file and returns it as a list of the lines"""
    #load data from the file 
    try:
        openTargetFile = open(targetFile, "r")
        targetFileLines = openTargetFile.readlines()
        openTargetFile.close()
        #strip all newline characters
        targetFileLines = map(lambda s: s.strip(), targetFileLines) 
    except IOError:
        print "Cannot open or access the file: %s" % targetFile
        raise
#        sys.exit()
    return targetFileLines


def parseOldSampleSheet( sampleSheetLocation ):
    """Parses all of the details from the sampleSheet for a run given the input sample sheet location

        Deprecated in favour of parseHiseqSampleSheet

        Takes the location of the sample sheet as input and creates a dictionary.
        Dictionary is in the format.
        ["SampleID"]["Sample","Reference","FCID","Lane","Barcode","Description",
                                            "Control", "Recipe","Operator","Project"]

    """

   
    #load data from the file 
    sampleSheetLines = openFileReadLines( sampleSheetLocation )

    #loop over all of the entries,creating a dict with an entry for each sample
    sampleSheetDict = {}
    #    Key - SampleID
    #        0 Sample Reference
    #        1 FCID
    #        2 Lane
    #        3 Barcode
    #        4 Description
    #        5 Control
    #        6 Recipe
    #        7 Operator
    #        8 Project
    sampleSheetLines.pop(0)
    for line in sampleSheetLines:
        sampleDetails = line.split(",")
        #default hiseq 2000 sample sheet.
        #FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,Project
        #This isn't the most concise way of doing this, but it's by far the clearest
        sampleID = sampleDetails[2]
        sampleReference = sampleDetails[3]
        FCID = sampleDetails[0]
        lane = sampleDetails[1]
        barcode = sampleDetails[4]
        description = sampleDetails[5]
        control = sampleDetails[6]
        recipe = sampleDetails[7]
        operator = sampleDetails[8]
        project = sampleDetails[9]

        sampleSheetDict[ sampleID ] = [ FCID, lane, barcode, description, control, 
                                        recipe, operator, project ]

    return( sampleSheetDict )


def parseNextseqSampleSheet( sampleSheetLocation ):
    """Returns a dictionary containing all the data in the given sample sheet

        Dict has 3 sections; header, reads and data.
        Header section has dicts containing the key:value pairs in the header section
        of the sample sheet
        Reads just has the length of the reads
        data is a dict where the key is the unique reference for the sample and the value 
        is another dict with column header:column value pairs for the sample.
        This allows it to adapt to the columns that are provided, rather than being rigid to one format.

    """

    #load data
    sampleSheetLines = openFileReadLines( sampleSheetLocation )

    header = {}
    reads = {}
    readCounter = 1
    settings = {} 
    data = {}
    sampleSheetReturn = {}
    #run through data skipping the first element
    section = ""
    #init datasection headers
    dataColumns = []
    for sampleSheetLine in sampleSheetLines:
        #if it's blank, skip it
        if sampleSheetLine.strip() == "":
            pass
        #define the section we're currently in
        elif sampleSheetLine[0] == "[":
            if sampleSheetLine.strip() == "[Header]":
                section = "header"
            elif sampleSheetLine.strip() == "[Reads]":
                section = "reads"
            elif sampleSheetLine.strip() == "[Settings]":
                section = "settings"
            elif sampleSheetLine.strip() == "[Data]":
                section = "data"
        else:    
            #get data from header section, add to header map
    
            if section == "header":
                splitLine = sampleSheetLine.strip().split(",")
                header[splitLine[0]] = splitLine[1]
            
            #get data from the Reads section
            elif section == "reads":
                readNumber = "read%d" % readCounter
                readCounter += 1
                reads[readNumber] = sampleSheetLine.strip()
        
            #get data from the settings section
            elif section == "settings":
                splitLine = sampleSheetLine.strip().split(",")
                settings[splitLine[0]] = splitLine[1]
                
        #get data from the data section
            elif section == "data":
            #init map using comma separated headers - varies depending on the run.
                if sampleSheetLine.strip().split(",")[0] == "Sample_ID":
                    dataColumns = sampleSheetLine.strip().split(",")
                #otherwise it's data
                else:
                    currentDataInput = sampleSheetLine.strip().split(",")
                    currentRowData = {}
                    #loop over the line to create a map for the information
                    for i,dataEntry in enumerate(currentDataInput): 
                        #dirty hack for making sure that the row length !> header length
                        if i < len(dataColumns):
                            currentRowData[dataColumns[i]] = dataEntry
                    #add this info to the data map with the sample id as the key
                    data[currentDataInput[0]] = currentRowData
    
    #package everything into a single map with header, reads, settings, data keys
    
    sampleSheetReturn = {"Header":header, "Reads":reads, "Settings":settings, "Data":data}

    return(sampleSheetReturn)


def parseHiseqSampleSheet( sampleSheetLocation ):
    """Parses a hiseq sample sheet given the location

    Returns a dictionary in with the keys header, reads and data

    Header contains a dict with the keys "Investigator Name" and "Assay", both blank.
    This is to maintain parity between this and the nextseq sample sheet
    Reads is empty
    Data contains a dictionary with the keys as the unique sample names for the samples
    Each of the values is dict containing the column header:column values.
    
    """
    #load data
    sampleSheetLines = openFileReadLines( sampleSheetLocation )

    header = {}
    reads = {}
    readCounter = 1
    settings = {} 
    data = {}
    sampleSheetReturn = {}
    #run through data skipping the first element
    section = ""
    #init datasection headers
    dataColumns = sampleSheetLines.pop(0).strip().split(",")
    #replace the word project with sample_project for later referencing.
    #Making all headers the same as NextSeqHeaders 
    dataColumns[dataColumns.index("Project")] = "Sample_Project"
    dataColumns[dataColumns.index("Index")] = "index"
    sampleIDIndex = dataColumns.index("SampleID")
    dataColumns[sampleIDIndex] = "Sample_ID"

    for sampleSheetLine in sampleSheetLines:
        #if it's blank, skip it
        if sampleSheetLine.strip() == "":
            pass
        #define the section we're currently in
        #get data from header section, add to header map

        currentDataInput = sampleSheetLine.strip().split(",")
        currentRowData = {}
        #loop over the line to create a map for the information
        for i,dataEntry in enumerate(currentDataInput): 
            #dirty hack for making sure that the row length !> header length
            if i < len(dataColumns):
                currentRowData[dataColumns[i]] = dataEntry
        #add this info to the data map with the sample id as the key
        data[currentDataInput[sampleIDIndex]] = currentRowData

    
    #package everything into a single map with header, reads, settings, data keys
    #header, reads, settings and data are prettymuch just placeholders for the hiseq
    header["Investigator Name"] = ""
    header["Assay"] = ""
    sampleSheetReturn = {"Header":header, "Reads":reads, "Settings":settings, "Data":data}

    return(sampleSheetReturn)

        
def loadFastQCZip( fastQCZipFile ):
    """Loads data in from the zip created by FastQC and returns a dictionary of the
        essential statistics. Also copies the image files into a sensible places for
        django to deal with it. TODO: Proper placement for image files

        Input is the zip file that fastqc generates. The files fastqc_data.txt and 
        summary.txt are parsed for the information they contain. 

        Returns dictionary with the keys:
        totalSequences
        filteredSequences
        sequenceLength
        percGC
        passWarnFail - this is itself a dictionary, with the following keys
            basicStatistics
            baseSequenceQuality
            sequenceQuality
            baseSequenceContent
            baseGCContent
            sequenceGCContent
            baseNContent
            lengthDistribution
            duplicationLevels
            overrepresentedSequences
            kmerContent                    

    """

    #load the zip file
    zipFile = file(fastQCZipFile)
    zipData = zipfile.ZipFile( zipFile )
    #get the summary.txt contents
    summaryFileName= [ s for s in zipData.namelist() if "summary.txt" in s][0]
    fastQCSummaryBytes = zipData.open(summaryFileName)
    fastQCSummary = fastQCSummaryBytes.readlines()
    #get the data.
    dataFileName= [ s for s in zipData.namelist() if "fastqc_data.txt" in s][0]
    fastQCDataBytes = zipData.open(dataFileName)
    fastQCData = fastQCDataBytes.readlines()
    
    return [fastQCSummary, fastQCData]

    #open the fastqc zip file safely
    #send the text file contents to parseFastQCData
    #move the image files to a sensible place for django.
    #pass the summary data back to whatever called this


def parseFastQCData( fastQCDataLocation=False, fastQCSummaryObject=False ):
    """Loads the data from the fastqc_data.txt file and returns it as a dictionary

       Input is either:
        fastQCDataLocation - the _folder_ that fastqc generates. The files fastqc_data.txt and 
        summary.txt are parsed for the information they contain. 
       Or:
        fastQCSummaryObject - list of two lists. First is the summary.txt data, second is the
        fastqc_data.txt data. This is output from the function loadFastQCZip.

        Returns dictionary with the keys:
        totalSequences
        filteredSequences
        sequenceLength
        percGC
        passWarnFail - this is itself a dictionary, with the following keys
            basicStatistics
            baseSequenceQuality
            sequenceQuality
            baseSequenceContent
            baseGCContent
            sequenceGCContent
            baseNContent
            lengthDistribution
            duplicationLevels
            overrepresentedSequences
            kmerContent                    
            q30Length

    """
    
    #print "fastQCDataLocation: %s" % fastQCDataLocation
    #print "fastQCSummaryObject: %s" % fastQCSummaryObject
    #load data from the file or from the input list
    if fastQCDataLocation != False:
        try:
            openFastQCSummary = open("%s/summary.txt" % fastQCDataLocation, "r")
            #line for testing the order
            #openFastQCSummary = open("%s/summary_testing.txt" % fastQCDataLocation, "r")
            fastQCSummaryLines = openFastQCSummary.readlines()
            openFastQCSummary.close()
            #strip all newline characters
            fastQCSummaryLines = map(lambda s: s.strip(), fastQCSummaryLines) 
#           elif fastQCSummaryObject != False:
#           openFastQCSummary = open(fastQCSummaryObject, "r")
        except IOError:
            print "Cannot open or access the fastQC summary: %s/summary.txt" % fastQCDataLocation
            raise
        try:
            openFastQCData = open("%s/fastqc_data.txt" % fastQCDataLocation, "r")
            fastQCDataLines = openFastQCData.readlines()
            openFastQCData.close()
            #strip all newline characters
            fastQCDataLines = map(lambda s: s.strip(), fastQCDataLines) 
        except:
            print "Cannot open or access the fastQC summary: %s/fastqc_data.txt" \
                                                                            % fastQCDataLocation
            print sys.exc_info()[0]
    elif fastQCSummaryObject != False:
        try:
            fastQCSummaryLines = fastQCSummaryObject[0]
            fastQCSummaryLines = map(lambda s: s.strip(), fastQCSummaryLines) 
            fastQCDataLines = fastQCSummaryObject[1]
            fastQCDataLines = map(lambda s: s.strip(), fastQCDataLines) 
        except:
            print "Unable to get data from the fastQCSummaryObject data"
    else:
        print "Unable to load any data."
        #sys.exit()
        raise

    
   
    #check that we have content
    if len(fastQCSummaryLines)==0: 
        #print fastQCSummaryLines
        print "Summary has no content" % fastQCDataLocation
        #sys.exit()
        raise
    if len(fastQCDataLines)==0:
        print "Data has no content" % fastQCDataLocation
        #sys.exit() 
    
    passWarnFailDict = {}
    #get all of the pass/warn/fail status from the summary
    for summaryLine in fastQCSummaryLines:
        splitLine = summaryLine.split("\t")

        if splitLine[1] == 'Basic Statistics':
            passWarnFailDict["basicStatistics"] = splitLine[0]

        elif splitLine[1] == 'Per base sequence quality':
            #show that we're in the baes sequence quality section to get the q30
            passWarnFailDict["baseSequenceQuality"] = splitLine[0]
        #this section loops over the base seq quality section to find the longest Q30
        #length. If you can think of a better way to do this, let me know!
        elif splitLine[1] == 'Per sequence quality scores':
            passWarnFailDict["sequenceQuality"] = splitLine[0]

        elif splitLine[1] == 'Per base sequence content':
            passWarnFailDict["baseSequenceContent"] = splitLine[0]

        elif splitLine[1] == 'Per base GC content':
            passWarnFailDict["baseGCContent"] = splitLine[0]

        elif splitLine[1] == 'Per sequence GC content':
            passWarnFailDict["sequenceGCContent"] = splitLine[0]

        elif splitLine[1] == 'Per base N content':
            passWarnFailDict["baseNContent"] = splitLine[0]

        elif splitLine[1] == 'Sequence Length Distribution':
            passWarnFailDict["lengthDistribution"] = splitLine[0]

        elif splitLine[1] == 'Sequence Duplication Levels':
            passWarnFailDict["duplicationLevels"] = splitLine[0]

        elif splitLine[1] == 'Overrepresented sequences':
            passWarnFailDict["overrepresentedSequences"] = splitLine[0]

        elif splitLine[1] == 'Kmer Content':
            passWarnFailDict["kmerContent"] = splitLine[0]

        elif splitLine[1] == 'Per tile sequence quality':
            passWarnFailDict["tileSequenceQuality"] = splitLine[0]

        elif splitLine[1] == 'Adapter Content':
            passWarnFailDict["adapterContent"] = splitLine[0]

        else:
            print "Error in fastqc summary.txt"
            #print splitLine
            #sys.exit()

    #go through the top of the fastqc_data.txt file and get the overview details we need.
    #total sequences.
    #filtered sequences
    #sequence length
    #%GC 
    #end on >>END_MODULE
    dataDict = {}
    #used for determining if we're in the base seequence quality section so we can get
    #the mean q30 length
    inBaseSeqQualSection = False
    q30Length = 0
    for dataLine in fastQCDataLines:
        splitDataLine = dataLine.split("\t")
        if splitDataLine[0] == 'Total Sequences':
            dataDict["totalSequences"] = splitDataLine[1]
        elif splitDataLine[0] == 'Filtered Sequences':
            dataDict["filteredSequences"] = splitDataLine[1]
        elif splitDataLine[0] == 'Sequence length':
            dataDict["sequenceLength"] = splitDataLine[1]
        elif splitDataLine[0] == '%GC':
            dataDict["percGC"] = splitDataLine[1]
        elif splitDataLine[0] == '>>Per base sequence quality':
            inBaseSeqQualSection = True 
        elif inBaseSeqQualSection == True:
            #if the section ends, move on
            if dataLine == ">>END_MODULE":
                break
            #skip the header
            elif "Mean" in dataLine:
                pass
            else:
                base = splitDataLine[0]
                meanQual = splitDataLine[1]
                #print meanQual
                #if the quality is over 30, record the longest place in sequence
                if float(meanQual) >= 30.0:
                    if "-" in base:
                        base = base.split("-")[1]
                    q30Length = base
                #if it's under 30, stop looking and continue
                elif float(meanQual) < 30.00:
                    inBaseQualSection = False
                    break


    #time to get the actual numbers out. This involves sectioning off all of the 
    #different parts between the >>HEADER and >>END_MODULE

    #join everything together so that we can split on >>END_MODULE\cr>>
    joinedData = "\n".join(fastQCDataLines).strip(">>END_MODULE")
    #split on >>END_MODULE\cr>>
    endModuleSplitData = joinedData.split(">>END_MODULE\n>>")
    #print joinedData
    #isolate sublists based on the first bit.
    fastQCSection = {}
    for section in endModuleSplitData:
        sectionLine = section.strip("\n").split("\n")
        theDataItself=[]
        for i,line in enumerate(sectionLine):
            if i==0:
                dataSection = "".join(line.split("\t")[0].split())
                #sorry. This gets the first element of the first line...
                #...then splits it into two by whitespace, then joins it into a single...
                #...string. Eg Kmer Content\tFail becomes KmerContent
            else:
                lineData = line.lstrip("#").split("\t")
                theDataItself.append(lineData)
            if i == (len(sectionLine)-1):
                fastQCSection[dataSection] = theDataItself
    

    #add the passWarnFail results to the data dictionary
    dataDict["passWarnFail"] = passWarnFailDict
    #add q30 length 
    dataDict["Q30Length"] = str(q30Length)
   #dataDict["fastQCData"] = fastQCSection
    #return dataDict
    return dataDict

def parseFastQScreenSummary( fastQScreenSummaryFile ):
    """Parses the fastQ screen summary file to get all of the relevant data
        about the contaminants in a sample.

        Returns a dictionary of the organism name (keys) and the percentages for
        each metric in a dictionary:
            Unmapped
            One_hit_one_library
            Multiple_hits_one_library
            One_hit_multiple_libraries
            Multiple_hits_multiple_libraries
        
        The exception to this is one entry in the dictionary with the key "HitsNoLibraries", 
        where the value is a single number (percentage).

    """

    fastQScreenSummary = openFileReadLines( fastQScreenSummaryFile )
    summaryOutput = {}
    if not re.match("#Fastq_screen version: .+", fastQScreenSummary[0]):
        raise Exception("Not a fastq screen summary file")    
 
    for line in fastQScreenSummary[2:]:#range is so we skip the header and version
        #split the line
        splitLine = line.split("\t")
        if len(splitLine) == 1:
            if splitLine[0] == "":
                pass #skipit
            elif splitLine[0].split(" ")[0] == "%Hits_no_libraries:":
                hitsNoLibsSplit = splitLine[0].splitline(" ")
                summaryOutput[ hitsNoLibsSplit[0].strip(":") ] = hitsNoLibsSplit[1] 
                #summaryOutput[ hitsNoLibsSplit[0].strip(":") ] = hitsNoLibsSplit[1] 
        else:
            
            Unmapped = splitLine[1].strip()
            One_hit_one_library = splitLine[2].strip()
            Multiple_hits_one_library = splitLine[3].strip()
            One_hit_multiple_libraries = splitLine[4].strip()
            Multiple_hits_multiple_libraries = splitLine[5].strip()

            summaryStatistics = {"Unmapped":Unmapped ,\
                          "One_hit_one_library":One_hit_one_library,\
                          "Multiple_hits_one_library": Multiple_hits_one_library,\
                          "One_hit_multiple_libraries": One_hit_multiple_libraries,\
                          "Multiple_hits_multiple_libraries":Multiple_hits_multiple_libraries}
            
            summaryOutput[ splitLine[0].strip(":") ] = summaryStatistics
    
    return summaryOutput
        #check if first element is hits no libraries
        #create the array
        #assign the array to the dictionary

        #if it is hits no libraries, handle it
        
        
    
    
def parseMD5Hash( md5FileLocation ):
    """Parses the md5 file given as input and returns a dictionary of it's content

        Return format:
        Dictionary keys are the file names, values are the md5 hash for the file

    """

    md5FileLines = openFileReadLines( md5FileLocation )

    md5Dict = {}
    for md5Line in md5FileLines:
        md5Split = md5Line.split("  ")
        md5Sum = md5Split[0]

        fileNameArray = md5Split[1].split("/")
        fileName = fileNameArray[-1]
        md5Dict[fileName] = md5Sum

    return md5Dict

def parseHiseqRunParameters( runParametersLocation ):
    """Parses the runParameters.xml file created by the hiseq/nextseq run to get some 
        essential details from it.a Input is the run Folder for a run.

        I'm really not expecting to ever need a lot of the data this provides.
        I collect it because why not? Metadata might be useful one day, even
        if it isn't, what's a few bytes, eh?
    
        Return dictionary keys:
        RTAVersion
        cameraDriver
        cameraFirmware
        sbsReagentKit
        peReagentKit
        indexReagentKit
        washBarcode
        controlSoftware
        FCPosition
        chemistryVersion
        length
        
    """

#    runParametersLine = openFileReadLines( runParametersLocation )

    try:
        runParametersXML = ElementTree.parse(runParametersLocation)
        runParameters = runParametersXML.getroot()
        runParameters = runParameters[0]
    except IOError:
        print "Cannot load information from %s" % runParametersLocation
        raise
    except ElementTree.ParseError:
        print "Invalid XML in %s" % runParametersLocation
        raise

    runParametersDict = {} 
        

    #length of the run
    for child in runParameters.iterfind("Read1"):
        runParametersDict["length"] =  child.text
    for child in runParameters.iterfind("PairEndFC"):
        if child.text == "true":
            runParametersDict["pairedSingle"] = "paired"
        else:
            runParametersDict["pairedSingle"] = "single"
    #flow cell position
    for child in runParameters.iterfind("FCPosition"):
        runParametersDict["FCPosition"] = child.text
    #software versions
    #Version of the hiseq control software used
    for child in runParameters.iterfind("ApplicationVersion"):
        runParametersDict["controlSoftware"] = child.text
    #camera firmware version
    for child in runParameters.iterfind("CameraFirmware"):
        runParametersDict["cameraFirmware"] = child.text
    #camera driver version
    for child in runParameters.iterfind("CameraDriver"):
        runParametersDict["cameraDriver"] = child.text
    #rta version
    for child in runParameters.iterfind("RTAVersion"):
        runParametersDict["RTAVersion"] = child.text
    #barcode for the wash flow cell.
    for child in runParameters.iterfind("WashBarcode"):
        runParametersDict["washBarcode"] = child.text
    #chemistry version
    for child in runParameters.iterfind("ChemistryVersion"):
        runParametersDict["chemistryVersion"] = child.text
    
    #PITA finding the kit IDs as they're nested.
    for reagentKit in runParameters.iterfind("ReagentKits"):
        #get the sbs kit id
        for sbsKit in reagentKit.iterfind("Sbs"):
            for kit in sbsKit.iterfind("SbsReagentKit"):
                for id in kit.iterfind("ID"):
                    runParametersDict["sbsReagentKit"] = id.text
        #index kit id
        for indexKit in reagentKit.iterfind("Index"):
            for kit in indexKit.iterfind("ReagentKit"):
                for id in kit.iterfind("ID"):
                    runParametersDict["indexReagentKit"] = id.text
        #paired end kit id
        for peKit in reagentKit.iterfind("Pe"):
            for kit in peKit.iterfind("ReagentKit"):
                for id in kit.iterfind("ID"):
                    runParametersDict["peReagentKit"] = id.text
    
    return runParametersDict

def parseNextSeqRunParameters( runParametersLocation ):
    """Parses the runParameters.xml file created by the hiseq/nextseq run to get some 
        essential details from it.a Input is the run Folder for a run.

        I'm really not expecting to ever need a lot of the data this provides.
        I collect it because why not? Metadata might be useful one day, even
        if it isn't, what's a few bytes, eh?
    
        Return dictionary keys:
        RTAVersion
        cameraDriver
        cameraFirmware
        sbsReagentKit
        peReagentKit
        indexReagentKit
        washBarcode
        controlSoftware
        FCPosition
        chemistryVersion
        length
        
    """

#    runParametersLine = openFileReadLines( runParametersLocation )

    try:
        runParametersXML = ElementTree.parse(runParametersLocation)
        runParameters = runParametersXML.getroot()
    except IOError:
        print "Cannot load information from %s" % runParametersLocation
        raise
    except ElementTree.ParseError:
        print "Invalid XML in %s" % runParametersLocation
        raise

    runParametersDict = {} 
    runParametersSetup = runParameters[1]
        

    #length of the run
    for child in runParametersSetup.iterfind("Read1"):
        runParametersDict["length"] =  child.text
    #software versions
    #Version of the hiseq control software used
    for child in runParametersSetup.iterfind("ApplicationVersion"):
        runParametersDict["controlSoftware"] = child.text
    #barcode for the wash flow cell.
    for child in runParametersSetup.iterfind("SystemSuiteVersion"):
        runParametersDict["SystemSuiteVersion"] = child.text
    #chemistry version
    for child in runParameters.iterfind("Chemistry"):
        runParametersDict["Chemistry"] = child.text
    #rta version
    for child in runParameters.iterfind("RTAVersion"):
        runParametersDict["RTAVersion"] = child.text
    
    #get the kit serials
    for pr2Serial in runParameters.iterfind("PR2BottleSerial"):
         runParametersDict["PR2BottleSerial"] = pr2Serial.text
    for reagentKit in runParameters.iterfind("ReagentKitSerial"):
         runParametersDict["ReagentKitSerial"] = reagentKit.text
    
    #paired end or not
    for pairedEnd in runParameters.iterfind("IsPairedEnd"):
        runParametersDict["IsPairedEnd"] = pairedEnd.text
    #basespacerunId
    for basespace in runParameters.iterfind("BaseSpaceRunID"):
        runParametersDict["BaseSpaceRunID"] = basespace.text
   
    return runParametersDict


def parseInterOp( runFolderLocation ):
    """Use the illuminate package to parse the interop folder from the run for cluster
        density and the like.

        Return dictionary keys are the lane number, value is a dictionary with the keys:
        clusterDensity
        clusterDensityStdDev
        clusterPFDensity
        clusterPFDensityStdDev
        numClusters
        numClustersStdDev
        numClustersPF
        numClustersPFStdDev
        firstBaseReportDensity
    
    """

    try:
        from illuminate import InteropDataset
        from numpy import mean, std
    except ImportError, e:
        print "Cannot import illuminate"
        raise

    #Parse the interop files for the clusterDensity information.
    try:
        interOpObject = InteropDataset( runFolderLocation )
    except:
        print "Cannot load InterOp data from %s" % runFolderLocation
        raise

    #Get the details of the first base report for the lane
    #try:
    #    firstBaseReport = parseFirstBaseReport( runFolderLocation )
    #except IOError:
    #    print "Cannot load first base report from %s" % runFolderLocation
    #    raise

    #get the tile metrics specifically
    tileMetrics = interOpObject.TileMetrics()
    #as it's done on a tile bases, gather the tiles into dicts
    #keys are the lanes
    densityDict = {}
    densityPFDict = {}
    numClustersDict = {}
    numClustersPFDict = {}
    tileMetricsOutputDict = {} # dictionary that is returned
    #collect the set of lanes, means it scales with more or less lanes on a flowcell.
    #*smug*
    for lane in set(tileMetrics.data["lane"]):
        densityDict[lane] = []
        densityPFDict[lane] = []
        numClustersDict[lane] = []
        numClustersPFDict[lane] = []
        #initialise the output dictionary.  Used later for looping
        tileMetricsOutputDict[lane] = []
    
    #loop over the data
    #code 100 is the cluster density, 1010 is the pass filter density
    #102 is the number of clusters and 103 is the number of cluster passing filter
    for index,value in enumerate(tileMetrics.data["lane"]):
        #density
        if tileMetrics.data["code"][index] == 100:
            densityDict[value].append( tileMetrics.data["value"][index] )
        #density passing filter
        elif tileMetrics.data["code"][index] == 101:
            densityPFDict[value].append( tileMetrics.data["value"][index] )
        #number of clusters
        elif tileMetrics.data["code"][index] == 102:
            numClustersDict[value].append( tileMetrics.data["value"][index] )
        #number of clusters passing filter
        elif tileMetrics.data["code"][index] == 103:
            numClustersPFDict[value].append( tileMetrics.data["value"][index] )
    
    #but we've only got the metrics for each tile, not the whole lane
    #so we need to do...*DUN DUN DUUUUUUN* MATHS!
    #loop over each of the lanes in the flow cell.
    for lane in tileMetricsOutputDict:
        
        clusterDensity = int(round(mean(densityDict[int(lane)])/1000))
        clusterDensityStdDev = int(round(std(densityDict[int(lane)])/1000))
        clusterPFDensity = int(round(mean(densityPFDict[int(lane)])/1000))
        clusterPFDensityStdDev = int(round(std(densityPFDict[int(lane)])/1000))
        numClusters = int(round(mean(numClustersDict[int(lane)])/1000))
        numClustersStdDev =  int(round(std(numClustersDict[int(lane)])/1000))
        numClustersPF = int(round(mean(numClustersPFDict[int(lane)])/1000))
        numClustersPFStdDev = int(round(std(numClustersPFDict[int(lane)])/1000))

        laneDict = { \
                "clusterDensity":clusterDensity, \
                "clusterDensityStdDev":clusterDensityStdDev, \
                "clusterPFDensity":clusterPFDensity, \
                "clusterPFDensityStdDev":clusterPFDensityStdDev, \
                "numClusters":numClusters, \
                "numClustersStdDev":numClustersStdDev, \
                "numClustersPF":numClustersPF, \
                "numClustersPFStdDev":numClustersPFStdDev,\
                "firstBaseDensity":0 } #TODO
        tileMetricsOutputDict[lane] = laneDict
    #
    #percPassingFilter = numClustersPF / numClusters * 100

    return tileMetricsOutputDict
    
def parseFirstBaseReport( runFolderLocation ):
    """Finds the first base report that's located in the given run folder location
       Returns a dict of the cluster densities from the first base report

    """

    firstBaseReportLocation = "%s/First_Base_Report.htm" % runFolderLocation
 
    #load data from the file 
    try:
        openTargetFile = open(firstBaseReportLocation, "r")
        targetFileLines = openTargetFile.readlines()
        openTargetFile.close()
        #strip all newline characters
        targetFileLines = map(lambda s: s.strip('\r\n'), targetFileLines) 
    except IOError:
        print "Cannot open or access the file: %s" % firstBaseReportLocation
        raise

    firstBaseReport = targetFileLines
    
    tableStart = firstBaseReport.index('<table border="1" cellpadding="5">')
    tableEnd = firstBaseReport.index('</table>')
    
    reportTable = firstBaseReport[tableStart:tableEnd]
    
    clusDensitySubstr="Cluster Density"
    headerSubstr="Metric"
    densityDict = {}
    for line in reportTable:
        if headerSubstr in line:
            headerLine = line.split("</td><td>")[1:]
    
        elif clusDensitySubstr in line:
            densityLine = line.split("</td><td>")[1:]
    #some parsing of the lists we just made and put them into the dictionary
    headerLine[-1] = headerLine[-1].rstrip('</td></tr>')
    for item in headerLine:
        densityDict[ int(item.lstrip("Lane "))] = 0
    densityLine[-1] = densityLine[-1].rstrip('</td></tr>')
    for index,value in enumerate(densityLine):
        densityDict[index+1] = float(value)
    
    return densityDict

    

def parseDemultiplexConfig( demultiplexConfigFile ):
    """Parses the DemultiplexConfig file for the version of casava used

        Output is the details of the software in the format:
        [softwareName, softwareVersion, softwareArguements]
        [bcl2fastq, 1.8.4, "cluster/gsu/data/hiseq/140506_SN7001398_0099_BC4362ACXX/Data/Intensities/BaseCalls --output-dir /cluster/gsu/data/processed/hiseq/140506_SN7001398_0099_BC4362ACXX/ --sample-sheet /homes/gsupipe-x/SampleSheets/140506_SN7001398_0099_BC4362ACXX/SampleSheet_revComp_edited.csv --use-bases-mask Y*,I8n*,Y*'"]

    """
    casavaDetails = []
    demultiplexConfigXML = ElementTree.parse(demultiplexConfigFile)
    for softwareDetails in demultiplexConfigXML.iterfind("Software"):
        versionString = softwareDetails.attrib["Version"]
        commandArgs = softwareDetails.attrib["CmdAndArgs"]

    casavaDetails.append( versionString.split("-")[0] )
    casavaDetails.append( versionString.split("-")[1] )
    casavaDetails.append( commandArgs )

    return casavaDetails
    
        
   # for line in demultiplexConfigFile:

def generateLatexFile( sampleName, destinationFolder, fastQCFolder, runName, q30Length ):
    """Generates pdf summary files for the sample, given the fastQC folder location

    """
    #eventually and ideally this will just be written in python.
    #for now though, we'll just use what we've got in bash. 
    pdfGeneratorScript = "pdfGenerator.sh"
    print pdfGeneratorScript
    #script takes the inputs:
    #fastqcFolderPath, runFolderName, q30 length
    pdfGeneratorArguements = [pdfGeneratorScript, fastQCFolder, destinationFolder, runName, q30Length]
    print pdfGeneratorArguements
    try:
        pdfGeneratorProcess = subprocess.check_call( pdfGeneratorArguements )
    except:
        print ("Failed to generate pdf file for %s") % fastQCFolder
        #sys.exit(1)
        raise

    latexFileName = "%s.pdf" % fastQCFolder.strip("_fastqc")
    return latexFileName


    
############### Parsing undetermined Reads #########################
def parseUndeterminedReads( undetReadFileOne, maxBarcodes=10 ):
    """Reads through the given fastq file and tracks the most common 
        barcodes in the file

        Returns a dict with the number in the top 10 as the key and the 
        [barcode, occurances] as the values. 

        First arguement is required, the second argument is optional for
        single end runs. You can change the number of barcodes produced by changing
        maxBarcodes (default 10) 

    """
    #input checks
    try:
        val = int(maxBarcodes)
        #maxBarcodes.isdigit()
    except ValueError, e:
        print e
        raise

    #regex for finding barcodes from fastq files
    fastqReadBarcode = re.compile("^\@(\S+) (\S+)\:(\S{6,17})$") 

    #check the first file exists
    allBarcodes = {} 
   # try:
    totalUndet = 0

    barcodes = []
    #took me ages to work this out. Turns it from hours to minutes.
    with gzip.open(undetReadFileOne) as undetGzip:
        for line in undetGzip.readlines()[::4]:
                    barcodes.append(line.strip().split(":")[-1])

    #uniqueBarcodes = barcodes.unique()
    totalUndet = len(barcodes)
    counter = Counter( barcodes )

    for undetPair in counter.items():
        allBarcodes[undetPair[0]] = undetPair[1]

    sortedBarcodes = sorted(allBarcodes, key = allBarcodes.get, reverse = True)
   
    topBarcodeOutput = {}
    for index,topBarcode in enumerate(sortedBarcodes[0:maxBarcodes]):
        topBarcodeOutput[ index + 1 ] = [topBarcode, allBarcodes[ topBarcode ] ]
        
    return totalUndet, topBarcodeOutput

def getDateFromRun( runName ):
    """Get the run date from the run folder name"""
    runNameSplit = runName.split("_")
    date_unparsed = runNameSplit[0]
    date = datetime.date(year=int("20%s" % date_unparsed[0:2]), month=int(date_unparsed[2:4]),\
                            day=int(date_unparsed[4:6]))
    return( date )

def createMediaFolder( runName ):
    """creates a run folder based on the run name given, if one doesn't already exist,
        that is located in the django media folder location"""
    mediaFolder = settings.MEDIA_ROOT
    print mediaFolder
    currentMediaFolder = os.path.join(mediaFolder, runName)
    try:
        if not os.path.exists( currentMediaFolder ):
            os.mkdir( currentMediaFolder )
    except:
        print "Cannot create media folder: %s" % currentMediaFolder

    return currentMediaFolder    

def moveFileToMediaFolder( filePath, destinationFolder ):
    """Moves the input file to the destination Folder"""
    try:
        shutil.copy(filePath, destinationFolder)
    except:
        print "Cannot copy %s to %s" %(filePath, destinationFolder)
    
    
################################################################################

#Add NextSeq run to AlmostSignificant
def addNextSeqRun( runLocation, rawLocation, qCFolder, machineType="nextseq", checkUndetIndicies=False):
    """Add a nextSeq run to AlmostSignificant
    First arguement is the bcl2fastq output folder
    Second arguement is the location for the raw data from the machine, including
    the sample sheet.
    Third location is a single folder that contains the fastQC and fastQScreen 
    files for all of the fastQ files

    """
    
    runName = runLocation.split("/")[-2]
    machineName, flowCellID = runName.split("_")[1:3]
    #gather the information from the sample sheet
    sampleSheetLocation = "/".join([rawLocation,"SampleSheet.csv"])

    ## Section specific to machine type: Nextseq or Hiseq
    if machineType.lower() == "nextseq":
        #nextseq data gathering
        sampleSheetData = parseNextseqSampleSheet(sampleSheetLocation)
        machineType = "NextSeq"
        runParameters = parseNextSeqRunParameters( "".join([rawLocation,"RunParameters.xml"]) )
        softwareToAdd = ["PR2BottleSerial", "Chemistry", "ReagentKitSerial", "controlSoftware", "RTAVersion"]


        length = sampleSheetData["Reads"]["read1"]#samplesheet
        if "read2" in sampleSheetData["Reads"]:
            pairedSingle = "paired"#samplesheet
        else:
            pairedSingle = "single"
        FCPosition = 1
        seqLanes = [1,2,3,4] #how many lanes the nextseq can potentially have

    elif machineType.lower() == "hiseq":
        #hiseq data gathering
        sampleSheetData = parseHiseqSampleSheet(sampleSheetLocation)
        machineType = "HiSeq"
        runParameters = parseHiseqRunParameters( "".join([rawLocation,"runParameters.xml"]) )
        softwareToAdd = [ "RTAVersion", "cameraDriver", "cameraFirmware", "sbsReagentKit",\
                         "washBarcode", "controlSoftware", "FCPosition", "chemistryVersion"]


        length = runParameters["length"]
        pairedSingle = runParameters["pairedSingle"]
        FCPosition = runParameters["FCPosition"]
        seqLanes = [1,2,3,4,5,6,7,8] #how many lanes the nextseq can potentially have
    else:
        #throw a tantrum
        print "InputMachineType of %s not elegible. Please use nextseq (default) or hiseq" % machineType
        #sys.exit(1)

    
    
    
    #Run parameters
    machine = machineName #from run name
    #machineType defined in machineType section
    date = getDateFromRun( runName )
    alias = "" #? can't remember what this was intended for. Keeping is as useful later?

    #Add run to AlmostSignificant
    print "Adding Run"
    runDetails = {"runName":runName, "machine":machine, "machineType":machineType, "date":date,\
                    "alias":alias, "length":length, "pairedSingle":pairedSingle, "fcPosition":FCPosition}
    thisRun = addRunToDatabase( runDetails )
    run_id = thisRun.id

    #gathing InterOp data
    interOpData = parseInterOp( rawLocation )
#
    #define the destination of the media files for putting files in later
    mediaFolder = createMediaFolder( thisRun.runName )
    #Undetermined indexes
    totalUndetsForRun = {}
    undetIndiciesForRun = {}
    if checkUndetIndicies == True:
        #find all the undetermined index files
        #now initiated in the machinechecking loop
        #SeqLanes = [1,2,3,4] #how many lanes the nextseq can potentially have
        #nextSeqLanes = [1] #how many lanes the nextseq can potentially have
        for currentLane in seqLanes: #for each of the potential lanes
            if machineType == "NextSeq":
                currentUndetFile = "%s/Undetermined_S0_L00%d_R1_001.fastq.gz" % (runLocation, currentLane )
            elif machineType == "HiSeq":
                currentUndetFile = "%s/Undetermined_indices/Sample_lane%s/lane%s_Undetermined_L00%s_R1_001.fastq.gz" \
                                                                % (runLocation, currentLane, currentLane, currentLane )
            #if the file exists
            if os.path.exists( currentUndetFile ):
                #run parseUndeterminedReads and add it to the undetIndiciesForRun array under the lane num
                print "Checking Undetermined Indicies for %s" % currentUndetFile
                totalUndetsForRun[currentLane], undetIndiciesForRun[currentLane] = parseUndeterminedReads( currentUndetFile ) 
            else:
                #occasionally, if a run has no barcodes, there isn't any undetermined reads, so deal with this
                #by setting everything to 0 if the undetermined index file doesn't exist
                totalUndetsForRun[currentLane] = "0" 
                undetIndiciesForRun[currentLane] = {1:["-","0"], 2:["-","0"], 3:["-","0"], 4:["-","0"], 5:["-","0"], 6:["-","0"], 7:["-","0"], 8:["-","0"], 9:["-","0"], 10:["-","0"] }
                
                
    else:
        #sets all lanes to have a undertermined indicies total of 0 for the top 10
        emptyUndetIndicies =  {1:["-","0"], 2:["-","0"], 3:["-","0"], 4:["-","0"], 5:["-","0"], 6:["-","0"], 7:["-","0"], 8:["-","0"], 9:["-","0"], 10:["-","0"] }
        undetIndiciesForRun =  {1: emptyUndetIndicies, 2: emptyUndetIndicies, 3: emptyUndetIndicies , 4: emptyUndetIndicies ,\
                                5: emptyUndetIndicies, 6: emptyUndetIndicies, 7: emptyUndetIndicies, 8: emptyUndetIndicies ,\
                                9: emptyUndetIndicies, 10: emptyUndetIndicies }
        #sets all lanes to have a total undertermined indicies total of 0 for the top 10
        totalUndetsForRun = {1:"0",2:"0",3:"0",4:"0",5:"0",6:"0",7:"0",8:"0",9:"0",10:"0"}
    print totalUndetsForRun
#   #Lane Parameters
    print "Adding Lanes"
    for lane, laneData in interOpData.iteritems():
        print lane
        thisLane = {"run_id":run_id, "lane":lane, \
                            "ClusterPFDensity":laneData["clusterPFDensity"],\
                            "percPassingFilter": (laneData["numClustersPF"] / laneData["numClusters"] * 100), \
                            "readsPassingFilter":0,\
                            "totalUndetIndexes":totalUndetsForRun[lane],\
                            "percentOverQ30":0,\
                            "numClusters":laneData["numClusters"],\
                            "clusterDensity":laneData["clusterDensity"], \
                            "clusterDensityStdDev":laneData["clusterDensityStdDev"],\
                            "clusterPFDensity":laneData["clusterPFDensity"],\
                            "clusterPFDensityStdDev":laneData["clusterPFDensityStdDev"],\
                            "firstBaseDensity":laneData["firstBaseDensity"],\
                            "numClustersStdDev": laneData["numClustersStdDev"],\
                            "numClustersPF": laneData["numClustersPF"], \
                            "numClustersPFStdDev": laneData["numClustersPFStdDev"]}
        thisLane = addLaneToDatabase( thisLane )
        interOpData[lane]["lane"] = thisLane
        interOpData[lane]["lane_id"] = thisLane.id
        #print lane,thisLaneID, run_id
        #setup the undetermined indicies
        if checkUndetIndicies == False:
            addUndetIndicesToDatabase( undetIndiciesForRun[lane], interOpData[lane]["lane_id"] )
        else:
            print "undetIndiciesForRun"
            print undetIndiciesForRun
            print "##########"
            addUndetIndicesToDatabase( undetIndiciesForRun[lane], interOpData[lane]["lane_id"], forceUpdate=True )

    ### Software ###
    #loop over currentSample software
    software_object_array = []
    #0 is the software, 1 is the version, 2 is the parameters
    #runParameteters now defined at start of function in the machine type checking section
        #runParameters = parseNextSeqRunParameters( "".join([rawLocation,"RunParameters.xml"]) )
        #Nextseq Control Software version and name
        #we now have: PR2BottleSerial, Chemistry, ReagentKitSerial, ControlSoftware, RTAVersion
        #softwareToAdd = ["PR2BottleSerial", "Chemistry", "ReagentKitSerial", "controlSoftware", "RTAVersion"]
    #loop over the software to add and generate or collect the software objects into an array
    for currentSoftware in softwareToAdd:
        software_object_array.append( addSoftwareToDatabase(currentSoftware, runParameters[currentSoftware] )) 
    
    ###########Sample#################

    #get md5 hashes from file. Assumes md5hashes.txt in run folder
    md5HashFile = "%s/%s" %( runLocation, "md5hashes.txt")
    if os.path.exists( md5HashFile ):
        md5Hashes = parseMD5Hash( md5HashFile )
#        md5Exists = True
    else:
        md5Hashes = False
        
    #Use the sampleSheet data. 
    #Either do it by Sample, or by file. By sample may be easier.
    #that way can do read 1 then 2.
    #initiate the search strings for lane and read numbers
    readNumberSearchString = re.compile('_R(\d)_') #As before
    laneNumberSearchString = re.compile('_L00(\d)_') #As before
    print "Adding Samples"
    #print sampleSheetData["Data"]
    #loop over each sample in the samplesheet
    #print sampleSheetData["Data"]
    for currentSampleName, currentSample in sampleSheetData["Data"].iteritems():
        #print currentSample
        sampleData = {} # initiate the dict
        #for each of the samples, gather the appropriate data
        sampleData["thisRun"] = thisRun #generated when we create the run in the db
        #either retrieve or generate the Project Stuff
        projectDetails = {"projectName":currentSample["Sample_Project"],\
                                    "owner":sampleSheetData["Header"]["Investigator Name"],\
                                    "projectPROID":None,"projectMISOID":None,\
                                    "description":currentSample["Description"] }
        sampleData["thisProject"] = addProjectToDatabase( projectDetails )

        sampleData["sampleReference"] = currentSample["Sample_ID"] #ss
        sampleData["sampleName"] = currentSampleName #ss
        sampleData["sampleDescription"] = currentSample["Description"]#ss
        sampleData["barcode"] = currentSample["index"] # ss
        #find the location in the run folder for the project
        #now defined in the machine checking section at the start
        if machineType == "NextSeq":
            projectFolder = "".join([runLocation, currentSample["Sample_Project"]])
        elif machineType == "HiSeq":
            projectFolder = "".join([runLocation, "Project_", currentSample["Sample_Project"]])
        #loop over every file in the folder
        #need to add to AS here as it deals with lanes and read number
        for root, dirs, fastqFiles in os.walk( projectFolder ):
            for fastqFile in fastqFiles:
                #Illumina. Why. You replace all of the _ in sample names with -. 
                #This wouldn't be so bad, but fastqc and illumina then add more _ into the name
                #which bones over my searches and makes my life harder. 
                pattern = "".join([sampleData["sampleReference"], "_*.fastq.gz"])
                patternDash = "".join([sampleData["sampleReference"].replace("_","-"), "_*.fastq.gz"]) #sigh, illumina
                if (fnmatch.fnmatch(fastqFile, pattern))\
                or (fnmatch.fnmatch(fastqFile, patternDash)): #sigh, illumina
                    if fnmatch.fnmatch(fastqFile, patternDash):
                        sampleData["sampleReference"] = sampleData["sampleReference"].replace("_","-")
                    print fastqFile
                    fastQScreenSummary = "" #set this for later
                    #get read number
                    sampleData["readNumber"] = readNumberSearchString.search(fastqFile).group(1)
                    #get lane number by searching the file name for it, then retrieve the lane object created earlier
                    laneNumber = int(laneNumberSearchString.search(fastqFile).group(1))
                    sampleData["thisLane"] = interOpData[laneNumber]["lane"]
                    sampleData["fastQLocation"] = os.path.join([root,fastqFile])
                    sampleData["contaminantsLink"] = "Null" #default to null, update later if we find a file
                    if md5Hashes != False:
                        if fastqFile in md5Hashes.keys():
                            sampleData["md5Hash"] = md5Hashes[fastqFile]
                        else:
                            sampleData["md5Hash"] = ""
                    else:
                        sampleData["md5Hash"] = ""
    
                    fileCoreName = fastqFile.split(".")[0]
                    for root, dirs, allQCFiles in os.walk(qCFolder):
                        #format is SampleRef_S*_L00*_R*_00*_fastqc
                        fastQCZipName = "%s_*_L00%s_R%s_*_fastqc.zip" %(  \
                                                sampleData["sampleReference"],\
                                                sampleData["thisLane"],\
                                                sampleData["readNumber"])
                        for currentQCFile in allQCFiles:
                            if fnmatch.fnmatch(currentQCFile, fastQCZipName):
                                print currentQCFile, fastQCZipName
                                #parse the fastqc results. 
                                currentFastQCZip = loadFastQCZip( "%s/%s" %( root, currentQCFile ) )
                                parsedQC = parseFastQCData(fastQCSummaryObject=currentFastQCZip) 
                                sampleData["reads"] = parsedQC["totalSequences"] #fastqc?
                                sampleData["sequenceLength"] = parsedQC["sequenceLength"]#fastqc
                                sampleData["filteredSequences"] = parsedQC["filteredSequences"]#fqc
                                sampleData["percentGC"] = parsedQC["percGC"]#fqc
                                sampleData["sequenceQuality"] = parsedQC["passWarnFail"]["sequenceQuality"]#fqc
                                sampleData["sequenceQualityScores"] = parsedQC["passWarnFail"]["sequenceQuality"]#fqc
                                sampleData["sequenceContent"] = parsedQC["passWarnFail"]["sequenceGCContent"]#fqc
                                sampleData["GCContent"] = parsedQC["passWarnFail"]["baseGCContent"]#fqc
                                sampleData["baseNContent"] = parsedQC["passWarnFail"]["baseNContent"]#fqc
                                sampleData["sequenceLengthDistribution"] = parsedQC["passWarnFail"]["lengthDistribution"]#fqc
                                sampleData["sequenceDuplicationLevels"] = parsedQC["passWarnFail"]["duplicationLevels"]#fqc
                                sampleData["overrepresentedSequences"] = parsedQC["passWarnFail"]["overrepresentedSequences"]#fqc
                                sampleData["kmerContent"]= parsedQC["passWarnFail"]["kmerContent"]  #fqc
                                sampleData["Q30Length"] = parsedQC["Q30Length"]
                                sampleData["QCStatus"] = "Pending" #TODO
                                
                                fastQCFolder = "%s/%s" %( root, currentQCFile.strip(".zip") )
                                #uncomment
                                #generate pdf file and then copy it to the media folder
                                currentLatexFile = generateLatexFile( sampleData["sampleReference"], mediaFolder,\
                                                    fastQCFolder, runName, sampleData["Q30Length"] )
                                #moveFileToMediaFolder( currentLatexFile, mediaFolder )    
                                sampleData["fastQCLink"] = "%s/%s" %(runName, os.path.split(currentLatexFile)[-1]) #this is the pdf file.


                            fastQScreenSummaryImageName = "%s_*_L00%s_R%s_*_screen.png" %(  \
                                                    sampleData["sampleReference"],\
                                                    sampleData["thisLane"],\
                                                    sampleData["readNumber"])
                       #    contaminants 
                            if fnmatch.fnmatch(currentQCFile, fastQScreenSummaryImageName):
                                #generate the name for the data file
                                fastQScreenSummaryDataName = currentQCFile.replace(".png",".txt")
                                #parse the fastqscreen summary
                                sampleData["contaminantsLink"] = "%s/%s" %( runName, currentQCFile )#search?
                                fastQScreenSummary = parseFastQScreenSummary( "%s/%s" %( root, fastQScreenSummaryDataName  ) )
                                #copy over the fastqscreen file to the media folder
                                moveFileToMediaFolder( os.path.join(root,currentQCFile), mediaFolder )    
    
                            sampleData["libraryReference"] = "N/A" #doesn't exist
                            sampleData["species"] = "Unknown"# cant currently do with Andy's excel sheet (Oct 15)
                            sampleData["method"] = sampleSheetData["Header"]["Assay"] # cant currently do with Andy's excel sheet (Oct 15)
                            sampleData["insertLength"] = 0# cant currently do with Andy's excel sheet (Oct 15)
                            #copy fastqscreen and pdf files
        
                    sample = addSampleToDatabase( sampleData, software_object_array )
                    addContaminantsDetailsToDatabase( fastQScreenSummary, sample.id )
                    
    

################################################################################

## Functions for adding information to the database

################################################################################
def addSoftwareToDatabase( softwareName, softwareVersion, softwareParameters="" ):
    """Gets or creates a software database entry for the current settinngs.
        Takes three parameters for the software: name, version, parameters
        where the default parameters is \"\"
    """

    try:
        currentSoftware = Software.objects.get( softwareName=softwareName,\
                                                        version=softwareVersion,\
                                                        parameters=softwareParameters )
    except django.core.exceptions.ObjectDoesNotExist:
        currentSoftware = Software(softwareName=softwareName,\
                                        version=softwareVersion,\
                                        parameters=softwareParameters )
        currentSoftware.save()
 
    return currentSoftware
        
        
def addRunToDatabase( runData ):
    """Checks if a run exists or creates the run. 
        Input is dict of the information.
        Keys:
        runName
        machine, machineType, date, alias, length
        pairedSingle, FCPosition, 
        Returns the runID
        """
    #Add run to AlmostSignificant
    try:
        #print runData["runName"]
        thisRun = Run.objects.get(runName=runData["runName"])
        thisRun.machine = runData["machine"]
        thisRun.machineType = runData["machineType"]
        thisRun.date = runData["date"]
        thisRun.alias = runData["alias"]
        thisRun.length = runData["length"]
        thisRun.pairedSingle = runData["pairedSingle"]
        thisRun.fcPosition = runData["fcPosition"]
        thisRun.save()
    except:
        #construct the run for saving
        thisRun = Run( runName=runData["runName"], machine=runData["machine"],\
                     machineType=runData["machineType"], date=runData["date"],\
                     alias=runData["alias"], length=runData["length"],\
                     pairedSingle=runData["pairedSingle"], fcPosition = runData["fcPosition"] )
        thisRun.save()
    
    return thisRun



def addLaneToDatabase( laneData ):
    """Checks if a lane exists or creates the lane.
        Input is a dict of information
        Keys:
        run_id
        lane
        ClusterPFDensity
        percPassingFilter
        readsPassingFilter
        totalUndetIndexes
        percentOverQ30
        numClusters
        clusterDensity
        clusterDensityStdDev
        clusterPFDensityStdDev
        firstBaseDensity
        numClustersStdDev
        numClustersPF
        numClustersPFStdDev
       
    """
    try:
        #add stuff to the actual database.
        thisLane = Lane.objects.get(lane=laneData["lane"], run_id=laneData["run_id"])
        thisLane.ClusterPFDensity = laneData["clusterPFDensity"]
        thisLane.clusterPFDensityStdDev = laneData["clusterPFDensityStdDev"]
        thisLane.clusterDensity = laneData["clusterDensity"]
        thisLane.clusterDensityStdDev = laneData["clusterDensityStdDev"]
        thisLane.numClusters = laneData["numClusters"]
        thisLane.numClustersStdDev = laneData["numClustersStdDev"]
        thisLane.numClustersPF = laneData["numClustersPF"]
        thisLane.numClustersPFStdDev = laneData["numClustersPFStdDev"]
        thisLane.percPassingFilter = laneData["percPassingFilter"]
        thisLane.readsPassingFilter = laneData["readsPassingFilter"]
        thisLane.percentOverQ30 = laneData["percentOverQ30"]
        thisLane.totalUndetIndexes = laneData["totalUndetIndexes"]
        thisLane.save()
    except:
        #calculate the last few things we need to know
        thisLane = Lane(run_id=laneData["run_id"], lane=laneData["lane"],\
                            ClusterPFDensity=laneData["clusterPFDensity"],\
                            percPassingFilter=laneData["percPassingFilter"],\
                            readsPassingFilter=laneData["readsPassingFilter"],\
                            totalUndetIndexes=laneData["totalUndetIndexes"],\
                            percentOverQ30=laneData["percentOverQ30"],\
                            numClusters = laneData["numClusters"],\
                            clusterDensity=laneData["clusterDensity"], \
                            clusterDensityStdDev=laneData["clusterDensityStdDev"],\
                            clusterPFDensityStdDev=laneData["clusterPFDensityStdDev"],\
                            firstBaseDensity=laneData["firstBaseDensity"],\
                            numClustersStdDev = laneData["numClustersStdDev"],\
                            numClustersPF = laneData["numClustersPF"], \
                            numClustersPFStdDev = laneData["numClustersPFStdDev"])
        thisLane.save()

    return thisLane

def addProjectToDatabase( projectData ):
    """Adds the project to the database
    Input is a dict containing: projectName, projectMISOID, projectPROID, owner,description
        """
    try:
        thisProject = Project.objects.get(project=projectData["projectName"])
        thisProject.projectMISOID = projectData["projectMISOID"]
        thisProject.projectPROID = projectData["projectPROID"]
        thisProject.owner = projectData["owner"]
        thisProject.description = projectData["description"]
        thisProject.save()

    except django.core.exceptions.ObjectDoesNotExist:
        thisProject = Project(project=projectData["projectName"], projectMISOID=projectData["projectMISOID"], \
                            projectPROID=projectData["projectPROID"], owner=projectData["owner"], \
                            description=projectData["description"])
        thisProject.save()

    return thisProject
    

    
def addSampleToDatabase( sampleData, software_object_array ):
    """Add the sample to the database if it doesn't exist.
        input dict:
        
        run
        project, lane, 
        sampleReference, sampleName, 
        readNumber, reads
        sequenceLength, sampleDescription, 
        libraryReference, barcode, 
        species, method
        fastQLocation, md5hash, 
        QCStatus, insertLength, 
        contaminantsImage, fastQCSummary
        filteredSequences, Q30Length, 
        percentGC, sequenceQuality, 
        sequenceQualityScores, sequenceContent
        GCContent, baseNContent, 
        sequenceLengthDistribution, sequenceDuplicationLevels, 
        overrepresentedSequences, kmerContent

        software_object_array is an array of software objects (eg those
        generated by addSoftwareToDatabase) to link with the sample
    """
    try:
        thisSample = Sample.objects.get(sampleReference=sampleData["sampleReference"],\
                                        sampleName=sampleData["sampleName"],\
                                        run_id=sampleData["thisRun"],\
                                        lane_id=sampleData["thisLane"],\
                                        project_id=sampleData["thisProject"],\
                                        libraryReference=sampleData["libraryReference"],\
                                        readNumber=sampleData["readNumber"])
        thisSample.readNumber = sampleData["readNumber"]
        thisSample.reads = sampleData["reads"]
        thisSample.sequenceLength = sampleData["sequenceLength"]
        thisSample.sampleDescription = sampleData["sampleDescription"]
        thisSample.libraryReference = sampleData["libraryReference"]
        thisSample.barcode = sampleData["barcode"]
        thisSample.species = sampleData["species"]
        thisSample.method = sampleData["method"]
        thisSample.fastQLocation = sampleData["fastQLocation"]
        thisSample.md5hash = sampleData["md5Hash"]
        thisSample.QCStatus = sampleData["QCStatus"]
        thisSample.insertLength = sampleData["insertLength"]
        thisSample.contaminantsImage = sampleData["contaminantsLink"]
        thisSample.fastQCSummary = sampleData["fastQCLink"]
        thisSample.filteredSequences = sampleData["filteredSequences"]
        thisSample.Q30Length = sampleData["Q30Length"]
        thisSample.percentGC = sampleData["percentGC"]
        thisSample.sequenceQuality = sampleData["sequenceQuality"]
        thisSample.sequenceQualityScores = sampleData["sequenceQualityScores"]
        thisSample.sequenceContent = sampleData["sequenceContent"]
        thisSample.GCContent = sampleData["GCContent"]
        thisSample.baseNContent = sampleData["baseNContent"]
        thisSample.sequenceLengthDistribution = sampleData["sequenceLengthDistribution"]
        thisSample.sequenceDuplicationLevels = sampleData["sequenceDuplicationLevels"]
        thisSample.overrepresentedSequences = sampleData["overrepresentedSequences"]
        thisSample.kmerContent = sampleData["kmerContent"]
        thisSample.save()

    except:
    #create the sample object
        thisSample  =  Sample(run = sampleData["thisRun"],\
                            project = sampleData["thisProject"],\
                            lane = sampleData["thisLane"],\
                            sampleReference = sampleData["sampleReference"],\
                            sampleName = sampleData["sampleName"],\
                            readNumber = sampleData["readNumber"],\
                            reads = sampleData["reads"],\
                            sequenceLength = sampleData["sequenceLength"],\
                            sampleDescription = sampleData["sampleDescription"],\
                            libraryReference = sampleData["libraryReference"],\
                            barcode = sampleData["barcode"],\
                            species = sampleData["species"],\
                            method = sampleData["method"],\
                            fastQLocation = sampleData["fastQLocation"],\
                            md5hash = sampleData["md5Hash"],\
                            QCStatus = sampleData["QCStatus"],\
                            insertLength = sampleData["insertLength"],\
                            contaminantsImage = sampleData["contaminantsLink"],\
                            fastQCSummary = sampleData["fastQCLink"],\
                            filteredSequences = sampleData["filteredSequences"],\
                            Q30Length = sampleData["Q30Length"],\
                            percentGC = sampleData["percentGC"],\
                            sequenceQuality = sampleData["sequenceQuality"],\
                            sequenceQualityScores = sampleData["sequenceQualityScores"],\
                            sequenceContent = sampleData["sequenceContent"],
                            GCContent = sampleData["GCContent"],\
                            baseNContent = sampleData["baseNContent"],\
                            sequenceLengthDistribution = sampleData["sequenceLengthDistribution"],\
                            sequenceDuplicationLevels = sampleData["sequenceDuplicationLevels"],\
                            overrepresentedSequences = sampleData["overrepresentedSequences"], \
                            kmerContent = sampleData["kmerContent"])
        thisSample.save()
    #add the software models to the sample
    for softwareModel in software_object_array:
        thisSample.software.add(softwareModel)
    return thisSample

def addUndetIndicesToDatabase( undetIndiciesForLane, lane_id, forceUpdate=False ):
    """Takes the input from parseUndeterminedReads and adds all of the relevant data to the database
        returns the id for the undetermined indexes"""
    #print undetIndiciesForLane
    #loop over the indicies stuff
    #0 is the sequence, 1 is occurances
    #Force update forces an update, rather than checking if they're all 0

    #need to get the object for the lane, if it exists
    #if it exists, empty it
    doWeNeedToUpdate = True
    if UndeterminedIndex.objects.filter(lane_id=lane_id).exists():
        try:
            undetIndexAlreadyPresent = UndeterminedIndex.objects.filter(lane_id=lane_id)
            #if the undetermined indicies are already present BUT they're not 0
            #and if the current set of data isn't 0, delete them and refresh
            #this stops us overwriting the long process of generating the undets with 0s
            
            #tricky? Loop over them all, if any are not ALL 0, and the incoming is, don't update
            for undetIndexObject in undetIndexAlreadyPresent:
                if undetIndexObject.occurances != 0:
                    doWeNeedToUpdate = False
            
            if (doWeNeedToUpdate == True) or (forceUpdate == True):        
                undetIndexAlreadyPresent.delete()
        except:
            print "Could not remove undetermined indexes that were already present"
            #sys.exit(1)
        
    #then add the details to it
    try:
        if doWeNeedToUpdate == True:
            for undetRank, undetValues in undetIndiciesForLane.iteritems():
                undetIndexModel = UndeterminedIndex(index=undetValues[0],\
                                                   occurances=undetValues[1],\
                                                   lane_id=lane_id)
                undetIndexModel.save()
    except:
        print "Cannot add undetermined reads"
        raise
   #     sys.exit(1)
 

def addContaminantsDetailsToDatabase( contaminantsSummary, sample_id ):
    """Takes the input from parseFastQScreenSummary (dict of data) and adds all of the relevant 
        data to the database"""    

    #add the contaminants details to the database
    for organism, contaminantValues in contaminantsSummary.iteritems():

        try:
            thisContam = ContaminantsDetails.objects.get( sample_id=sample_id, organism=organism )
            thisContam.percUnmapped = contaminantValues["Unmapped"]
            thisContam.oneHitOneLib = contaminantValues["One_hit_one_library"]
            thisContam.manyHitOneLib = contaminantValues["Multiple_hits_one_library"]
            thisContam.oneHitManyLib = contaminantValues["One_hit_multiple_libraries"]
            thisContam.manyHitManyLib = contaminantValues["Multiple_hits_multiple_libraries"]
            #not always hits no libs present, so check and assign depending on this
            if "Hits_no_libraries" in contaminantValues:
                thisContam.hitsNoLibraries = contaminantValues["Hits_no_libraries"]  
            thisContam.save()
        except:
            #not always hits no libs present, so check and assign depending on this
            if "Hits_no_libraries" in contaminantValues:
                currentHitsNoLibs = contaminantValues["Hits_no_libraries"]
            else:
                currentHitsNoLibs = None
            thisContam  = ContaminantsDetails( \
                                sample_id = sample_id, organism = organism, \
                                percUnmapped = contaminantValues["Unmapped"], \
                                oneHitOneLib = contaminantValues["One_hit_one_library"], \
                                manyHitOneLib = contaminantValues["Multiple_hits_one_library"], \
                                oneHitManyLib = contaminantValues["One_hit_multiple_libraries"], \
                                manyHitManyLib = contaminantValues["Multiple_hits_multiple_libraries"], \
                                hitsNoLibraries = currentHitsNoLibs ) 
                
            thisContam.save()
 




if __name__ == "__main__":
    #"""If the function is the main function, kick it into gear and run the script"""    

    #parse the arguements. Duh
    parser = argparse.ArgumentParser(prog='AlmostSignificant DataLoading', \
                                    description='This script is for loading data from nextseq and hiseq DNA sequencing runs into AlmostSignificant.', version=version) 
    parser.add_argument('runLocation', type=str, help='Location of processed sequencing run')
    parser.add_argument('rawLocation', type=str, help='Location of raw from-machine sequencing run')
    parser.add_argument('qCFolder', type=str, \
         help='Folder containing the output from fastQC and/or fastQScreen for each of the fastq files in the run')
    parser.add_argument('-m', '--machineType', default="nextseq", choices=['hiseq','nextseq'],\
         help='Set the machine type. Accepts hiseq or nextseq. By default assumes %(default)s runs')
    parser.add_argument('-c', '--checkUndet', default="False", action="store_true",\
         help='Flag for parsing the undetermined indexes for a run. May take a few minutes to run, depending on the number of undetermined indexes and the number of lanes.')

    #gather the arguements
    args = parser.parse_args()

    #print (args.runLocation, args.rawLocation, args.qCFolder, args.machineType, args.checkUndet )
    addNextSeqRun( args.runLocation, args.rawLocation, args.qCFolder, machineType=args.machineType, checkUndetIndicies=args.checkUndet )
    



