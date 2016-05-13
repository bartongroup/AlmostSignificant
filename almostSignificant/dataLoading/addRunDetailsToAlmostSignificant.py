#This script collects and parses all the details for a run from
#the files that are created by the run, casava, fastQC, and the
#QC script to generate the relevant entries in the gsu_qc database.

import os
import json 
import django
import sys
import subprocess
import re
import xml.etree.ElementTree as ElementTree
import datetime
from django.core.exceptions import ObjectDoesNotExist
from pprint import pprint
#The illuminate package is used to get the cluster Densities.
#was from here: https://bitbucket.org/invitae/illuminate
from illuminate import InteropDataset
from numpy import mean, std
 

print "Adding run details to almostSignificant"
#EEEEEEEVIL
#shouldn't be doing this. Sorry
#needs this path, or the path to your almostSignificant install, loaded into PYTHONPATH
#djangoFolder = "/homes/gsupipe-x/djangoProjects/almostSignificant/gsuStats/"

#load and import the models from django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gsuStats.settings')
django.setup()

from gsuStats import settings
from  gsuStats.almostSignificant.models import *

#mediaFolder ="/homes/gsupipe-x/djangoProjects/almostSignificant/gsuStats/gsuStats/media/" 
#mediaFolder ="/homes/gsupipe-x/bodgeScripts/test/" 
mediaFolder = settings.MEDIA_ROOT

#takes input as a JSON string as described in the example below below.
#Outer contents pertain to the run in general
#has sample value which is an array of samples, each a dict of information pertaining
#to the individual samples, rather than the run
#{
#   "runName":"130531_SN7001389_0053_AC2410ACXX",
#   "runLocation":"/cluster/gsu/data/hiseq/130531_SN7001398_0053_AC2410ACXX",
#   "project":"Project_GSU_AG_Worm",
#   "totalSequences":1895437,
#   "filteredSequences":0,
#   "undeterminedIndex":[
#      {
#         "index":"TGAC",
#         "occurances":7,
#         "lane":1
#      },
#      {
#         "index":"GATK",
#         "occurances":8,
#         "lane":2
#      }
#   ],
#   "sample":[
#      {
#         "sampleName":"1",
#         "lane":1,
#         "Q30Length":89,
#         "libraryID":"55",
#         "software":[
#            {
#               "softwareName":"CASAVA",
#               "version":"1.8.1",
#               "parameters":"--explode FALSE"
#            },
#            {
#               "softwareName":"OtherSoftware",
#               "version":"1",
#               "parameters":"doesnt exist"
#            }
#         ],
#         "fastQCSummary":"/cluster/gsu/data/processed/Stats/Run/130531_SN7001398_0053_AC2410ACXX/Project_GSU_AG_Worm/Sample_3_LIB55_LDI19/3_LIB55_LDI19_CGATGT_L008_R1_001.fastq.gz_screen.png",
#         "md5Hash":"asdhfsahdfljshdfljshdf",
#         "contaminantsImage":"/cluster/gsu/data/processed/Stats/Run/130531_SN7001398_0053_AC2410ACXX/Project_GSU_AG_Worm/Sample_3_LIB55_LDI19/3_LIB55_LDI19_CGATGT_L008_R1_001.pdf",
#         "percentGC":45,
#         "sequenceLength":"20-100",
#         "sequenceQuality":"Pass",
#         "sequenceQualityScores":"Pass",
#         "sequenceContent":"Pass",
#         "GCContent":"Pass",
#         "baseNContent":"Pass",
#         "sequenceLengthDistribution":"Pass",
#         "sequenceDuplicationLevels":"Pass",
#         "overrepresentedSequences":"Pass",
#         "kmerContent":"Pass"
#      },
#      {
#         "sampleName":"2",
#         "lane":2,
#         "Q30Length":89,
#         "libraryID":"56",
#         "software":[
#            {
#               "softwareName":"CASAVA",
#               "version":"1.8.1",
#               "parameters":"--explode TRUE"
#            },
#            {
#               "softwareName":"OtherSoftware",
#               "version":"1",
#               "parameters":"doesnt exist"
#            }
#         ],
#         "fastQCSummary":"/cluster/gsu/data/processed/Stats/Run/130531_SN7001398_0053_AC2410ACXX/Project_GSU_AG_Worm/Sample_3_LIB56_LDI20/3_LIB56_LDI20_TGACCA_L008_R1_001.fastq.gz_screen.png",
#         "md5Hash":"asdhfsahdfljshdfljshdf",
#         "contaminantsImage":"/cluster/gsu/data/processed/Stats/Run/130531_SN7001398_0053_AC2410ACXX/Project_GSU_AG_Worm/Sample_3_LIB56_LDI20/3_LIB56_LDI20_TGACCA_L008_R1_001.pdf",
#         "percentGC":45,
#         "sequenceLength":"100",
#         "sequenceQuality":"Pass",
#         "sequenceQualityScores":"Pass",
#         "sequenceContent":"Pass",
#         "GCContent":"Pass",
#         "baseNContent":"Pass",
#         "sequenceLengthDistribution":"Pass",
#         "sequenceDuplicationLevels":"Pass",
#         "overrepresentedSequences":"Pass",
#         "kmerContent":"Pass"
#      }
#   ]
#}
#loads the JSON from the QC script

###########################  FUNCTIONS #########################################
def getFirstBaseReport( runLocation ):
    """ Takes the runLocation as input and returns a dict of the cluster
        densities from the first base report
    """

    if "miseq" in runLocation:
        print "First Base Reports are not made for MiSeq runs"
        sys.exit(1)
    firstBaseReportLocation = "%s/First_Base_Report.htm" % runLocation
    fileOpen = open(firstBaseReportLocation, "r")

    firstBaseReport = []
    for line in fileOpen.readlines():
        firstBaseReport.append( line.rstrip('\r\n') )
    fileOpen.close()

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

################################################################################




def HiMiSeqRun ( qcData, runName, runNameSplit, machineType ):
    """Deals with adding Miseq or Hiseq runs"""
    run_id=""
    thisRun = ""
    
    date_unparsed = runNameSplit[0]
    date = datetime.date(year=int("20%s" % date_unparsed[0:2]), month=int(date_unparsed[2:4]),\
                            day=int(date_unparsed[4:6]))
    #load the run Parameteres from the runParameters file made by casava.
    #RUNPARAMSHERE
    if machineType == "HiSeq":
        runParametersLocation = qcData["runLocation"] + "/runParameters.xml"
    elif machineType == "MiSeq":
        runParametersLocation = qcData["runLocation"] + "/RunParameters.xml"
    runParametersXML = ElementTree.parse(runParametersLocation)
    runParameters = runParametersXML.getroot()
    if machineType=="HiSeq":
        runParameters = runParameters[0]
        for child in runParameters.iterfind("Read1"):
            length = child.text
        for child in runParameters.iterfind("FCPosition"):
            FCPosition = child.text
    elif machineType=="MiSeq":
        for child in runParameters.iterfind("Reads"):
            for item in child.iterfind("RunInfoRead"):
                length = child[0].attrib["NumCycles"]
        FCPosition = ""
    #alias- needed?
    alias = ""
    #length
    #pairedSingle - library from one sample - libraryType, description 
    #pairedSingle = libraryData["libraryType"]["description"]
    #the easiest way to get this is to use the library details from miso
    #so thats what I did. It's defined repeatedly in the sample loop
    #BUT I need to do the run creation here ideally, bit of a problem
    pairedSingle = ""
    #FCPosition
    FCPosition = ""
    for child in runParameters[0].iterfind("FCPosition"):
        FCPosition = child.text
    
    #if the run exists, update it.
    #if it doesn't exist, make it !
    try:
        thisRun = Run.objects.get(runName=runName)
        thisRun.machine = machine
        thisRun.machineType = machineType
        thisRun.date = date
        thisRun.alias = alias
        thisRun.length = length
        thisRun.pairedSingle = pairedSingle
        thisRun.fcPosition = FCPosition
        thisRun.save()
        run_id = thisRun.id
    except:
        #construct the run for saving
        thisRun = Run(runName=runName, machine=machine, machineType=machineType, date=date,\
                        alias=alias, length=length, pairedSingle=pairedSingle, fcPosition = FCPosition)
        thisRun.save()
        run_id=thisRun.id
    
    print "Run id: %s" % run_id
    
    #Parse the interop files for the clusterDensity information.
    interOpObject = InteropDataset( qcData["runLocation"] )
    tileMetrics = interOpObject.TileMetrics()
    densityDict = {}
    densityPFDict = {}
    numClustersDict = {}
    numClustersPFDict = {}
    for lane in set(tileMetrics.data["lane"]):
        densityDict[lane] = []
        densityPFDict[lane] = []
        numClustersDict[lane] = []
        numClustersPFDict[lane] = []
    
    for index,value in enumerate(tileMetrics.data["lane"]):
        if tileMetrics.data["code"][index] == 100:
            densityDict[value].append( tileMetrics.data["value"][index] )
        elif tileMetrics.data["code"][index] == 101:
            densityPFDict[value].append( tileMetrics.data["value"][index] )
        elif tileMetrics.data["code"][index] == 102:
            numClustersDict[value].append( tileMetrics.data["value"][index] )
        elif tileMetrics.data["code"][index] == 103:
            numClustersPFDict[value].append( tileMetrics.data["value"][index] )
    
    #get the first base report cluster densities
    firstBaseReport = getFirstBaseReport( qcData["runLocation"] )
    print firstBaseReport
    
    #Have to loop over every sample.
    for currentSample in qcData["sample"]:
        #Load the library data from MISO        
        library = currentSample["libraryID"]
        print library
        if library.find("Undetermined") != -1:
            print "Undetermined read: Skipping"
        else:
            #get the library json from miso
            home = os.path.expanduser('~')
            misoRESTLibraryCall = ['%s/bin/get_library_info.sh' % home, '-r', library]
            try:
                libraryJSONProcess = subprocess.Popen(misoRESTLibraryCall,\
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE )
                libraryJSON = libraryJSONProcess.communicate()[0]
            except:
                print "Something went wrong with the MISO library rest call"
                sys.exit(1)
            
            #json handling
            try:
                libraryData = json.loads(libraryJSON)
            except ValueError:
                print "Invalid JSON - check your library reference and/or api key (1)"
                sys.exit(1)
            #defining this here as it's the easiest way. A single run will only have one method
            #so any sample will have the same as all other samples.
            pairedSingle = libraryData["libraryType"]["description"]
            if pairedSingle == "mRNA Seq":
                pairedSingle = "Paired End"
            elif pairedSingle == "Small RNA":
                pairedSingle = "Single End"
            insertLength = libraryData["libraryQCs"][0]["insertSize"]
            #update the run to have the correct paired\single value
            try:
                thisRun.pairedSingle = pairedSingle
                thisRun.save()
            except:
                print "Something went wrong when updating the pairedSingle value in the run"
                sys.exit(1)
             
            ### Project ###
            project_id = ""
            thisProject = ""
            # need to check that the project isn't already in the database
            # because it can be from a previous run or a previous sample of this run
            #information needed
            #project - qcData - project
            projSearchTerm = "alias" 
            projectName = currentSample["project"]
            if projectName.find("Project_") != -1:
                projectName = projectName.lstrip("Project_")
                projSearchTerm = "alias"
            if machineType == "MiSeq":
                projSearchTerm = "name"
            projectMISOID = 0
            projectPROID =  0
            owner = ""
            description = ""
            #get the library json from miso
            misoRESTProjectCall = ['%s/bin/get_project_info.sh' % home]
            projectJSONProcess = subprocess.Popen(misoRESTProjectCall,\
                                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            projectJSON = projectJSONProcess.communicate()[0]
            #json handling
            try:
               projectData = json.loads(projectJSON)
            except ValueError:
                print "Invalid JSON - check your library reference and/or api key (2)"
                sys.exit(1)
            #get the details we need from the project data
            #if the project name is already in terms of the PRO ID we set the search term to projectId
            #if it is the human project name, search for the alias
            #the search term is set above here, where it checks for Project_
            for eachProject in projectData:
                if eachProject[projSearchTerm] == projectName:
                    projectMISOID = eachProject["projectId"]
                    projectPROID = eachProject["name"]
                    projectName = eachProject["alias"]
                    #cant get this until I can get prjects via name using the restAPI
                    #owner = eachProject["overviews"][0]["principleInvestigator"]
                    description = eachProject["description"]
    
            #check if the run exists and update it
            #if it doesn't, make it
            try:
                thisProject = Project.objects.get(project=projectName)
                thisProject.projectMISOID = projectMISOID
                thisProject.projectPROID = projectPROID
                thisProject.owner = owner
                thisProject.description = description
                thisProject.save()
                project_id  = thisProject.id
            except ObjectDoesNotExist: 
                thisProject = Project(project=projectName, projectMISOID=projectMISOID, \
                                    projectPROID=projectPROID, owner=owner, description=description)
                thisProject.save()
                project_id = thisProject.id
    
              
            
    
            print "Project id: %s" % project_id
    
    
    
            ### Lane ###
            lane_id=""
            thisLane = ""
            #information needed
            #run_id foreign key
            #lane
            lane = currentSample["lane"]
            #clusterDensity
            #percPassingFilter
            #readsPassingFilter
            #percentOverQ30
            #open the read summary file
            #InterOp parsing for the clusterDensity
            clusterDensity = int(round(mean(densityDict[int(lane)])/1000))
            clusterDensityStdDev = int(round(std(densityDict[int(lane)])/1000))
            clusterPFDensity = int(round(mean(densityPFDict[int(lane)])/1000))
            clusterPFDensityStdDev = int(round(std(densityPFDict[int(lane)])/1000))
            numClusters = int(round(mean(numClustersDict[int(lane)])/1000))
            numClustersStdDev =  int(round(std(numClustersDict[int(lane)])/1000))
            numClustersPF = int(round(mean(numClustersPFDict[int(lane)])/1000))
            numClustersPFStdDev = int(round(std(numClustersPFDict[int(lane)])/1000))
    
            percPassingFilter = numClustersPF / numClusters * 100
            readsPassingFilter = 0
            percentOverQ30 = 0.0
            laneUndeterminedArray = qcData["totalUndeterminedReads"]
            if lane in laneUndeterminedArray.keys():
                totalUndeterminedIndexes = laneUndeterminedArray[lane]
            else:
                totalUndeterminedIndexes = 0
    
            if machineType == "HiSeq":
                firstBaseDensity = int(round(firstBaseReport[int(lane)]))
            else:
                firstBaseDensity = "None"            
            #Check if lane doesn't already exist
            #if it does update, doesn't then create
            try:
                thisLane = Lane.objects.get(lane=lane, run_id=run_id)
                thisLane.ClusterPFDensity = clusterPFDensity
                thisLane.clusterPFDensityStdDev = clusterPFDensityStdDev
                thisLane.clusterDensity = clusterDensity
                thisLane.clusterDensityStdDev = clusterDensityStdDev
                thisLane.numClusters = numClusters
                thisLane.numClustersStdDev = numClustersStdDev
                thisLane.numClustersPF = numClustersPF
                thisLane.numClustersPFStdDev = numClustersPFStdDev
                thisLane.firstBaseDensity = firstBaseDensity
                thisLane.percPassingFilter = percPassingFilter
                thisLane.readsPassingFilter = readsPassingFilter
                thisLane.percentOverQ30 = percentOverQ30
                thisLane.totalUndetIndexes = totalUndeterminedIndexes
                thisLane.save()
                lane_id = thisLane.id
            except:
                print(lane,laneUndeterminedArray)
                thisLane = Lane(run_id=run_id, lane=lane, ClusterPFDensity=clusterPFDensity,\
                                    percPassingFilter=percPassingFilter, readsPassingFilter=readsPassingFilter,\
                                    totalUndetIndexes=totalUndeterminedIndexes,\
                                    percentOverQ30=percentOverQ30, numClusters = numClusters,\
                                    clusterDensity=clusterDensity, \
                                    clusterDensityStdDev=clusterDensityStdDev,\
                                    clusterPFDensityStdDev=clusterPFDensityStdDev,\
                                    firstBaseDensity=firstBaseDensity,\
                                    numClustersStdDev = numClustersStdDev,\
                                    numClustersPF = numClustersPF, \
                                    numClustersPFStdDev = numClustersPFStdDev)
                thisLane.save()
                lane_id = thisLane.id
            print "Lane id: %s" % lane_id 
                
                
            ### Software ###
            #need to check that the combination doesn't currently exist
            #information Needed
            #softwareName - softwareName
            #version - version
            #parameters - parameters
            #loop over currentSample software
            software_object_array = []
            #0 is the software, 1 is the version, 2 is the parameters
            for softwareEntry in currentSample["software"]:
                #softwareDetails = [softwareEntry["softwareName"],softwareEntry["version"],softwareEntry["parameters"] ]
                try: 
                    software_object_array.append(Software.objects.get(softwareName=softwareEntry["softwareName"],\
                                                                 version=softwareEntry["version"],\
                                                                 parameters=softwareEntry["parameters"]))
                except ObjectDoesNotExist:
                    newSoftware = Software(softwareName=softwareEntry["softwareName"],\
                                                version=softwareEntry["version"],\
                                                    parameters=softwareEntry["parameters"])
                    newSoftware.save()
                    software_object_array.append( newSoftware )
            
            #HiSeq/Miseq Control Software version and name
            CSSoftware = {"parameters":""}
            if machineType == "HiSeq":
                for child in runParameters.iterfind("ApplicationName"):
                    CSSoftware["softwareName"] = child.text
                for child in runParameters.iterfind("ApplicationVersion"):
                    CSSoftware["version"] = child.text
                #CameraFirmware Version and name
                CameraFirmware = {"softwareName":"Camera Firmware", "parameters":""}
                for child in runParameters.iterfind("CameraFirmware"):
                    CameraFirmware["version"] = child.text
                try:
                    software_object_array.append( Software.objects.get( softwareName=CameraFirmware["softwareName"],\
                                                                    version=CameraFirmware["version"] ) )
                except ObjectDoesNotExist:
                    CameraFirmwareModel = Software(softwareName=CameraFirmware["softwareName"],\
                                                    version=CameraFirmware["version"],\
                                                    parameters=CameraFirmware["parameters"] )
                    CameraFirmwareModel.save()
                    software_object_array.append( CameraFirmwareModel )
       
                #CameraDriver version and name
                CameraDriver = {"softwareName":"Camera Driver", "parameters":""}
                for child in runParameters.iterfind("CameraDriver"):
                    CameraDriver["version"] = child.text
                try:
                    software_object_array.append( Software.objects.get( softwareName=CameraDriver["softwareName"],\
                                                                    version=CameraDriver["version"] ) )
                except ObjectDoesNotExist:
                    CameraDriverModel = Software(softwareName=CameraDriver["softwareName"],\
                                                    version=CameraDriver["version"],\
                                                    parameters=CameraDriver["parameters"] )
                    CameraDriverModel.save()
                    software_object_array.append( CameraDriverModel )
               #miseq software handling
            elif machineType == "MiSeq":
                for softwareSetup in runParameters.iterfind("Setup"):
                    for softwareDetail in softwareSetup.iterfind("ApplicationName"):
                        CSSoftware["softwareName"] = softwareDetail.text
                    for softwareDetail in softwareSetup.iterfind("ApplicationVersion"):
                        CSSoftware["version"] = softwareDetail.text
               
            try:
                software_object_array.append( Software.objects.get( softwareName=CSSoftware["softwareName"], \
                                                                version=CSSoftware["version"]) )
            except ObjectDoesNotExist:
                CSSoftwareModel = Software(softwareName=CSSoftware["softwareName"],\
                                           version=CSSoftware["version"],\
                                           parameters=CSSoftware["parameters"])
                CSSoftwareModel.save()
                software_object_array.append( CSSoftwareModel )
                
       
            #RTA Version
            #This isnt added to the software_object_array as we add it in the original creation of sample
            RTAVersion = {"softwareName":"RTA Version", "parameters":""}
            RTAVersionModel = ""
            for child in runParameters.iterfind("RTAVersion"):
                RTAVersion["version"] = child.text
            try:
                RTAVersionModel = Software.objects.get( softwareName=RTAVersion["softwareName"],\
                                                                version=RTAVersion["version"] ) 
            except ObjectDoesNotExist:
                RTAVersionModel = Software(softwareName=RTAVersion["softwareName"],\
                                                version=RTAVersion["version"],\
                                                parameters=RTAVersion["parameters"] )
                RTAVersionModel.save()
            
            
            
            
            
            ### Sample ###
            sample_id = ""
            thisSample = ""
            #information needed
            #run_id foreign key
            #project_id foreign key
            #software foreign key. can have many
            #lane foreign key
            #sampleReference - library - sample, id
            sampleReference = libraryData["sample"]["id"]
            #sampleName - libraru - sample, alias
            sampleName = libraryData["sample"]["alias"]
            #fastQLocation
            fastQLocation = currentSample["fastQLocation"]
            #readNumber - parse from runName
            readNumberSearchString = re.compile('_R(\d)_')
            readNumber = readNumberSearchString.search(currentSample["fastQLocation"]).group(1)
            #reads - currentSample - totalSequences
            reads = currentSample["totalSequences"]
             #sequenceLength - sequenceLength
            sequenceLength = currentSample["sequenceLength"]
            #sampleDescription
            sampleDescription = libraryData["description"]
            #libraryReference  
            libraryReference = libraryData["id"]
            #barcode - library - tagBarcodes,1, sequence
            #handling for things without a barcode
            if libraryData["tagBarcodes"]:
                barcode = libraryData["tagBarcodes"]["1"]["sequence"]
                #method - library - tagBarcodes,1, strategyName
                method = libraryData["tagBarcodes"]["1"]["strategyName"]
            else:
                barcode = ""
                method = ""
                
            #species - library - sample,scientificName
            species = libraryData["sample"]["scientificName"]
            #fastQLocation - currentSample - fastQCSummary
            fastQLocation = currentSample["fastQCSummary"]
            #md5hash - currentSample - md5Hash
            md5hash = currentSample["md5Hash"]
            #QCStatus - set to pending
            QCStatus = "pending"
            
            #insertSize - library - libraryQCs,insertSiz#e
            insertSize = libraryData["libraryQCs"][0]["insertSize"]
       
            #Copy the two files across
            #make directory if it doesn't exist
            mediaPath = mediaFolder + "/" + runName + "/"
            if not os.path.exists(mediaPath):
                try:
                    os.makedirs(mediaPath)
                except OSError:
                    print "Unable to create %s" % mediaPath
            #contaminantsImage - COPY TO MEDIA THEN USE MODIFIED LOCATION currentSample - contaminantsImage
            if not os.path.exists(currentSample["contaminantsImage"]):
                print "Error: %s doesn't exist" % currentSample["contaminantsImage"]
                sys.exit()
            contaminantsPath, contaminantsFile = os.path.split(currentSample["contaminantsImage"])
            contaminantsDestination = os.path.join(mediaPath,contaminantsFile)
            contaminantsLink = os.path.join(runName, contaminantsFile)
            try:
                if not os.path.lexists(contaminantsDestination):
                    os.symlink(currentSample["contaminantsImage"], contaminantsDestination) 
            except OSError as e:
                print "Error linking %s to %s" % ( currentSample["contaminantsImage"], contaminantsDestination)
                print e
            #add contaminantsDestination to the database
            
            #fastQCSummary -  COPY TO MEDIA THEN USE MODIFIED LOCATION currentSample - fastQCSummary
            if not os.path.exists(currentSample["fastQCSummary"]):
                print "Error: %s doesn't exist" % currentSample["fastQCSummary"]
                sys.exit()
            fastQCPath, fastQCFile = os.path.split(currentSample["fastQCSummary"])
            fastQCDestination = os.path.join(mediaPath,fastQCFile)
            fastQCLink = os.path.join( runName, fastQCFile)
            try:
                if not os.path.lexists(fastQCDestination):
                    os.symlink(currentSample["fastQCSummary"], fastQCDestination) 
            except OSError as e:
                print "Error linking %s to %s" % ( currentSample["fastQCSummary"], fastQCDestination)
                sys.exit()
                print e
            #add fastQCDestination to the database
            
            #filteredSequences - currentSample - filteredSequences
            filteredSequences = currentSample["filteredSequences"]
            #Q30Length - currentSample - Q30Length
            Q30Length = currentSample["Q30Length"]
            #percentGC - currentSample - percGC
            percentGC = currentSample["percentGC"]
            #sequenceQuality - currentSample - sequenceQuality
            sequenceQuality = currentSample["sequenceQuality"]
            #sequenceQualityScores - currentSample - sequenceQualityScores
            sequenceQualityScores= currentSample["sequenceQualityScores"]
            #sequenceContent - currentSample - sequenceContent
            sequenceContent = currentSample["sequenceContent"]
            #GCContent - currentSample - GCContent
            GCContent = currentSample["GCContent"]
            #baseNContent -currentSample - baseNContent
            baseNContent = currentSample["baseNContent"]
            #sequenceLengthDistribution - currentSample - sequenceLengthDistrbution
            sequenceLengthDistribution = currentSample["sequenceLengthDistribution"]
            #sequenceDuplicationLevels - currentSample - sequenceDuplicationLevels
            sequenceDuplicationLevels = currentSample["sequenceDuplicationLevels"]
            #overrepresentedSequences - currentSample - overrepresentedSequences
            overrepresentedSequences = currentSample["overrepresentedSequences"]
            #kmerContent - currentSample - kmerContent
            kmerContent = currentSample["kmerContent"]
            #check if the sample exists
            #if it does, update, otherwise create
            try:
                thisSample = Sample.objects.get(sampleReference=sampleReference, sampleName=sampleName,\
                                                run_id=run_id,lane_id=lane_id,project_id=project_id,\
                                                libraryReference=libraryReference,readNumber=readNumber)
                thisSample.readNumber = readNumber
                thisSample.reads = reads
                thisSample.sequenceLength = sequenceLength
                thisSample.sampleDescription = sampleDescription
                thisSample.libraryReference = libraryReference
                thisSample.barcode = barcode
                thisSample.species = species
                thisSample.method = method
                thisSample.fastQLocation = fastQLocation
                thisSample.md5hash = md5hash
                thisSample.QCStatus = QCStatus
                thisSample.insertLength = insertLength
                thisSample.contaminantsImage = contaminantsLink
                thisSample.fastQCSummary = fastQCLink
                thisSample.filteredSequences = filteredSequences
                thisSample.Q30Length = Q30Length
                thisSample.percentGC = percentGC
                thisSample.sequenceQuality = sequenceQuality
                thisSample.sequenceQualityScores = sequenceQualityScores
                thisSample.sequenceContent = sequenceContent
                thisSample.GCContent = GCContent
                thisSample.baseNContent = baseNContent
                thisSample.sequenceLengthDistribution = sequenceLengthDistribution
                thisSample.sequenceDuplicationLevels = sequenceDuplicationLevels
                thisSample.overrepresentedSequences = overrepresentedSequences
                thisSample.kmerContent = kmerContent
                thisSample.save()
                sample_id = thisSample.id
            except:
               
                #create the sample object
                #epic.
                thisSample = Sample(run=thisRun,\
                                    project=thisProject,\
                                    #software_id=RTAVersionModel,\
                                    lane=thisLane,\
                                    sampleReference=sampleReference,\
                                    sampleName=sampleName,\
                                    readNumber=readNumber,\
                                    reads=reads,\
                                    sequenceLength=sequenceLength,\
                                    sampleDescription=sampleDescription,\
                                    libraryReference=libraryReference,\
                                    barcode=barcode,\
                                    species=species,\
                                    method=method,\
                                    fastQLocation=fastQLocation,\
                                    md5hash=md5hash,\
                                    QCStatus=QCStatus,\
                                    insertLength=insertLength,\
                                    contaminantsImage=contaminantsLink,\
                                    fastQCSummary=fastQCLink,\
                                    filteredSequences=filteredSequences,\
                                    Q30Length=Q30Length,\
                                    percentGC=percentGC,\
                                    sequenceQuality=sequenceQuality,\
                                    sequenceQualityScores=sequenceQualityScores,\
                                    sequenceContent=sequenceContent,
                                    GCContent=GCContent,\
                                    baseNContent=baseNContent,\
                                    sequenceLengthDistribution=sequenceLengthDistribution,\
                                    sequenceDuplicationLevels=sequenceDuplicationLevels,\
                                    overrepresentedSequences=overrepresentedSequences, \
                                    kmerContent=kmerContent)
                thisSample.save()
                sample_id = thisSample.id
    
                #now the sample is made, we can associate it with all of the software
                for softwareModel in software_object_array:
                    thisSample.software.add(softwareModel)
    
                
                                    
            print "Sample id: %s" % sample_id 
    
            #add the contaminants details to the database
            contaminantsSummary = contaminantsFile.replace("png","txt")
            contaminantsSummaryFile = os.path.join(contaminantsPath,contaminantsSummary )#loc of file
            contFile = open(contaminantsSummaryFile, "r")
            contFileLines = contFile.readlines()
            contFile.close()
            hitsNoLibs = contFileLines[-1].split(": ")[1].strip()
            for line in contFileLines[2:-2]:
                splitLine = line.split("\t")
                organism = splitLine[0].strip()
                unmapped = splitLine[1].strip()
                oneHitOneLib = splitLine[2].strip()
                manyHitOneLib = splitLine[3].strip()
                oneHitManyLib = splitLine[4].strip()
                manyHitManyLib = splitLine[5].strip()
                
                try:
                    thisContam = ContaminantsDetails.objects.get( sample_id=sample_id, organism=organism )
                    thisContam.percUnmapped=unmapped
                    thisContam.oneHitOneLib=oneHitOneLib
                    thisContam.manyHitOneLib=manyHitOneLib 
                    thisContam.oneHitManyLib=oneHitManyLib
                    thisContam.manyHitManyLib=manyHitManyLib
                    thisContam.hitsNoLibraries=hitsNoLibs  
                    thisContam.save()
                except:
                    thisContam = ContaminantsDetails( \
                                        sample_id=sample_id, organism=organism, \
                                        percUnmapped=unmapped, oneHitOneLib=oneHitOneLib, \
                                        manyHitOneLib=manyHitOneLib, oneHitManyLib=oneHitManyLib, \
                                        manyHitManyLib=manyHitManyLib, hitsNoLibraries=hitsNoLibs)  
                    thisContam.save()
    
    
    ### UndeterminedIndex ###
    #information needed
    #lane foreignKey
    #index - index
    #occurances -index
    #loop over undeterminedIndex in qcData
    undetIndexArray = []
    #0 is the sequence, 1 is occurances
    lanesSeen = []
    for undetIndex in qcData["undeterminedIndex"]: 
        #entry for adding to the database
        try:
            undetIndexLane = Lane.objects.get(run_id=run_id,lane=undetIndex["lane"])
        except:
            print "Error: lane cannot be assigned to the undetermined Index"
            sys.exit(1)
        #if we havn't seen the lane before, delete all the old undet reads
        if undetIndex["lane"] not in lanesSeen:
            try:
                undetIndexAlreadyPresent = UndeterminedIndex.objects.filter(lane_id=undetIndexLane.id)
                undetIndexAlreadyPresent.delete()
            except:
                print "Could not remove undetermined indexes that were already present"
                sys.exit(1)
            #store the lanes we've seen for the purposes of removing the old undet reads
            lanesSeen.append(undetIndex["lane"])
        try:
    #        undetIndexModel = UndeterminedIndex.objects.get(lane_id=undetIndexLane.id,\
    #                                                             index=undetIndex["index"],\
    #                                                             occurances=undetIndex["occurances"]).id 
    #        undetIndexArray.append( undetIndexModel )
    #    except:
            undetIndexModel = UndeterminedIndex(index=undetIndex["index"],\
                                                occurances=undetIndex["occurances"],\
                                                lane_id=undetIndexLane.id)
            undetIndexModel.save()
            undetIndex_id = undetIndexModel.id
            undetIndexArray.append(undetIndexModel)
        except:
            print "Cannot add undetermined reads"
            sys.exit(1)
    
    
    
 ### Run ###

qcJson = sys.argv[1]
qcFile = open(qcJson).read()
try:
    #qcData = json.loads(qcJson)
    qcData = json.loads(qcFile)
except ValueError:
    print "Invalid JSON: Check your qc data json"
    sys.exit(1)
#qcFile.close()

#findString = 'Lane[@key="%s"]' % lane
#DensityRatio = readSummary.attrib["densityRatio"]
#ClusterPF = ""
#for elem in readSummary.iterfind(findString):
#    #print elem.tag, elem.attrib['key'], elem.attrib['ClusterPF']
#    ClusterPF = elem.attrib['ClustersPF']
#clusterDensity = "%.d" % (int(ClusterPF) * float(DensityRatio) / 1000)

#generate the database objects in this order
#must be done in order for the foreign keys in undetReads and sample to work
#run
#software
#project
#lane
#undetReads
#sample


#information Needed
#runName - QC data - runName
runName = qcData["runName"]
#parse the runName for more details
runNameSplit = runName.split("_")
#machine - parse from runName
machine = runNameSplit[1]
#machineType - case based on machine
if machine == "SN7001398":
    machineType = "HiSeq"
    HiMiSeqRun ( qcData, runName, runNameSplit, machineType )
    
elif machine == "M01357":
    machineType = "MiSeq"
    HiMiSeqRun ( qcData, runName, runNameSplit, machineType )

elif machine == "NS500650":
    machineType = "NextSeq"
    #NextSeqRun ( qcData, runName, runNameSplit, machineType )

else:
    machineType = "Unknown"
    print "Error - unknown machine type. Is your path right?"
    sys.exit(1)
#date - parse from runName

   
