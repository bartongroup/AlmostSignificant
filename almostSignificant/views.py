import datetime
import numpy
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse 
from django.shortcuts import render, render_to_response, get_object_or_404
from almostSignificant.models import *
from django.conf import settings
from django.contrib import auth
from django.template import RequestContext
from django.db.models import Q
from almostSignificant import *
import os, re, json, itertools, numpy
from django.utils.http import urlquote
import locale

#locale.setlocale(locale.LC_ALL, 'en_GB')

def overview(request):
    """Overview view for AlmostSignificant showing all the runs.

    Generates the number of reads, bases, runs and samples for the header.
    Calls the render of the main page, which then has fun with javascript.
    /gsuStats/

    """
    #get the details for the header section
    details = Run.objects.all()
    numberOfRuns = len(details)
    numberOfSamples = len(Sample.objects.filter(readNumber=1).exclude(run__machineType="NextSeq")) + \
                            (len(Sample.objects.filter(readNumber=1,run__machineType="NextSeq"))/4)
    readsAndRunID = Sample.objects.only("reads","run_id").values_list("reads","run_id")
    #values list returns a list, so sum over the list and get the total
    #numberOfReads = [sum(x) for x in zip(*readsAndLength)][0]
    numberOfReads = 0
    Gbases = 0
    prevRunId = 0
    curRunLength = 0
    #loop over the reads, updating the length of the run as needs be
    for reads,curRunId in readsAndRunID:
        if curRunId != prevRunId:
            prevRunId = curRunId
            curRunLength = Run.objects.get(id=curRunId).length
        curGbases = reads * curRunLength
        Gbases += curGbases 
        numberOfReads += reads
    #return the page with the details we just generated
    return render_to_response('almostSignificant_mainpage.html',
                                {"v":0.001,"detailsName":"Run Overview",\
                                "runs":str(numberOfRuns), \
                                "samples":str(numberOfSamples),\
                                "numberOfReads":"%.2f" % (numberOfReads/1000000.0),\
                                "Gbases":"%.2f" % (Gbases/1000000000.0)},
                                context_instance=RequestContext(request)
                             )

def runView(request, run_name):
    """Overview for a single run, displaying each sample in the run.

    Calculated the number of reads, bases, samples for the run for the header.
    Calls the render of the project page, which then has fun with javascript.
    /gsuStats/run/<run name>

    """
    #generate all the important details for the header
    runDetails = get_object_or_404(Run, runName=run_name)
    numberOfSamples = len(Sample.objects.filter(run_id=runDetails.id,readNumber=1).exclude(run__machineType="NextSeq")) + \
                            (len(Sample.objects.filter(run_id=runDetails.id,readNumber=1,run__machineType="NextSeq"))/4)
    #get the samples which relate to the current runID
    numberOfReadsList = Sample.objects.filter(run_id=runDetails.id).values_list('reads')
    numberOfReads = 0
    for reads in numberOfReadsList:
        numberOfReads += reads[0]
    GBases = numberOfReads*runDetails.length
    #return the page with the details we just generated
    return render_to_response('almostSignificant_runpage.html',
                                {"detailsName":run_name,\
                                "machine":runDetails.machine,\
                                "machineType":runDetails.machineType,\
                                "samples":numberOfSamples,\
                                "numberOfReads":"%.2f" % (numberOfReads/1000000.0),\
                                "Gbases":"%.2f" % (GBases/1000000000.0)},
                                context_instance=RequestContext(request)
                                )

def projectView(request):
    """Overview for all of the current projects.

    Calculates the number of reads, bases, projects and samples.
    Calls the render of the project page, which then has fun with javascript.
    /gsuStats/project/

    """
    #get the details for the header section
    details = Project.objects.all()
    numberOfProjects = len(details)
    numberOfSamples = len(Sample.objects.filter(readNumber=1).exclude(run__machineType="NextSeq")) + \
                            (len(Sample.objects.filter(readNumber=1,run__machineType="NextSeq"))/4)
    readsAndRunID = Sample.objects.only("reads","run_id").values_list("reads","run_id")
    #values list returns a list, so sum over the list and get the total
    #numberOfReads = [sum(x) for x in zip(*readsAndLength)][0]
    numberOfReads = 0
    Gbases = 0
    prevRunId = 0
    curRunLength = 0
    #loop over the reads to calculate the number of bases. Update the run as needed.
    for reads,curRunId in readsAndRunID:
        if curRunId != prevRunId:
            prevRunId = curRunId
            curRunLength = Run.objects.get(id=curRunId).length
        curGbases = reads * curRunLength
        Gbases += curGbases 
        numberOfReads += reads
    #return the page with the details we just generated
    return render_to_response('almostSignificant_projectmain.html',
                                {"v":0.001,"detailsName":"Project Overview",\
                                "projects":numberOfProjects,\
                                "samples":str(numberOfSamples),\
                                "numberOfReads":"%.2f" % (numberOfReads/1000000.0),\
                                "Gbases":"%.2f" % (Gbases/1000000000.0)},
                                 context_instance=RequestContext(request)
                                )

def projectDetailView(request, project_name):
    """Overview for a specific project, detailing all the samples.

    Calculate the number of reads, bases and samples for the project.
    Calls the render of the project page, which then has fun with javascript.
    /gsuStats/project/<projet name>

    """
    #projectDetails = Project.objects.get(project=project_name)
    projectDetails = get_object_or_404(Project, project=project_name)
    projectSamples = Sample.objects.filter(project_id=projectDetails.id,readNumber=1)
    numberOfSamples = len(projectSamples.exclude(run__machineType="NextSeq")) + \
                            (len(projectSamples.filter(run__machineType="NextSeq"))/4)
    #get the samples which relate to the current runID
    readsAndRunID = Sample.objects.filter(project_id=projectDetails.id).values_list('reads','run_id')
    numberOfReads = 0
    Gbases = 0
    prevRunId = 0
    curRunLength = 0
    #loop over calculating the number of reads and bases, updating for runs as needed.
    for reads,curRunId in readsAndRunID:
        if curRunId != prevRunId:
            prevRunId = curRunId
            curRunLength = Run.objects.get(id=curRunId).length
        curGbases = reads * curRunLength
        Gbases += curGbases 
        numberOfReads += reads
    #return the page with the details we just generated.
    return render_to_response('almostSignificant_projectpage.html',
                                {"v":0.001,"detailsName":project_name,\
                                "Owner":projectDetails.owner,\
                                "samples":numberOfSamples,\
                                "numberOfReads":"%.2f" % (numberOfReads/1000000.0),\
                                "Gbases":"%.2f" % (Gbases/1000000000.0)},
                                context_instance=RequestContext(request)
                                )


def statistics(request):
    """Main view for the statistics page.
    
    The aim of this page is to show a summary statistic for each of the run types on 
    each of the machines. 

    """
        #get the details for the header section
    details = Run.objects.all()
    numberOfRuns = len(details)
    #return the page with the details we just generated
    return render_to_response('almostSignificant_statistics.html',
                                {"v":0.001,"detailsName":"General Overview",\
                                "runs":str(numberOfRuns)}, \
                                context_instance=RequestContext(request)
                             )

def runNotesEntry(request, runName):
    """Page to allow editing of the notes entry for a run"""
    #get the runData
    newNoteSet = False
    error = False
    runData = get_object_or_404(Run, runName=runName)
    #if the request has a new note, save the new note
    if 'newNote' in request.GET:
        try:
            newNoteSet = True
            newNote = request.GET['newNote']
            runData.notes = newNote
            runData.save()
        except:
            error = True
    #get the note
    runNotes = runData.notes
    return render(request, "almostSignificant_notesForm.html", \
                    {"runNotes":runNotes,
                     "runName":runName,"newNote":newNoteSet,
                     "error":error})

def projectNotesEntry(request, projectName):
    """Page to allow editing of the notes entry for a project"""
    #get the projectData
    newNoteSet = False
    error = False
    print("BLAH",projectName)
    projectData = get_object_or_404(Project, project=projectName)
    #if the request has a new note, save the new note
    if 'newNote' in request.GET:
        try:
            newNoteSet = True
            newNote = request.GET['newNote']
            projectData.notes = newNote
            projectData.save()
        except:
            error = True
    #get the note
    projectNotes = projectData.notes
    return render(request, "almostSignificant_notesForm.html", \
                    {"runNotes":projectNotes,
                     "runName":projectName,"newNote":newNoteSet,
                     "error":error})


def datasetsAjax(request):
    """Loads the Overview table.

    Returns JSON containing data for all of the runs in the database.
    Calculates and populates the json as needed. 
    Ajax for table in /gsuStats/run/

    """
    #setup the json data dictionary
    data={"aaData":[]}

    cols = [
        {
            "sTitle":"",
            "bSortable":False,
            "bSearchable":False,
            "sWidth":"60px"
        },
        {
            "sTitle":"Date",
            "bSortable":True
        },
        {  
            "sTitle":"Run Name",
            "bSortable":True
        },
        {
            "sTitle":"Machine",
            "bSortable":True
        },
        {
            "sTitle":"Machine Type",
            "bSortable":True
        },
        {
            "sTitle":"No. Samples",
            "bSortable":True
        },
        {
            "sTitle":"Length",
            "bSortable":True
        },
        {
            "sTitle":"Total Reads",
            "bSortable":True
        },
        {
            "sTitle":"Gbases",
            "bSortable":True
        },
        {
            "sTitle":"Strategy",
            "bSortable":True
        }
    ]

    data["aaSorting"] = [[1,"desc"]]
    data["aoColumns"] = cols
    #get all of the data
    dsData = Run.objects.all()
    #loop over each run, generating data as needed and adding it to the array
    for dataset in dsData:
        expstr = {}
        expstr["DT_RowId"]=dataset.id
        expstr["0"] = "" #empty for the dropdown button
        expstr["1"] = str(dataset.date) #date of the run
        expstr["2"] = '<a href="run/%s">%s</a>' % (dataset.runName, dataset.runName) #runName
        expstr["3"] = dataset.machine #machine name
        expstr["4"] = dataset.machineType #machine type

        #get the samples which relate to the current runID
        runData = Sample.objects.filter(run_id=dataset.id)
        numberOfReadsList = runData.values_list('reads')
        #values list returns a list, so sum over the list and get the total
        if len(numberOfReadsList) > 0:
            numberOfReads = [sum(x) for x in zip(*numberOfReadsList)][0]
            GBases = numberOfReads*dataset.length
        #handling for when I make a mistake and add a run with no samples
        else:
            numberOfReads = 0
            GBases = 0
        #if it's paired end, there's two reads for each sample
        #so we have to halve the number of samples.
        if dataset.pairedSingle.find("paired") != -1:
            numberOfSamples = len(runData)/2 #number of samples 
        else:
            numberOfSamples = len(runData) #number of samples 
        if dataset.machineType == "NextSeq": #handles the 4 lanes of nextseq
            numberOfSamples = numberOfSamples/4
        expstr["5"] = numberOfSamples
        expstr["6"] = dataset.length #read length
        expstr["7"] = locale.format("%d", numberOfReads, grouping=True) # number of reads
        expstr["8"] = "%.2f" % ( GBases/1000000000.0)  #Gb  
        expstr["9"] = dataset.pairedSingle #paired or single end
        #expstr["7"] = numberOfReads # number of reads
        #expstr["8"] = GBases  #Gb  
        data["aaData"].append(expstr) 
    
    #render response
    return HttpResponse(json.dumps(data), 'application/json')

def runAjax(request, run_name):
    """Generates the JSON for a run, detailing the samples.

    This returns the ajax for the table that shows all the samples for a run.
    Ajax for table in /gsuStats/run/<run name>

    """
    runID = Run.objects.get(runName=run_name).id

    #setup the json data dictionary
    data={"aaData":[]}

    cols = [
#        {
#            "mDataProp": None,
#            "sTitle": "",
#            "bSortable":False,
#            "bSearchable":False,
#            "sWidth":"60px"
#        },
        {
            "sTitle":"",
            "bSortable":False,
            "bSearchable":False,
            "sWidth":"60px"
        },
        {
            "sTitle":"Sample",
            "bSortable":True
        },
        {
            "sTitle":"Sample Ref",
            "bSortable":True
        },
        {
            "sTitle":"Lane",
            "bSortable":True
        },
        {   
            "sTitle":"Read",
            "bSortable":True
        },
        {
            "sTitle":"Index",
            "bSortable":True
        },
        {
            "sTitle":"No. Reads",
            "sType":"formatted_numbers",
            "bSortable":True
        },
        {
            "sTitle":"GBases",
            "bSortable":True
        },
        {
            "sTitle":"Q30 length",
            "bSortable":True
        },
        {
            "sTitle":"Overrep. Seqs",
            "bSortable":True
        },
        {
            "sTitle":"GC Content",
            "bSortable":True
        },
        {
            "sTitle":"Library",
            "bSortable":False
        },
        {
            "sTitle":"QC",
            "bSortable":False
        }
        #{
        #    "sTitle":"QC Summary",
        #    "bSortable":True
        #}
    ]

    data["aoColumns"] = cols
    data["aaSorting"] = [[3,"desc"],[1,"desc"],[4,"desc"]]

    #populate the dictionary
    dsData = Sample.objects.filter(run_id=runID)

    #loop over all the samples in the run
    for dataset in dsData:
        expstr = {}
        expstr["DT_RowId"]=dataset.id
        expstr["0"] = "" #empty string
        expstr["1"] = dataset.sampleName #sample name
        expstr["2"] = "SAM%s" % dataset.sampleReference #miso sam reference
        expstr["3"] = dataset.lane.lane #lane
        expstr["4"] = dataset.readNumber #read 1 or read 2
        expstr["5"] = dataset.barcode #barcode used
        expstr["6"] = locale.format("%d", dataset.reads, grouping=True) #number of reads
        expstr["7"] = "%.2f" % (dataset.run.length*dataset.reads/1000000000.0) #Gbases 
        expstr["8"] = "%s of %s" % (dataset.Q30Length, dataset.sequenceLength) #q30 and sequence lengths
        #color the overrepresented sequences based on whether it passed of warned/failed
        if dataset.overrepresentedSequences == "FAIL":
            print dataset.overrepresentedSequences
            expstr["9"] = '<p style="color:red"> %s</p>' % dataset.overrepresentedSequences
        elif dataset.overrepresentedSequences == "WARN":
            expstr["9"] = '<p style="color:orange"> %s</p>' % dataset.overrepresentedSequences
        else:
            expstr["9"] = '<p style="color:green"> %s</p>' % dataset.overrepresentedSequences
        expstr["10"] = dataset.percentGC
        #html string linking the library to miso
        if dataset.libraryReference != "N/A":
            expstr["11"] = "<a href=http://ngs-miso.lifesci.dundee.ac.uk/miso/library/%s target=\"_blank\">LIB%s</a>" \
                                        % ( dataset.libraryReference.lstrip("LIB"), dataset.libraryReference )
        else:
            expstr["11"] = dataset.libraryReference
        
        expstr["12"] = "<a href=%s%s target=\"_blank\">QC</a>" \
                                    %( settings.MEDIA_URL, dataset.fastQCSummary )
        data["aaData"].append(expstr) 
    
    #render response
    return HttpResponse(json.dumps(data), 'application/json')

def laneAjax(request, run_name, lane_number):
    """Generates the JSON for a lane, detailing the content of the run.

    This returns the ajax for the lane tabs in /gsuStats/run.

    """
    curRun = Run.objects.get(runName=run_name)
    runID = curRun.id
    lane = Lane.objects.get(run_id=runID,lane=lane_number)
    samples = Sample.objects.filter(lane_id=lane.id)
    print runID, lane

    #setup the json data dictionary
    data={"aaData":[]}
    lableArray = []
    readArray = []
    baseArray = []
    #use if using stackedBarChart
    #value2Array = []
    expstr = {}
    tempReadDict = {}
    tempBaseDict = {}
    #loop over all the samples in the run
    for dataset in samples:
        #sampleName = "%s_read%s" % ( dataset.sampleName, dataset.readNumber)
        #lableArray.append(sampleName) #sample name
        #valueArray.append("%.2f" % (dataset.reads/1000000.0)) #Gbases 
        if dataset.sampleName in tempReadDict.keys():
            tempReadDict[dataset.sampleName] = tempReadDict[dataset.sampleName] + \
                                                    dataset.reads/1000000.0
            tempBaseDict[dataset.sampleName] = tempBaseDict[dataset.sampleName] + \
                                                    dataset.reads*curRun.length/1000000000.0
            #use if using stackedBarChart
            #else
            #tempDict[dataset.sampleName] = [tempDict[dataset.sampleName], \
            #                                        dataset.reads/1000000.0]
        else:
            tempReadDict[dataset.sampleName] = dataset.reads/1000000.0 
            tempBaseDict[dataset.sampleName] = dataset.reads*curRun.length/1000000000.0 

    for key,value in iter(sorted(tempReadDict.iteritems())):
        lableArray.append(key)
        readArray.append("%.2f" % value)
        baseArray.append("%.2f" % tempBaseDict[key])
    #use if using stackedBarChart
    #    value2Array.append("%.2f" % value[1])
    #    valueArray.append("%.2f" % value[0])
    
    expstr["lableArray"]=lableArray 
    expstr["readArray"]=readArray 
    expstr["baseArray"]=baseArray
    #use if using stacked bar chart
    #expstr["value2Array"]=valueArray 

    data["aaData"].append(expstr) 
    
    #render response
    return HttpResponse(json.dumps(data), 'application/json')


def projectsAjax(request):
    """Generates JSON for all of the projects in the database.

    Ajax for the table in /gsuStats/Project.

    """

    #setup the json data dictionary
    data={"aaData":[]}

    cols = [
        {
            "sTitle":"",
            "bSortable":False,
            "bSearchable":False,
            "sWidth":"60px"
        },
        {

            "sTitle":"Name",
            "bSortable":True
        },
        {  
            "sTitle":"Project ID",
            "bSortable":True
        },
        {
            "sTitle":"No. Samples",
            "bSortable":True
        },
        {
            "sTitle":"Total Reads",
            "bSortable":True
        },
        {
            "sTitle":"Total Gbases",
            "bSortable":True
        },
        {
            "sTitle":"HTML",
            "bSortable":False
        }
    ]

    data["aoColumns"] = cols
    data["aaSorting"] = [[0,"asc"]]

    #populate the dictionary
    dsData = Project.objects.all()

    #loop over all of the projects
    for dataset in dsData:
        expstr = {}
        expstr["DT_RowId"]=dataset.id
        expstr["0"] = ""#empty
        expstr["1"] = '<a href="%s">%s</a>' % ( dataset.project, dataset.project ) #Project name
        expstr["2"] = dataset.projectPROID  #miso PRO id

        #get the samples which relate to the current runID
        samples = Sample.objects.filter(project_id=dataset.id)
        numberOfSamples = 0
        #loop over the samples, if it's the first read, count it
        #this stops paired end runs doubling the nuber of actual samples
        for sample in samples:
            if sample.readNumber == 1:
                numberOfSamples += 1
        
        readsAndRunID = samples.values_list('reads','run_id')
        #values list returns a list, so sum over the list and get the total
        #numberOfReads = [sum(x) for x in zip(*numberOfReadsList)][0]
        #GBases = numberOfReads*dataset.length
        numberOfReads = 0
        Gbases = 0
        prevRunId = 0
        curRunLength = 0
        #loop over each read and run to calculate the number of Gb and number of reads
        for reads,curRunId in readsAndRunID:
            if curRunId != prevRunId:
                prevRunId = curRunId
                curRunLength = Run.objects.get(id=curRunId).length
            curGbases = reads * curRunLength
            Gbases += curGbases 
            numberOfReads += reads
    
        expstr["3"] = numberOfSamples # number of samples
        expstr["4"] = locale.format("%d", numberOfReads, grouping=True) # number of reads
        expstr["5"] = "%.2f" % ( Gbases/1000000000.0)  #Gb  
        #link to a html table that is useful for copy-pasting to customers
        expstr["6"] = "<a href=\"html/project/%s\" target=\"_blank\">HTML Table</a>" \
                        % dataset.id
        data["aaData"].append(expstr) 
    
    #render response
    return HttpResponse(json.dumps(data), 'application/json')

def projectAjax(request, project_name):
    """Creates JSON for an individual project, detailing each sample.

    Ajax for the table in /gsuStats/project/<project name> """
    projectID = Project.objects.get(project=project_name).id

    #setup the json data dictionary
    data={"aaData":[]}

    cols = [
#        {
#            "mDataProp": None,
#            "sTitle": "",
#            "bSortable":False,
#            "bSearchable":False,
#            "sWidth":"60px"
#        },
        {
            "sTitle":"",
            "bSortable":False,
            "bSearchable":False,
            "sWidth":"60px"
        },
        {
            "sTitle":"Sample",
            "bSortable":True
        },
        {
            "sTitle":"Sample Ref",
            "bSortable":True
        },
        {
            "sTitle":"Run",
            "bSotrable":True
        },
        {
            "sTitle":"Date",
            "bSortable":True
        },
        {
            "sTitle":"Lane",
            "bSortable":True
        },
        {
            "sTitle":"Read",
            "bSortable":True
        },
        {
            "sTitle":"Index",
            "sSortable":True
        },
        {
            "sTitle":"No. Reads",
            "bSortable":True
        },
        {
            "sTitle":"GBases",
            "bSortable":True
        },
        {
            "sTitle":"Q30 length",
            "bSortable":True
        },
        {
            "sTitle":"GC Content",
            "bSortable":True
        },
#        {
#            "sTitle":"Library",
#            "bSortable":False
#        }
        #{
        #    "sTitle":"QC Summary",
        #    "bSortable":True
        #}
    ]

    data["aoColumns"] = cols
    data["aaSorting"] = [[5,"asc"],[1,"asc"],[6,"asc"]]

    #grap all of the samples belonging to this project
    dsData = Sample.objects.filter(project_id=projectID)

    #loop over each of the samples in the project
    for dataset in dsData:
        expstr = {}
        expstr["DT_RowId"]=dataset.id
        expstr["0"] = "" # this line intentionally left blank
        expstr["1"] = dataset.sampleName #sample name
        expstr["2"] = "SAM%s" % dataset.sampleReference #sample reference
        #runDetails
        runDetail = Run.objects.get(id=dataset.run_id)
        urlForRun = reverse('runView', args=(runDetail.runName,))
        expstr["3"] = "<a href=\"%s\">%s</a>" %(urlForRun, runDetail.runName)#run 
        expstr["4"] =  str(runDetail.date)#date
        expstr["5"] = dataset.lane.lane#lane
        expstr["6"] = dataset.readNumber#read one or read two, you don't get to choose
        expstr["7"] = dataset.barcode
        expstr["8"] = locale.format("%d", dataset.reads, grouping=True) # number of reads
        expstr["9"] = "%.2f" % (dataset.run.length*dataset.reads/1000000000.0) #Gbases
        expstr["10"] = "%s of %s" % (dataset.Q30Length, dataset.sequenceLength) #Q30 and sequence lengths
        expstr["11"] = dataset.percentGC #%GC
        #link to miso's library page
#        expstr["12"] = "<a href=http://ngs-miso.lifesci.dundee.ac.uk/miso/library/%s target=\"_blank\">LIB%s</a>" \
#                                % ( dataset.libraryReference.lstrip("LIB"), dataset.libraryReference.lstrip("LIB") )
        data["aaData"].append(expstr) 

    #render response
    return HttpResponse(json.dumps(data), 'application/json')


def sampleAjax(request, sample_id):
    """Get the full suite of details for the current sample.
    
    Renders a nice set of tabs containing detail inforamtion about a sample.
    Ajax returning HTML for the tabs in the dropdown for /gsuStats/run/<run name>.

    """
    #get the sample data
    sampleData = Sample.objects.get(id=sample_id)

    #fastQCDetails = buildFastQCDetials(sampleData)
    #generate the tab for the general details
    sampleDetails = buildSampleDetails(sampleData)
    #tab for the more technical details
    techDetails = buildTechDetails(sampleData)
    #tab for the contaminants image
    contaminantsImage = buildContaminantsImage(sampleData)
    contaminantsTable = buildContaminantsTable(sampleData)
    #tab for the fastQC summary pdf
    fQCDetails = buildFastQCDetails(sampleData)
    # build the json to return
    data = {}
    data["htmlTabs"] = buildTabsHTML(sample_id, sampleDetails, techDetails, \
                                    contaminantsImage, contaminantsTable, fQCDetails)
    return HttpResponse(json.dumps(data), 'application/json')
    

def buildSampleDetails(sampleData):
    """Builds the html/div for the sample data summary tab for the sample details.

    Returns a pair of html tables detailing the...erm....details.
    HTML for the first tab in /gsuStats/run/<run name> drop downs.
    Called by sampleAjax .

    """
    
    # make strings for the general details
    name_str = '<h1>Sample: %s (SAM%s)</h1>' \
                  % (sampleData.sampleName, sampleData.sampleReference)

    leftTable_str = '<table class="psteptable"><tr><th></th><th></th></tr>'
    runDetails = Run.objects.get(id=sampleData.run_id)
    run_str = '<tr><th>Run:</th><th>%s</th></tr><tr><th>Date:</th><th>%s</th></tr>' \
                % ( runDetails.runName, runDetails.date )
    projectName = Project.objects.get(id=sampleData.project_id)
    project_str = '<tr><th>Project:</th><th>%s</th></tr><tr><th>Owner:</th><th>%s</th></tr>' \
                    %( projectName.project, projectName.owner )
    barcode_str = '<tr><th>Barcode:</th><th>%s</th></tr>' %( sampleData.barcode )
    clientName_str = '<tr><th>Client Sample Name:</th><th>%s</th>' % sampleData.sampleDescription
    library_str = '<tr><th>Library:</th><th>%s</th></tr>' %( sampleData.libraryReference )
    species_str = '<tr><th>Species:</th><th>%s</th></tr>' % sampleData.species
    length_str = '<tr><th>Sequence Length:</th><th>%s</th></tr>' % ( sampleData.sequenceLength )
    insert_str = '<tr><th>Insert Size:</th><th>%s</th></tr>' % ( sampleData.insertLength )
    method_str = '<tr><th>Method:</th><th>%s</th></tr>' % ( sampleData.method )
    #concatonate all the above strings together
    sampleSummary = name_str + leftTable_str + run_str + project_str + clientName_str + barcode_str \
                    + library_str + length_str + species_str + insert_str + method_str + "</table>"

    #the table for the fastQC summary
    processing_str = '<h1>FastQC Summary:</h1>' \
                     '<table class="psteptable"><tr>' \
                     '<th>Test</th>' \
                     '<th>Result</th></tr>'
   
    seqQual = '<tr><td>Sequence Quality</td><td>%s</td>' % ( sampleData.sequenceQuality )
    seqQualScores = '<tr><td>Sequence Quality Scores</td><td>%s</td>' % ( sampleData.sequenceQualityScores )
    seqContent = '<tr><td>Sequence Content</td><td>%s</td>' % ( sampleData.sequenceContent )
    GCCont = '<tr><td>GC Content</td><td>%s</td>' % ( sampleData.GCContent )
    baseN = '<tr><td>Base N Content</td><td>%s</td>' % ( sampleData.baseNContent )
    seqLenDist = '<tr><td>Sequence Length Distribution</td><td>%s</td>' % ( sampleData.sequenceLengthDistribution )
    seqDupLev = '<tr><td>Sequence Duplication Levels</td><td>%s</td>' % ( sampleData.sequenceDuplicationLevels )
    overRep = '<tr><td>Overrepresented Sequences</td><td>%s</td>' % ( sampleData.overrepresentedSequences )
    kmerCont = '<tr><td>Kmer Contents</td><td>%s</td>' % ( sampleData.kmerContent )
   
    #concatonate the strings for the fastQC details   
    processing_str = processing_str + seqQual + seqQualScores + seqContent + GCCont \
                        + baseN + seqLenDist + seqDupLev + overRep + kmerCont
    processing_str = processing_str + "</table>"
    
    #add the two tables into the two divs 
    datasetdesc_div = '<div class="dsetsummary">%s</div>' \
                      '<div class="dsetprocessing">%s</div>' \
                      '' % (sampleSummary, processing_str )
    
    return(datasetdesc_div)


def buildTechDetails(sampleData):
    """ Builds the html/div for the technical details for the sample details tabs.

    Returns an HTML table for the technical details of the sample.
    HTML for the second tab in /gsuStats/run/<run name> drop down.
    Called by sampleAjax

    """
    # make strings
    name_str = '<h1>Sample: %s (%s)</h1>' \
                  % (sampleData.sampleName, sampleData.sampleReference)
    leftTable_str = '<table class="psteptable"><tr><th></th><th></th></tr>'
    md5_str = '<tr><th>MD5 Hash:</th><th>%s</th></tr>' %( sampleData.md5hash )

    #get the software details
    softwareVersion = sampleData.software.all()
    softwareAllStr = ""
    #for all the software, loop over and add them to the table 
    for softwareType in softwareVersion:
        if softwareType.parameters == "":
            software_str = '<tr><th>%s Version:</th><th>%s</th></tr>' %(softwareType.softwareName, softwareType.version)
        else:
            software_str = '<tr><th>%s Version:</th><th>%s (%s)</th></tr>' %(softwareType.softwareName, softwareType.version, softwareType.parameters)
        softwareAllStr = softwareAllStr + software_str 
    #concatonate all of the technical details together
    sampleSummary = name_str + leftTable_str + md5_str \
                    + softwareAllStr + "</table>"
    return(sampleSummary)

def buildContaminantsImage(sampleData):
    """Builds the html to display the image of the contaminants.

    HTML for the contaminants image and table tab of /gsuStats/run/<run name>
    Called by sampleAjax.

    """
    #make the strings
    name_str = '<h1>Sample: %s (%s)</h1>' \
                  % (sampleData.sampleName, sampleData.sampleReference)
    table_str = '<table class="psteptable">'
    #get the location of the image
    contaminantsFile = sampleData.contaminantsImage
    if contaminantsFile != "Null":
        contaminantsHTML = "<tr><th><img src=\"%s%s\" alt=\"FastqScreen Contaminants Check\"></tr></th><br />" %(settings.MEDIA_URL, contaminantsFile)
    else:
        contaminantsHTML = "<tr><th><H3>No FastQScreen Contaminants File Found</H3></th></tr><br />"
    
    
    leftTable  = name_str + table_str + contaminantsHTML + "</table>"

    #rightTable = '<table class="psteptable">'
    #rightHeaders = '<th>Organism</th><th>%OneHit</br>OneLibrary</th> \
    #                <th>%ManyHits</br>OneLibrary</th><th>%OneHitMany</br>Libraries</th> \
    #                <th>%ManyHits</br>ManyLibraries</th>'
    #
    #contaminantsDetails = ContaminantsDetails.objects.filter(sample_id=sampleData.id)
    #rightTable = rightTable + '<h1>Contaminants Details</h1><br><p>Hits no library: %s%%</p>' \
    #                    % contaminantsDetails[0].hitsNoLibraries
    #rightTable = rightTable + rightHeaders
    #for curOrganism in contaminantsDetails:
    #    currentLine = '<tr><td>%s</td><td>%.2f%%</td> \
    #                       <td>%.2f%%</td><td>%.2f%%</td><td>%.2f%%</td></tr>' \
    #                   %( curOrganism.organism, curOrganism.oneHitOneLib, \
    #                      curOrganism.manyHitOneLib, curOrganism.oneHitManyLib, \
    #                      curOrganism.manyHitManyLib) 
    #    rightTable = rightTable + currentLine

    #rightTable = rightTable + '</table>'
    returnString = '<div class="dsetsummary">%s</div>' \
                      '' % leftTable #, rightTable )
                   #   '<div class="dsetprocessing">%s</div>' \
    return(returnString)

def buildContaminantsTable(sampleData):
    """Builds the html to display the image of the contaminants.

    HTML for the contaminants image and table tab of /gsuStats/run/<run name>
    Called by sampleAjax.

    """
    #make the strings
    name_str = '<h1>Sample: %s (%s)</h1>' \
                  % (sampleData.sampleName, sampleData.sampleReference)
    #table_str = '<table class="psteptable">'
    #get the location of the image
    #contaminantsFile = sampleData.contaminantsImage
    #contaminantsHTML = "<tr><th><img src=\"%s%s\" alt=\"FastqScreen Contaminants Check\"></tr></th><br />" %(settings.MEDIA_URL, contaminantsFile)
    #
    #leftTable  = name_str + table_str + contaminantsHTML + "</table>"

    rightTable = '%s <table class="psteptable">' % name_str
    rightHeaders = '<th>Organism</th><th>%OneHit</br>OneLibrary</th> \
                    <th>%ManyHits</br>OneLibrary</th><th>%OneHitMany</br>Libraries</th> \
                    <th>%ManyHits</br>ManyLibraries</th>'
    
    try:
        contaminantsDetails = ContaminantsDetails.objects.filter(sample_id=sampleData.id)
        rightTable = rightTable + '<h1>Contaminants Details</h1><br><p>Hits no library: %s%%</p>' \
                            % contaminantsDetails[0].hitsNoLibraries
        rightTable = rightTable + rightHeaders
        for curOrganism in contaminantsDetails:
            currentLine = '<tr><td>%s</td><td>%.2f%%</td> \
                               <td>%.2f%%</td><td>%.2f%%</td><td>%.2f%%</td></tr>' \
                           %( curOrganism.organism, curOrganism.oneHitOneLib, \
                              curOrganism.manyHitOneLib, curOrganism.oneHitManyLib, \
                              curOrganism.manyHitManyLib) 
            rightTable = rightTable + currentLine
    except:
        rightTable = rightTable + '<h1>Contaminants Details</h1><br><p>Hits no library: %s%%</p>' \
                            % "-" 
        rightTable = rightTable + rightHeaders
        currentLine = '<tr><td>%s</td><td>%s</td> \
                           <td>%s</td><td>%s</td><td>%s</td></tr>' \
                       %( "-", "-", "-", "-", "-") 
        rightTable = rightTable + currentLine


    rightTable = rightTable + '</table>'
    returnString = '<div class="dsetsummary">%s</div>' \
                      '' % rightTable 
                    #  '<div class="dsetprocessing">%s</div>' \
    return(returnString)

def buildFastQCDetails(sampleData):
    """Builds the html to embed the fastQC summary pdf.

    HTML for the fastQC pdf tab in /gsuStats/run/<run name> drop downs
    Called by sampleAjax.

    """
    #create the strings
    name_str = '<h1>Sample: %s (%s)</h1>' \
                  % (sampleData.sampleName, sampleData.sampleReference)
    #table_str = '<table class="psteptable">'
    fastQCFile = sampleData.fastQCSummary
    #embed the pdf
    fastQCHTML = "<embed height=\"400\" width=\"100%%\"  name=\"plugin\" \
                 src=\"%s%s\"  type=\"application/pdf\">" %(settings.MEDIA_URL, fastQCFile)
    #fastQCline = "<a href=\"javascript:void(null);\" onclick=\"pdfPopup();\">Open</a>"

    returnString = name_str + fastQCHTML
    return(returnString)

def buildTabsHTML(sample_id, sampleDetails, techDetails, contaminantsImage, contaminantsTable, fQCDetails):
    """Builds the tabs for the drop-down information in the run-overview tables.

    Input is the ouput from buildFastQCDetails, buildSampleDetails and buildTechDetails.
    Called by sampleAjax to construct the divs for the dropdown in /gsuStats/run/<run name>

    """
    #create our epic string
    returnStr = '''
    <div id="subtabs" class="subtabs">
        <ul id="datasettabs">
            <li id="dataset%stab">
                <a href="#summary%stab-div">Summary Information</a>
            </li>
            <li id="stats%stab">
                <a href="#stats%stab-div">Technical Summary</a>
            </li>
            <li id="contaminantsI%stab">
                <a href="#contaminantsI%stab-div">Contaminants Plot</a>
            </li>
            <li id="contaminantsT%stab">
                <a href="#contaminantsT%stab-div">Contaminants Table</a>
            </li>
             <li id="fastQC%stab">
                <a href="#fastQC%stab-div">FastQC Summary</a>
            </li>
        </ul>
        
        <div id="summary%stab-div" class="subtab">
            %s
        </div>
        <div id="stats%stab-div" class="subtab">
            %s
        </div>
        <div id="contaminantsI%stab-div" class="subtab">
            %s
        </div>
        <div id="contaminantsT%stab-div" class="subtab">
            %s
        </div>
         <div id="fastQC%stab-div" class="subtab">
            %s
        </div>
    </div> ''' % (sample_id,sample_id,sample_id,sample_id,sample_id,
                  sample_id,sample_id,sample_id,sample_id,sample_id,
                  sample_id, sampleDetails, 
                  sample_id, techDetails,
                  sample_id, contaminantsImage,
                  sample_id, contaminantsTable,
                  sample_id, fQCDetails)
    #aaaaand return it.
    return(re.sub("\n", "", re.sub("\t", "", returnStr)))

def runSummaryAjax(request, run_id):
    """Get the full suite of details for the current run.
        
    Creates a table to display a summary for each lane of a run, inc undetermined reads.
    Ajax containing HTML for the dropdown of /gsuStats/run

    """
    #get the run data!
    runData = Run.objects.get(id=run_id)
    
    #generate the rables
    runDetails = buildRunDetails(runData)
    laneDetails = buildAllLaneDetails(runData)

    laneDetailsDict = laneDetails[0]
    laneJSONDetails = laneDetails[1]
    runNotes = runData.notes.replace("\r\n","</br>")
    runNoteString = """<p>%s</p>
                        <a style="color:blue" href="/runNotes/%s">Edit Note</a>""" \
                            % (runNotes, runData.runName)
    # build the json to return
    data = {}
    #fully generate the tabs
    data["htmlTabs"] = buildRunTabsHTML(run_id, runDetails, laneDetailsDict, runNoteString)
    data["laneDetails"] = laneJSONDetails
    data["runID"]= run_id
    #return of the string
    return HttpResponse(json.dumps(data), 'application/json')


def buildAllLaneDetails(runData):
    """Build summary ajax for the given run.

    Called by runSummaryAjax to provide the content for the lane tabs of 
    /gsuStats/run/ and to return an array of lane numbers and urls that will be
    parsed to the javascript (getRunDetails and funcLaneDetails in 
    almostSignificant_base.js).

    """
    lanes = Lane.objects.filter(run_id=runData.id)
    laneOutputDict = {}
    laneOutputForAjax = {}
    sampleDetailsTable = "<table><tr><th>Sample</th><th>Reads</th><th>Gbases</th></tr>"
    for lane in lanes:
        content = sampleDetailsTable
        samples = Sample.objects.filter(lane_id=lane.id)
        tempSampleDict = {}
        for sample in samples:
            if sample.sampleName in tempSampleDict.keys():
                tempSampleDict[sample.sampleName][0] = \
                                        tempSampleDict[sample.sampleName][0] + sample.reads
                tempSampleDict[sample.sampleName][1] = tempSampleDict[sample.sampleName][1] \
                                                        + sample.reads*runData.length
            else:
                tempSampleDict[sample.sampleName] = [sample.reads, sample.reads*runData.length]
        for key,value in iter(sorted(tempSampleDict.iteritems())):
            content = "%s<tr><td>%s</td><td>%.2fM</td><td>%.2fGb</td></tr>" \
                    %( content, key, value[0]/1000000.0, value[1]/1000000000.0)
        content = "%s</table>" % content
        laneOutputDict[lane.lane] = content
        laneOutputForAjax[lane.lane] = "run/%s/%s/Ajax/" % (runData.runName, lane.lane)
    return (laneOutputDict, laneOutputForAjax)
        

def buildRunDetails(runData):
    """Builds the html/div for the run data summary tab.

    Creates a table that shows all of the details for the lanes in the run.
    Includes the number of samples and the undetermined indices for each lane.
    Called by runSummaryAjax. HTML for the first tab of /gsuStats/run/ drop down.
    
    """
    # make strings
    name_str = '<h1>Run: %s </h1>' \
                  % (runData.runName)

    leftTable_str = '<table class="psteptable"><tr><th></th><th></th></tr>'
    #get all the lanes for the run
    #create a dictionary with all the information we need for each lane
    lanesAll = Lane.objects.filter(run_id=runData.id)
    laneStr = ""
    laneDict = {}
    #loop over the lanes
    for lane in lanesAll:
        laneKey = lane.lane
        #get the sample related data, reads, gb etc
        laneSamples = Sample.objects.filter(lane_id=lane.id)
        readsTuple = laneSamples.values_list("reads")
        #values list returns a list, so sum over the list and get the total
        numberOfReads = 0
        for reads in readsTuple:
            numberOfReads += reads[0]
        Gbases = numberOfReads * runData.length
        samplesValue = len(laneSamples)
        readsValue = "%.2fm" %( numberOfReads/1000000.0 )
        baseValue = "%.2fGb" %( Gbases/1000000000.0 )
        clusterDensity = "%s &plusmn; %s" %( lane.clusterDensity, lane.clusterDensityStdDev )
        print(lane.totalUndetIndexes)
        if lane.totalUndetIndexes != None:
            totalUndet = locale.format("%d", lane.totalUndetIndexes, grouping=True)
            print("Lane:", lane, ". totUndet: ", lane.totalUndetIndexes)
        else:
            totalUndet = "-"
        #get the undetermined indices
        undetIndex = UndeterminedIndex.objects.filter(lane_id=lane.id).order_by('-occurances').values_list('index','occurances')
        #concatonate the strings!
        #laneDict[ laneKey ] = [ densityValue, samplesValue, readsValue, baseValue,\
        #                        percPFValue, percOverQ30Value, undetIndex] 
        laneDict[ laneKey ] = [ samplesValue, readsValue, baseValue, totalUndet, undetIndex, clusterDensity]

    #initialise the lines of the table
    titleStr = '<tr><th>Lane:</th>'
    samples = '<tr><td>Number of Samples:</td>'
    reads = '<tr><td>Number of Reads passing filter:</td>' 
    clusterDensity = '<tr><td>Cluster Density k/mm:</td>' 
    totUndet = '<tr><td>Total Undetermined Index Reads:</td>'
    gbasesLine = '<tr><td>Number of Bases:</td>'
    undetIndexLines =  ['<tr><td>Undet Index:</td>','<tr><td>Undet Index:</td>',\
                        '<tr><td>Undet Index:</td>','<tr><td>Undet Index:</td>',\
                        '<tr><td>Undet Index:</td>','<tr><td>Undet Index:</td>',\
                        '<tr><td>Undet Index:</td>','<tr><td>Undet Index:</td>',
                        '<tr><td>Undet Index:</td>','<tr><td>Undet Index:</td>']
    #fill in the lines from the details in the dict we created above
    for lane,detailsArray in laneDict.iteritems():
        titleStr = titleStr + "<td>%s</td>" %( lane )
        if runData.pairedSingle.find("Paired") != -1:
            samples = samples + "<td>%s</td>" %( detailsArray[0]/2 )
        else:
            samples = samples + "<td>%s</td>" %( detailsArray[0] )
        reads = reads + "<td>%s</td>" %( detailsArray[1] )
        gbasesLine = gbasesLine + "<td>%s</td>" %( detailsArray[2] )
        totUndet = totUndet + "<td>%s</td>" %( detailsArray[3] )
        print ( "details array 3 %s" % detailsArray[3] )
        clusterDensity = clusterDensity + "<td>%s</td>" %( detailsArray[5] )
        #loop over the undetermined index
        #this is slightly complicated as we need space for the top ten, but there can be anywhere 
        #between 0 and 10 undetermined indices.
        undetIndexLine = ""
        counter=0
        if len(detailsArray[4]) > 0:
            for index,occurance in detailsArray[4]:
                textColor="black"
                if occurance > 1000000:
                    textColor="red"
                undetIndexLines[counter] = undetIndexLines[counter] \
                                           + "<td style=\"color:%s\">%s (%s)</td>" \
                                           %(textColor, index, occurance)
                counter += 1
            #handles occasions when fewer than 10 undets
            if counter < 10:
                while counter < 10:
                    undetIndexLines[counter] = undetIndexLines[counter] + "<td>-</td>"
                    counter += 1
        #handles occasions when there are no undets
        else:
            while counter <10: 
                undetIndexLines[counter] = undetIndexLines[counter] + "<td>-</td>"
                counter += 1
            
            
    #close the lines. Can't have open rows now can we?
    titleStr = titleStr + "</tr>"
    samples = samples + "</tr>"
    reads = reads + "</tr>"
    gbasesLine = gbasesLine + "</tr>"
    totUndet = totUndet + "</tr>"
    clusterDensity = clusterDensity + "</tr>"
    runSummary = name_str + leftTable_str + titleStr + samples + reads + \
                        gbasesLine + clusterDensity + totUndet
    #loop over the undetermined index
    for undetIndexLine in undetIndexLines:
        undetIndexLine = undetIndexLine + "</tr>"
        runSummary = runSummary + undetIndexLine
    #and close the table
    runSummary = runSummary + "</table>"

    #add it all to a div.
    datasetdesc_div = '<div class="dsetsummary">%s</div>' %( runSummary )
    
    return(datasetdesc_div)


def buildRunTabsHTML(run_id, runDetails, laneDetailsDict, runNotes):
    """Builds the tabs for the drop-down information in the run-overview tables.

    Input is the ouput from buildRunDetails and buildAllLaneDetails.
    HTML for the drop down in /gsuStats/run
    
    """
    #generate our return string
    returnStr = '''
    <div id="subtabs" class="subtabs">
        <ul id="datasettabs">
            <li id="dataset%stab">
                <a href="#summary%stab-div">Summary Information</a>
            </li>
            <li id="notes%stab">
                <a href="#notes%stab-div">Notes</a>
            </li>''' % (run_id, run_id, run_id, run_id)
    for lane, content in laneDetailsDict.iteritems():
        laneDiv = '<li id="run%slane%stab"><a href="#run%slane%stab-div">Lane %s</a></li>' \
                    %( run_id, lane, run_id,lane, lane )
        returnStr = returnStr + laneDiv
    returnStr = returnStr + '</ul>' 
    returnStr = returnStr + '<div id="summary%stab-div" class="subtab">%s</div>'\
                     % (run_id, runDetails) 
    returnStr = returnStr + '<div id="notes%stab-div" class="subtab">%s</div>'\
                     % (run_id, runNotes) 
    for lane, content in laneDetailsDict.iteritems():
        laneTabContent = '<div id="r%sl%splot" class="laneplot"></div>' \
                         '<div class="lanetable">%s</div>' \
                      '' % (run_id, lane, content )
   
        laneStr = '<div id="run%slane%stab-div" class="subtab">%s</div>' \
                                %(run_id,lane, laneTabContent)
        returnStr = returnStr + laneStr
    
    returnStr = returnStr + '</div>'
    #return it
 
    return(re.sub("\n", "", re.sub("\t", "", returnStr)))

def ProjectDetailViewHTML(request, projectID):
    """Creates a HTML table detailing the specifics of a project.

    Designed to be copy and pasted into emails for Mel.
    The table is a brief summary of the quality and size of the samples for a project
    HTML table for /gsuStats/html/<project id>

    """
    #renders the project overview as a html table
    #gather all the data for all the samples in the project 
    projectData = get_object_or_404(Project, id=projectID)
    sampleData = Sample.objects.filter(project_id=projectID)
    header = "<h1>%s</h1>"  % projectData.project
    tableStart = "<table border='1' cellpadding='4'>" 
    tableHeader = '<tr><th>Sample Name</th><th>Reference</th><th>Run Name</th> \
                   <th>Run Date</th><th>Lane</th><th>Read Number</th> \
                   <th>No. Reads</th><th>GBases</th><th>Q30 Length</th>\
                   <th>%GC Content</th><th>Index</th>\
                   <th>Insert Size</th></tr>'
    tableClose = "</table>"
    tableRowsHTML = header + tableStart + tableHeader
    runDetail = sampleData[0]
    #loop over all of the samples.
    for dataset in sampleData:
        tempDataArray = []
        #runDetails
        if dataset.run_id != runDetail.id:
            runDetail = Run.objects.get(id=dataset.run_id)
        tempDataArray.append(dataset.sampleDescription)
        tempDataArray.append(dataset.sampleName)
        tempDataArray.append("SAM%s" % dataset.sampleReference)
        tempDataArray.append( runDetail.runName)
        tempDataArray.append( str(runDetail.date))
        tempDataArray.append(dataset.lane.lane)
        tempDataArray.append(dataset.readNumber)
        tempDataArray.append(locale.format("%d", dataset.reads, grouping=True))
        tempDataArray.append("%.2f" % (dataset.run.length*dataset.reads/1000000000.0))
        tempDataArray.append("%s of %s" % (dataset.Q30Length, dataset.sequenceLength))
        tempDataArray.append(dataset.percentGC)
        tempDataArray.append(dataset.barcode)
        tempDataArray.append(dataset.insertLength)
        tableRow = "<tr><td>%s</td><td>%s (%s)</td><td>%s</td><td>%s</td><td align='center'>%s</td> \
                    <td align='center'>%s</td><td>%s</td><td align='center'>%s</td><td>%s</td> \
                    <td align='center'>%s</td><td>%s</td><td>%s</td></tr>" \
                    % ( tempDataArray[0], tempDataArray[1], tempDataArray[2], \
                        tempDataArray[3], tempDataArray[4], tempDataArray[5], \
                        tempDataArray[6], tempDataArray[7], tempDataArray[8], \
                        tempDataArray[9], tempDataArray[10], tempDataArray[11],\
                        tempDataArray[12])
        tableRowsHTML += tableRow 
    #generate a html table that contains all of this data in it.
    tableRowsHTML += tableClose
    print "yes"
    print tableRowsHTML

    return HttpResponse(tableRowsHTML)

def stupidStats(response):
    """Generates some stupid stats for the GSU.

    Can be found at /gsuStats/stupidStats

    """
    #set the sizes of single bases
    dnaLength = 3.4e-10
    dnaVolume = 3.4e-10**3
    #get the number of reads and gb of dna
    details = Run.objects.all()
    numberOfRuns = len(details)
    numberOfSamples = len(Sample.objects.filter(readNumber=1))
    readsAndRunID = Sample.objects.only("reads","run_id").values_list("reads","run_id")
    #values list returns a list, so sum over the list and get the total
    #numberOfReads = [sum(x) for x in zip(*readsAndLength)][0]
    numberOfReads = 0
    Gbases = 0
    prevRunId = 0
    curRunLength = 0
    for reads,curRunId in readsAndRunID:
        if curRunId != prevRunId:
            prevRunId = curRunId
            curRunLength = Run.objects.get(id=curRunId).length
        curGbases = reads * curRunLength
        Gbases += curGbases 
        numberOfReads += reads
   
    #calculate the length and volume of dna
    totalLength = dnaLength * Gbases
    totalVolume = dnaVolume * Gbases
    
   
    outputHTML='<h1>Stupid, but interesting, Stats</h1>'
    readsHTML ='<h3>Total Reads: %sm</h3>'\
                 % ( locale.format("%d", round(numberOfReads/1000000.0, -1), grouping=True ))
    basesHTML ="<h3>Total Bases: %sGb (that's %.1f trillion bases of DNA!)</h3>"\
         % ( locale.format("%d", round(Gbases/1000000000, -1), grouping=True),\
             Gbases/1000000000000.0 )
    lengthHTML='<h3>Total Length of DNA: %s meters</h3>'\
                 % locale.format("%d", round(totalLength, -1), grouping=True)
    volumeHTML='<h3>Total Volume of DNA: %.2Em<sup>3</sup></h3>' % totalVolume
    
    wikiAvWords = 581 # based off of rough caluclulations
    engAvChars = 4.5
    #approx 4.3million articles with 2.5billion words. Average english word is 4.5 letters
    wikiAvChars = wikiAvWords*engAvChars
    numWikiArticles = Gbases / wikiAvChars
    wikiHTML = '<h3>%sG bases would fill a (very rough) average %sm wikipedia articles.</h3>' \
                      % ( locale.format("%d", round(Gbases/1000000000, -1), grouping=True),\
                          locale.format("%d", round(numWikiArticles/1000000, -1), grouping=True) )
    #length of the killer whale genome
    killerWhaleLength = 2372919877.0
    humanLength = 3000000000.0
    #how many times we could have sequences a killer whale.
    numberOfKillerPeople = Gbases / humanLength
    numberOfKillerWhales = Gbases / killerWhaleLength
    whaleHTML = '<h3>We have sequenced the equivilent of %s humans, \
                                        or %s Killer Whales.</h3><br>' \
                % ( locale.format("%d", round(numberOfKillerPeople, -1), grouping=True) ,\
                     locale.format("%d", round(numberOfKillerWhales, -1), grouping=True)  )

    #height if printed, double sides size 11
    wordsPerPage = 2295*2
    pageThickness = 0.0001
    pageLength = 0.297
    everestHeight = 8848 
    benNevisHeight = 1334
    blueWhaleLength = 30
    numberOfPages=Gbases / wordsPerPage
    paperHeight = numberOfPages * pageThickness
    everests = paperHeight / everestHeight
    nevises = paperHeight / benNevisHeight
    blueWhales = pageLength*numberOfPages / blueWhaleLength
    pagesHTML = '<h3>Printed at size 11, on A4, double sided, \
                    we would need %s million pages of A4 paper.<br>\
                  As a single stack this would be %skm tall (into the thermosphere)<br> \
                    That\'s the same height as %.1f Ben Nevis\' or %.1f Everests.<br> \
                Laid end to end this is the same length as %.1f million Blue Whales.</h3>' \
               % ( locale.format("%d", round(numberOfPages/1000000.0, -1) , grouping=True), \
                   locale.format("%d", paperHeight/1000  , grouping=True), \
                    nevises, everests, \
                    blueWhales/1000000 )
    #concatonate the strings together. 

    recordWordsPerMinute = 200
    recordWordsPerSecond = 200*5/60 #a word in typing is 5 characters
    timeToTypeSeconds = recordWordsPerSecond * Gbases
    timeToTypeMinutes = timeToTypeSeconds/60
    timeToTypeHours = timeToTypeMinutes/60
    timeToTypeDays = timeToTypeHours/24
    timeToTypeYears = timeToTypeDays/365
    timeToTypeYearsFormatted = locale.format("%d", timeToTypeYears, grouping=True) # number of reads
    typingHTML = "<h3>Typing a a world record speed of 200 words per minute, it would take %.1f million years to type all of the bases.<br>\
                    The genus <i>Homo</i> is only 2.5million years old. The first mammoth fossils are 5 million years old." \
                %( timeToTypeYears/1000000.0 )
    outputHTML = outputHTML + readsHTML + basesHTML + lengthHTML + \
                        wikiHTML + whaleHTML + pagesHTML + typingHTML
    return HttpResponse(outputHTML)    

#def getDatasetDetailsAjax(request):
#def run(request):
#    #need to get the table id of the given runID
#    run_key = Run.objects.filter(runName=runID).values("id")
#    #then need to get all samples for this run (ie with this run_id)
#    runSummary = Sample.objects.filter(run_id=run_key).values("sampleReference","Q30Length","sequenceLength","readNumber","lane", "overrepresentedSequences","percentGC","QCSummaryLocation")
#    table = SampleTable(runSummary, runID)
#    #format it into the django_tables2 table
#    RequestConfig(request).configure(table)
#    #return the render!
#    return render(request, "runView.html", {'table':table})
#
#def sample(request):
#    #need to get the table id of the given runID
#    run_key = Run.objects.filter(runName=runID).values("id")
#    #then need to get all samples for this run (ie with this run_id)
#    runSummary = Sample.objects.filter(run_id=run_key, sampleReference=sampleRef)
#    table = SampleTable(runSummary, runID)
#    #format it into the django_tables2 table
#    RequestConfig(request).configure(table)
#    #return the render!
#    return render(request, "sampleView.html", {'table':table})
#
#

def projectSummaryAjax(request, project_id):
    """Get the full suite of details for the current run.
        
    Creates a table to display a summary for each lane of a run, inc undetermined reads.
    Ajax containing HTML for the dropdown of /gsuStats/projects

    """
    #get the run data!
    projectData = Project.objects.get(id=project_id)
    
    #generate the rables
    sampleDetails = buildProjectDetails(projectData)

    projectNotes = projectData.notes.replace("\r\n","</br>")
    projectNoteString = """<p>%s</p>
                       <a style="color:blue" href="/projectNotes/%s">Edit Note</a>""" \
                            % (projectNotes, projectData.project)
 # build the json to return
    data = {}
    #fully generate the tabs
    data["htmlTabs"] = buildProjectTabsHTML(project_id, sampleDetails, projectNoteString)
    data["runID"]= project_id
    #return of the string
    return HttpResponse(json.dumps(data), 'application/json')

def buildProjectDetails(projectData):
    """Builds the html/div for the run data summary tab.

    Creates a table that shows all of the details for the lanes in the run.
    Includes the number of samples and the undetermined indices for each lane.
    Called by runSummaryAjax. HTML for the first tab of /gsuStats/projects/ drop down.
    
    """
    # make strings
    name_str = '<h1>Project: %s </h1>' \
                  % (projectData.project)

    leftTable_str = '<table class="psteptable">'
    #get all the lanes for the run
    #create a dictionary with all the information we need for each lane
    sampleAll = Sample.objects.filter(project_id=projectData.id)
    sampleStr = ""
    sampleDict = {} #0: reads array, 1: Gbases, 2: number of times sampleName in db, \
                        # 3: number of fails, 4:array of covered runs
    #loop over the lanes
    for sample in sampleAll:
            #if sample already in the dict, get the highest reads, highest gb and incremement run
            if sample.sampleName in sampleDict.keys(): #if we've seen the sample before
                if sample.QCStatus != "fail": #and the current run didn't fail
                    print(sampleDict[sample.sampleName])
                    if [sample.run_id,sample.lane_id] in sampleDict[sample.sampleName][4]: 
                        #and we've seen the run/lane combo before
                        sampleDict[sample.sampleName][0].append(sample.reads)
                        sampleDict[sample.sampleName][1] = sampleDict[sample.sampleName][1] + \
                                                sample.reads * sample.run.length  
                    elif [sample.run_id,sample.lane_id] not in sampleDict[sample.sampleName][4]: 
                        #and we've not seen the run/lane combo before
                        print(sampleDict[sample.sampleName][0])
                        sampleDict[sample.sampleName][0].append(sample.reads)
                        sampleDict[sample.sampleName][1] = sampleDict[sample.sampleName][1] + \
                                                            sample.reads * sample.run.length
                        sampleDict[sample.sampleName][2] = sampleDict[sample.sampleName][2] +1
                        sampleDict[sample.sampleName][4].append([sample.run_id, sample.lane_id])
                elif sample.QCStatus == "fail" \
                  and [sample.run_id,sample.lane_id] not in sampleDict[sample.sampleName][4]: 
                    #and the current run did fail but we've not seen it.
                    sampleDict[sample.sampleName][2] = sampleDict[sample.sampleName][2] + 1
                    sampleDict[sample.sampleName][3] = sampleDict[sample.sampleName][3] + 1
                    sampleDict[sample.sampleName][4].append([sample.run_id, sample.lane_id])
            #otherwise, add it to the dict, add the reads and start the number of runs
            elif sample.QCStatus == "fail": #if it failed, initialise as 0
                sampleDict[sample.sampleName] = [[0], 0,\
                                                 1,1, [[sample.run_id,sample.lane_id]]]
            else: #if we've never seen the sample and it didn't fail, add it normally
                sampleDict[sample.sampleName] = [[sample.reads], sample.reads*sample.run.length,\
                                                 1,0, [[sample.run_id,sample.lane_id]]]

    titleStr = """<thead><tr><th>Sample</th><th>Reads</th><th>GBases</th>
                    <th>Times Run</th><th>Times Failed</th><tr></thead><tbody>"""
    htmlLine = ""
    for sample,detailsArray in iter(sorted(sampleDict.iteritems())):
        htmlLine = "%s<tr><td>%s</td><td>%.2fM</td><td>%.2fGb</td><td>%d</td><td>%d</td></tr>" \
                    %( htmlLine, sample, sum(detailsArray[0])/1000000.0, \
                       detailsArray[1]/1000000000.0, detailsArray[2], detailsArray[3])
        
            
    projectSummary = name_str + leftTable_str + titleStr + htmlLine + "<tbody></table>"

    #add it all to a div.
    datasetdesc_div = '<div class="dsetsummary">%s</div>' %( projectSummary )
    
    return(datasetdesc_div)


def buildProjectTabsHTML(project_id, projectDetails, projectNotes):
    """Builds the tabs for the drop-down information in the run-overview tables.

    Input is the ouput from buildRunDetails and buildAllLaneDetails.
    HTML for the drop down in /gsuStats/projects
    
    """
    #generate our return string
    returnStr = '''
    <div id="subtabs" class="subtabs">
        <ul id="datasettabs">
            <li id="dataset%stab">
                <a href="#summary%stab-div">Summary Information</a>
            </li>
            <li id=notes%stab">
                <a href="#notes%stab-div">Notes</a>
            </li>''' % (project_id, project_id, project_id, project_id)
#    for lane, content in laneDetailsDict.iteritems():
#        laneDiv = '<li id="run%slane%stab"><a href="#run%slane%stab-div">Lane %s</a></li>' \
#                    %( run_id, lane, run_id,lane, lane )
#        returnStr = returnStr + laneDiv
    returnStr = returnStr + '</ul>' 
    returnStr = returnStr + '<div id="summary%stab-div" class="subtab">%s</div>'\
                     % (project_id, projectDetails) 
    returnStr = returnStr + '<div id="notes%stab-div" class="subtab">%s</div>'\
                     % (project_id, projectNotes) 
    
#    for lane, content in laneDetailsDict.iteritems():
#        laneTabContent = '<div id="r%sl%splot" class="laneplot"></div>' \
#                         '<div class="lanetable">%s</div>' \
#                      '' % (run_id, lane, content )
#   
#        laneStr = '<div id="run%slane%stab-div" class="subtab">%s</div>' \
#                                %(run_id,lane, laneTabContent)
#        returnStr = returnStr + laneStr
    returnStr = returnStr + '</div>'
    print returnStr
    #return it
 
    return(re.sub("\n", "", re.sub("\t", "", returnStr)))

def statisticsAjax(request):
    """Loads ajax for the statistics tables.

    Called by statistics at gsuStats/statsAjax. 
    """
    data={"aaData":[]}

    cols = [
        {
            "sTitle":"",
            "bSortable":False,
            "bSearchable":False,
            "sWidth":"60px"
        },
        {
            "sTitle":"Machine",
            "bSortable":True
        },
        {
            "sTitle":"Run Type",
            "bSortable":True
        },
        {
            "sTitle":"Mean Reads per FC / M",
            "bSortable":True,
            "sClass":"centerTable"            
        },
        {
            "sTitle":"Mean Gb per FC / Gb",
            "bSortable":True,
            "sClass":"centerTable"            
        },       
        {
            "sTitle":"Mean Reads per Lane / M",
            "bSortable":True,
            "sClass":"centerTable"            
        },
        {
            "sTitle":"Mean Gb per Lane / Gb",
            "bSortable":True,
            "sClass":"centerTable"            
        },
        {
            "sTitle":"No. Flow Cells",
            "bSortable":True,
            "sClass":"centerTable"            
        },
        {
            "sTitle":"No. Lanes",
            "bSortable":True,
            "sClass":"centerTable"            
        },
        {
            "sTitle":"Mean Q30",
            "bSortable":True,
            "sClass":"centerTable"            
        }
  ]
 
    
    data["aaSorting"] = [[1,"desc"]]
    data["aoColumns"] = cols
 
    #2D Array
    #Array needs five elements. First is the desired name, second is the machine type,
    #third is the strategy type eg Paired End
    #fourth is the lower boundry for the length and the fifth is the upper length boundry
    machineLengthArray = [ ["75BP PE", "NextSeq", "paired", 70,80],
                           ["100BP PE", "NextSeq", "paired", 90,110],
                           ["150BP SE", "NextSeq", "paired", 140,160],
                           ["75BP SE", "NextSeq", "single", 70,80],
                           ["100BP SE", "NextSeq", "single", 90,110],
                           ["150BP SE", "NextSeq", "single", 140,160],
                            #
                           ["50BP PE", "HiSeq", "paired" ,49,60] ,
                           ["100BP PE","HiSeq",  "paired" ,90,110], 
                           ["50BP SE", "HiSeq", "single" ,40,60] ,
                           ["100BP SE", "HiSeq", "single" ,90,110] ,
                            #
                           ["150BP PE","MiSeq",  "paired" ,140,160], 
                           ["150BP SE","MiSeq",  "single" ,140,160], 
                           ["75BP PE", "MiSeq", "paired" ,70,80] ,
                           ["250BP PE", "MiSeq", "paired" ,240,260] ]
    #
    for runTypeData in machineLengthArray:
        desiredName = runTypeData[0]
        machineType = runTypeData[1]
        strategy = runTypeData[2]
        lowerLength = runTypeData[3]
        upperLength = runTypeData[4]    
        if strategy == "Paired End" or strategy == "paired":
            shortStrat="P"
        else:
            shortStrat="S"
        rowID = "_".join([machineType,shortStrat,str(lowerLength),str(upperLength)])
        #get all runs with a length over 99
        print runTypeData
        all100bpRuns = Run.objects.filter(length__gt=lowerLength, length__lt=upperLength,\
                                                machineType=machineType,\
                                                pairedSingle=strategy)
        if all100bpRuns.count() > 0:
            allLaneReads = []
            allLaneReadsWithUndet = []
            allLaneGb = []
            allLaneGbWithUndet = []
            allRunReads = [] 
            allRunReadsWithUndet = [] 
            allRunGb = []
            allRunGbWithUndet = []
            allQ30 = []
            #loop over them
            for run in all100bpRuns:
                runReads = 0
                runReadsWithUndet = 0
                runGb = 0
                runGbWithUndet = 0
                #get all the samples for the run
                samples = Sample.objects.filter(run_id=run.id)
                #get all the lanes for the run
                lanes = Lane.objects.filter(run_id=run.id)
                
                #loop over the lanes
                for lane in lanes:
                    laneReads = 0
                    laneGb = 0
                    if lane.totalUndetIndexes != None:
                        laneReadsWithUndet = lane.totalUndetIndexes
                        laneGbWithUndet = lane.totalUndetIndexes * run.length
                    else:
                        laneReadsWithUndet = 0
                        laneGbWithUndet = 0
                    #get the samples for the lane
                    laneSamples = samples.filter(lane_id=lane.id)
                    
                    for sample in laneSamples:
                        #number of reads for the lane DONT FORGET UNDET READS
                        laneReads = laneReads + sample.reads
                        laneReadsWithUndet = laneReadsWithUndet + sample.reads
                        #number of GB for the lane DONT FORGET UNDET READS
                        laneGb = laneGb + sample.reads*run.length
                        laneGbWithUndet = laneGbWithUndet + sample.reads*run.length
                        #Q30 array for the lane
                        allQ30.append(sample.Q30Length)
                    #add reads to master array
                    allLaneReads.append(laneReads)
                    allLaneReadsWithUndet.append(laneReadsWithUndet)
                    #add GB to master array
                    allLaneGb.append(laneGb)
                    allLaneGbWithUndet.append(laneGbWithUndet)
                    
                    #number of reads for the lane DONT FORGET UNDET READS
                    runReads = runReads + laneReads
                    runReadsWithUndet = runReadsWithUndet + laneReadsWithUndet
                    #number of GB for the lane DONT FORGET UNDET READS
                    runGb = runGb + laneGb 
                    runGbWithUndet = runGbWithUndet + laneGbWithUndet
                    #Q30 array for the lane
                allRunReads.append(runReads)
                allRunReadsWithUndet.append(runReadsWithUndet)
                allRunGb.append(runGb)
                allRunGbWithUndet.append(runGbWithUndet)

            #take mean and SD for the runs read array
            if allRunReads != []:
                meanRunReads = "%.2fM" % (float(numpy.mean(allRunReads))/1000000.0)
                sdRunReads = "%.2fM" % (float(numpy.std(allRunReads))/1000000.0)
                runMinReads ="%.2fM" % (float(min(allRunReads))/1000000.0)
                runMaxReads ="%.2fM" % (float(min(allRunReads))/1000000.0)
            else:
                meanRunReads = 0
                sdRunReads = 0
                runMinReads =0
                runMaxReads =0
            #mean and SD for the runs GB array
            if allRunGb != []:
                meanRunGb = "%.2fGb" % (float(numpy.mean(allRunGb))/1000000000.0)
                sdRunGb = "%.2fGb" % (float(numpy.std(allRunGb))/1000000000.0)
                runMinGb ="%.2fGb" % (float(min(allRunGb))/1000000000.0)
                runMaxGb ="%.2fGb" % (float(min(allRunGb))/1000000000.0)
            else:
                meanRunGb = 0
                sdRunGb = 0
                runMinGb =0
                runMaxGb =0
            #mean and sd for the lane reads array
            if allLaneReads != []:
                meanLaneReads = "%.2fM" % (float(numpy.mean(allLaneReads))/1000000.0)
                sdLaneReads = "%.2fM" % (float(numpy.std(allLaneReads))/1000000.0)
                laneMinReads = "%.2fM" % (float(min(allLaneReads))/1000000.0)
                laneMaxReads ="%.2fM" % (float(max(allLaneReads))/1000000.0)
            else:
                meanLaneReads = 0
                sdLaneReads = 0
                laneMinReads = 0
                laneMaxReads =0
            #mean and sd for the lane GB array
            if allLaneGb != []:
                meanLaneGb = "%.2fGb" % (float(numpy.mean(allLaneGb))/1000000000.0)
                sdLaneGb = "%.2fGb" % (float(numpy.std(allLaneGb))/1000000000.0)
                laneMinGb ="%.2fGb" % (float(min(allLaneGb))/1000000000.0)
                laneMaxGb ="%.2fGb" % (float(max(allLaneGb))/1000000000.0)
            else:
                meanLaneGb = 0
                sdLaneGb = 0
                laneMinGb =0
                laneMaxGb =0
            #take mean and SD for the runs read array
            if allRunReadsWithUndet != []:
                meanRunReadsWithUndet = "%.2f" % (float(numpy.mean(allRunReadsWithUndet))/1000000.0)
                sdRunReadsWithUndet = "%.2f" % (float(numpy.std(allRunReadsWithUndet))/1000000.0)
                runMinReadsWithUndet = "%.2fM" % (float(min(allRunReadsWithUndet))/1000000.0)
                runMaxReadsWithUndet = "%.2fM" % (float(min(allRunReadsWithUndet))/1000000.0)
            else:
                meanRunReadsWithUndet = 0
                sdRunReadsWithUndet = 0
                runMinReadsWithUndet = 0
                runMaxReadsWithUndet = 0
            #mean and SD for the runs GB array
            if allRunGbWithUndet != []:
                meanRunGbWithUndet = "%.2f" % (float(numpy.mean(allRunGbWithUndet))/1000000000.0)
                sdRunGbWithUndet = "%.2f" % (float(numpy.std(allRunGbWithUndet))/1000000000.0)
                runMinGbWithUndet = "%.2fGb" % (float(min(allRunGbWithUndet))/1000000000.0)
                runMaxGbWithUndet = "%.2fGb" % (float(min(allRunGbWithUndet))/1000000000.0)
            else:
                meanRunGbWithUndet = 0
                sdRunGbWithUndet = 0
                runMinGbWithUndet = 0
                runMaxGbWithUndet = 0
            #mean and sd for the lane reads array
            if allLaneReadsWithUndet != []:
                meanLaneReadsWithUndet = "%.2f" % (float(numpy.mean(allLaneReadsWithUndet))/1000000.0)
                sdLaneReadsWithUndet = "%.2f" % (float(numpy.std(allLaneReadsWithUndet))/1000000.0)
                laneMinReadsWithUndet ="%.2fM" % (float(min(allLaneReadsWithUndet))/1000000.0)
                laneMaxReadsWithUndet ="%.2fM" % (float( max(allLaneReadsWithUndet))/1000000.0)
            else:
                meanLaneReadsWithUndet = 0
                sdLaneReadsWithUndet = 0
                laneMinReadsWithUndet =0
                laneMaxReadsWithUndet =0
            #mean and sd for the lane GB array
            if allLaneGbWithUndet != []:
                meanLaneGbWithUndet = "%.2f" % (float(numpy.mean(allLaneGbWithUndet))/1000000000.0)
                sdLaneGbWithUndet = "%.2f" % (float(numpy.std(allLaneGbWithUndet))/1000000000.0)
                laneMinGbWithUndet ="%.2fGb" % (float(min(allLaneGbWithUndet))/1000000000.0)
                laneMaxGbWithUndet = "%.2fGb" % (float(max(allLaneGbWithUndet))/1000000000.0)
            else:
                meanLaneGbWithUndet = 0
                sdLaneGbWithUndet = 0
                laneMinGbWithUndet =0
                laneMaxGbWithUndet =0
   #        mean and SD for Q30 array.
            if allQ30 != []:
                meanQ30 = "%d" % numpy.mean(allQ30)
                sdQ30 = "%d" % numpy.std(allQ30)
                maxQ30 = max(allQ30)
                minQ30 = min(allQ30)
            else:
                meanQ30 = 0
                sdQ30 = 0
                maxQ30 = 0
                minQ30 = 0

            numberRuns = len(allRunReads)
            numberLanes = len(allLaneReads)

            expstr = {}
            expstr["DT_RowId"]=rowID
            expstr["0"] = "" #empty for the dropdown button
            expstr["1"] = machineType
            expstr["2"] = desiredName
            expstr["3"] = "%s &plusmn;%s" % ( meanRunReadsWithUndet, sdRunReadsWithUndet )
            expstr["4"] = "%s &plusmn;%s" % ( meanRunGbWithUndet, sdRunGbWithUndet )
            expstr["5"] = "%s &plusmn;%s" % ( meanLaneReadsWithUndet, sdLaneReadsWithUndet )
            expstr["6"] = "%s &plusmn;%s" % ( meanLaneGbWithUndet, sdLaneGbWithUndet )
            expstr["7"] = "%s" % ( numberRuns )
            expstr["8"] = "%s" % ( numberLanes )
            expstr["9"] = "%s &plusmn;%s" % ( meanQ30, sdQ30 )


            data["aaData"].append(expstr) 
    
    return HttpResponse(json.dumps(data), 'application/json')
#    runDict = {"numRuns":numberRuns, "MinGb":runMinGb, "MaxGb":runMaxGb, \
#               "MinReads":runMinReads, "MaxReads":runMaxReads, \
#               "MeanReads":meanRunReads,"SDReads":sdRunReads, \
#               "MeanGb":meanRunGb,"SDGb":sdRunGb, \
#               "MinReadsWithUndet":runMinReadsWithUndet, \
#               "MaxReadsWithUndet":runMaxReadsWithUndet, \
#               "MeanReadsWithUndet":meanRunReadsWithUndet,\
#               "SDReadsWithUndet":sdRunReadsWithUndet, \
#               "MeanGbWithUndet":meanRunGbWithUndet,"SDGbWithUndet":sdRunGbWithUndet}
#    laneDict = {"numLanes":numberLanes, "MinGb":laneMinGb, "MaxGb":laneMaxGb, \
#               "MinReads":laneMinReads, "MaxReads":laneMaxReads, \
#               "MeanReads":meanLaneReads,"SDReads":sdLaneReads, \
#               "MeanGb":meanLaneGb,"SDGb":sdLaneGb, \
#               "MinReadsWithUndet":laneMinReadsWithUndet, \
#               "MaxReadsWithUndet":laneMaxReadsWithUndet, \
#               "MeanReadsWithUndet":meanLaneReadsWithUndet, \
#               "SDReadsWithUndet":sdLaneReadsWithUndet, \
#               "MeanGb":meanLaneGb,"SDGb":sdLaneGb}
#    returnDict = {"Run":runDict, "Lane":laneDict, "Q30Mean":meanQ30, "Q30SD":sdQ30, \
#                    "Q30Max":maxQ30, "Q30Min":minQ30}

def statisticsSummaryAjax(request, runType):
    """Get the full suite of details for everything.
        
    Creates a table to display a summary of the statsistics for each run type.
    Ajax containing HTML for the dropdown of /gsuStats/stats

    """
    print runType 
    runTypeBreakdown = runType.split("_")
    machineType = runTypeBreakdown[0]
    shortStrat = runTypeBreakdown[1]
    lowerLength = int(runTypeBreakdown[2])
    upperLength = int(runTypeBreakdown[3])
    if shortStrat == "S":
        strategy = "single"
    elif shortStrat == "P":
        strategy = "paired"

    allRelevantRuns = Run.objects.filter(length__gt=lowerLength, length__lt=upperLength,\
                                        machineType=machineType,\
                                        pairedSingle=strategy)
    htmlTable, laneReads, densityStats, laneQ30, firstBaseVClusDensStats = \
                                                            gatherStatistics(allRelevantRuns)

    # build the json to return
    data = {}
    #fully generate the tabs
    if machineType != "MiSeq":
        data["firstBase"] = firstBaseVClusDensStats
        data["htmlTabs"] = buildStatisticsTabsHTMLwithFirstBaseReport(runType, htmlTable)
    else:
        data["htmlTabs"] = buildStatisticsTabsHTMLwithoutFirstBaseReport(runType, htmlTable)
    print data["htmlTabs"]
    data["laneReads"] = laneReads
    data["densityStats"] = densityStats
    data["laneQ30"] = laneQ30
    data["runID"]= runType
    #return of the string
    return HttpResponse(json.dumps(data), 'application/json')

def gatherStatistics(runData):
    """Generates and gathers the statsistics for the set of runs given.
    """
    allLaneReads = []
    allLaneReadsWithUndet = []
    allLaneReadsWithUndetFormatted = []
    allLaneGb = []
    allLaneGbWithUndet = []
    allRunReads = [] 
    allRunReadsWithUndet = [] 
    allRunGb = []
    allRunGbWithUndet = []
    allLaneUndet = []
    allRunUndet = []    
    allRunUndetProportion = []
    allLaneUndetProportion = []
    allQ30 = []
    maxUndetRun = ""
    densityStats = []
    laneQ30Stats = []
    firstBaseVClusDensStats = []
    #loop over them
    for run in runData:
        runReads = 0
        runReadsWithUndet = 0
        runGb = 0
        runGbWithUndet = 0
        runUndet = 0
        #get all the samples for the run
        samples = Sample.objects.filter(run_id=run.id)
        #get all the lanes for the run
        lanes = Lane.objects.filter(run_id=run.id)
        #loop over the lanes
        for lane in lanes:
            #pass over lanes that had issues. ignore
            laneQ30 = []
            laneReads = 0
            laneGb = 0
            #get lane undetermined read statistics
            if lane.totalUndetIndexes != None:
                laneReadsWithUndet = lane.totalUndetIndexes
                laneGbWithUndet = lane.totalUndetIndexes * run.length
                laneUndet = lane.totalUndetIndexes
            else:
                laneReadsWithUndet = 0
                laneGbWithUndet = 0
                laneUndet = 0
            #get the samples for the lane
            laneSamples = samples.filter(lane_id=lane.id)
            
            for sample in laneSamples:
                #number of reads for the lane DONT FORGET UNDET READS
                laneReads = laneReads + sample.reads
                laneReadsWithUndet = laneReadsWithUndet + sample.reads
                #number of GB for the lane DONT FORGET UNDET READS
                laneGb = laneGb + sample.reads*run.length
                laneGbWithUndet = laneGbWithUndet + sample.reads*run.length
                #Q30 array for the lane
                allQ30.append(sample.Q30Length)
            #    if sample.readNumber == 2:
                laneQ30.append(sample.Q30Length)
            #get clusterDensity stats
            if lane.clusterDensity != None:
                #this gathers the stats for the densityScatterGraph in barchart.js
                #create an empty array for the yvalue stddev for the density v reads plot
                emptyYStdDev = 0
                #density v read number
                #x is cluster density, y is number of reads for the lane
                #x std dev is the density stddev, y stddev is empty - has no variation
                densityStats.append( [lane.clusterDensity, laneReads, \
                                      lane.clusterDensityStdDev, emptyYStdDev, \
                                      "Run %s, Lane %s" %( run.runName, lane.lane )])
                #density v q30 length
                #x is cluster density, y is mean q30 over all samples in the lane
                #x stddev is density stddev, y stddev is the dev of the q30
                if laneQ30 == []:
                    laneQ30 = [0,0]
                laneQ30Stats.append( [lane.clusterDensity, numpy.mean(laneQ30), \
                                    lane.clusterDensityStdDev, numpy.std(laneQ30),  \
                                    "Run %s, Lane %s" %( run.runName, lane.lane )])
                # first base density v passing filter density
                #x is cluster pf density, y is firstBaseReport density, 
                #x stddev is density stddev, y stddev is empty
                firstBaseVClusDensStats.append( [lane.clusterDensity,\
                                                   lane.firstBaseDensity,\
                                            lane.clusterDensityStdDev, emptyYStdDev, \
                                            "Run %s, Lane %s" %( run.runName, lane.lane )])
                                
            #    print("clusterDensityStdDev %d" % lane.clusterDensityStdDev)
            #    print(densityStats[-1])
            #    print("laneQ30 - std dev %.2f" % numpy.std(laneQ30))
            #    print(laneQ30Stats[-1])
            #add reads to master array
            #if run.id not in [51,45,47]
            allLaneReads.append(laneReads)
            allLaneReadsWithUndet.append(laneReadsWithUndet)
            formattedReads = "%.2f" % (float(laneReadsWithUndet)/1000000.0)
            allLaneReadsWithUndetFormatted.append(formattedReads)
            #add GB to master array
            allLaneGb.append(laneGb)
            allLaneGbWithUndet.append(laneGbWithUndet)
            
            #number of reads for the lane DONT FORGET UNDET READS
            runReads = runReads + laneReads
            runReadsWithUndet = runReadsWithUndet + laneReadsWithUndet
            #number of GB for the lane DONT FORGET UNDET READS
            runGb = runGb + laneGb 
            runGbWithUndet = runGbWithUndet + laneGbWithUndet
            #undets
            runUndet = runUndet + laneUndet
            if laneUndet > 0:
                print laneUndet
                allLaneUndet.append(laneUndet)
                print allLaneUndet
                undetProportion = float(laneUndet)/float(laneReadsWithUndet)*100.0 
                print undetProportion
                allLaneUndetProportion.append( undetProportion )
                if undetProportion >= max(allLaneUndetProportion):
                    maxUndetRun = run.runName
        #if run.id not in [51,45,47]:
            allRunReads.append(runReads)
            allRunReadsWithUndet.append(runReadsWithUndet)
            allRunGb.append(runGb)
            allRunGbWithUndet.append(runGbWithUndet)
            allRunUndet.append(runUndet)
            if runReadsWithUndet != 0:
                allRunUndetProportion.append( float(runUndet)/float(runReadsWithUndet)*100.0 )
            else:
                allRunUndetProportion.append( 0.0 )
       
    #undet Min, max, proportion
    if allLaneUndetProportion != []:
        meanLaneUndetProportion = "%.2f%%" % (numpy.mean(allLaneUndetProportion))
        sdLaneUndetProportion = "%.2f" % (numpy.std(allLaneUndetProportion))
        meanRunUndetProportion = "%.2f%%" % (numpy.mean(allRunUndetProportion))
        sdRunUndetProportion = "%.2f" % (numpy.std(allRunUndetProportion))
    else:
        meanLaneUndetProportion = "0.00"
        sdLaneUndetProportion = "0.00"
        meanRunUndetProportion = "0.00"
        sdRunUndetProportion = "0.00"
        allLaneUndetProportion = [0,0]
            #take mean and SD for the runs read array
    if allRunReads != []:
        meanRunReads = "%.2fM" % (float(numpy.mean(allRunReads))/1000000.0)
        sdRunReads = "%.2fM" % (float(numpy.std(allRunReads))/1000000.0)
        runMinReads ="%.2fM" % (float(min(allRunReads))/1000000.0)
        runMaxReads ="%.2fM" % (float(min(allRunReads))/1000000.0)
    else:
        meanRunReads = 0
        sdRunReads = 0
        runMinReads =0
        runMaxReads =0
    #mean and SD for the runs GB array
    if allRunGb != []:
        meanRunGb = "%.2fGb" % (float(numpy.mean(allRunGb))/1000000000.0)
        sdRunGb = "%.2fGb" % (float(numpy.std(allRunGb))/1000000000.0)
        runMinGb ="%.2fGb" % (float(min(allRunGb))/1000000000.0)
        runMaxGb ="%.2fGb" % (float(min(allRunGb))/1000000000.0)
    else:
        meanRunGb = 0
        sdRunGb = 0
        runMinGb =0
        runMaxGb =0
    #mean and sd for the lane reads array
    if allLaneReads != []:
        meanLaneReads = "%.2fM" % (float(numpy.mean(allLaneReads))/1000000.0)
        sdLaneReads = "%.2fM" % (float(numpy.std(allLaneReads))/1000000.0)
        laneMinReads = "%.2fM" % (float(min(allLaneReads))/1000000.0)
        laneMaxReads ="%.2fM" % (float(max(allLaneReads))/1000000.0)
    else:
        meanLaneReads = 0
        sdLaneReads = 0
        laneMinReads = 0
        laneMaxReads =0
    #mean and sd for the lane GB array
    if allLaneGb != []:
        meanLaneGb = "%.2fGb" % (float(numpy.mean(allLaneGb))/1000000000.0)
        sdLaneGb = "%.2fGb" % (float(numpy.std(allLaneGb))/1000000000.0)
        laneMinGb ="%.2fGb" % (float(min(allLaneGb))/1000000000.0)
        laneMaxGb ="%.2fGb" % (float(max(allLaneGb))/1000000000.0)
    else:
        meanLaneGb = 0
        sdLaneGb = 0
        laneMinGb =0
        laneMaxGb =0
    #take mean and SD for the runs read array
    if allRunReadsWithUndet != []:
        meanRunReadsWithUndet = "%.2f" % (float(numpy.mean(allRunReadsWithUndet))/1000000.0)
        sdRunReadsWithUndet = "%.2f" % (float(numpy.std(allRunReadsWithUndet))/1000000.0)
        runMinReadsWithUndet = "%.2fM" % (float(min(allRunReadsWithUndet))/1000000.0)
        runMaxReadsWithUndet = "%.2fM" % (float(min(allRunReadsWithUndet))/1000000.0)
    else:
        meanRunReadsWithUndet = 0
        sdRunReadsWithUndet = 0
        runMinReadsWithUndet = 0
        runMaxReadsWithUndet = 0
    #mean and SD for the runs GB array
    if allRunGbWithUndet != []:
        meanRunGbWithUndet = "%.2f" % (float(numpy.mean(allRunGbWithUndet))/1000000000.0)
        sdRunGbWithUndet = "%.2f" % (float(numpy.std(allRunGbWithUndet))/1000000000.0)
        runMinGbWithUndet = "%.2fGb" % (float(min(allRunGbWithUndet))/1000000000.0)
        runMaxGbWithUndet = "%.2fGb" % (float(min(allRunGbWithUndet))/1000000000.0)
    else:
        meanRunGbWithUndet = 0
        sdRunGbWithUndet = 0
        runMinGbWithUndet = 0
        runMaxGbWithUndet = 0
    #mean and sd for the lane reads array
    if allLaneReadsWithUndet != []:
        meanLaneReadsWithUndet = "%.2f" % (float(numpy.mean(allLaneReadsWithUndet))/1000000.0)
        sdLaneReadsWithUndet = "%.2f" % (float(numpy.std(allLaneReadsWithUndet))/1000000.0)
        laneMinReadsWithUndet ="%.2fM" % (float(min(allLaneReadsWithUndet))/1000000.0)
        laneMaxReadsWithUndet ="%.2fM" % (float( max(allLaneReadsWithUndet))/1000000.0)
    else:
        meanLaneReadsWithUndet = 0
        sdLaneReadsWithUndet = 0
        laneMinReadsWithUndet =0
        laneMaxReadsWithUndet =0
    #mean and sd for the lane GB array
    if allLaneGbWithUndet != []:
        meanLaneGbWithUndet = "%.2f" % (float(numpy.mean(allLaneGbWithUndet))/1000000000.0)
        sdLaneGbWithUndet = "%.2f" % (float(numpy.std(allLaneGbWithUndet))/1000000000.0)
        laneMinGbWithUndet ="%.2fGb" % (float(min(allLaneGbWithUndet))/1000000000.0)
        laneMaxGbWithUndet = "%.2fGb" % (float(max(allLaneGbWithUndet))/1000000000.0)
    else:
        meanLaneGbWithUndet = 0
        sdLaneGbWithUndet = 0
        laneMinGbWithUndet =0
        laneMaxGbWithUndet =0
   #mean and SD for Q30 array.
    if allQ30 != []:
        meanQ30 = "%d" % numpy.mean(allQ30)
        sdQ30 = "%d" % numpy.std(allQ30)
        maxQ30 = max(allQ30)
        minQ30 = min(allQ30)
    else:
        meanQ30 = 0
        sdQ30 = 0
        maxQ30 = 0
        minQ30 = 0


    numberRuns = len(allRunReads)
    numberLanes = len(allLaneReads)

    leftTable_str = '<table class="psteptable"><th></th><th></th>'
    minMaxReadsRun = '<tr><td>Min/Max Reads per run</td><td>%s/%s</td></tr>' \
                        %( runMinReadsWithUndet, runMaxReadsWithUndet )
    minMaxGbRun = '<tr><td>Min/Max Gb per run</td><td>%s/%s</td></tr>' \
                        %( runMinGbWithUndet, runMaxGbWithUndet )
    minMaxReadsLane = '<tr><td>Min/Max Reads per lane</td><td>%s/%s</td></tr>' \
                        %( laneMinReadsWithUndet, laneMaxReadsWithUndet )
    minMaxGbLane = '<tr><td>Min/Max Gb per lane</td><td>%s/%s</td></tr>' \
                        %( laneMinGbWithUndet, laneMaxGbWithUndet )
    minMaxUndetLane = '<tr><td>Max Undetermined</br>Proportion per Lane</td><td>%.2f%% (Run %s)</td></tr>'\
                        %( max(allLaneUndetProportion), maxUndetRun )
#    proportionUndetReadsRun = '<tr><td>Proportion Undet Reads/run (SD)</td><td>%s (%s)</td></tr>'\
#                                %( meanRunUndetProportion, sdRunUndetProportion )
#    proportionUndetGbRun
    proportionUndetReadsLane = '<tr><td>Mean Proportion</br>Undet Lane/run (SD)</td><td>%s (%s)</td></tr>'\
                                %( meanLaneUndetProportion, sdLaneUndetProportion )
#    proportionUnderGbRun
#    meanUndetReadsRun = '
#    meanUndetGbRun
#    meanUndetReadsLane
#    meanUndetGbLane
    tableString = leftTable_str + minMaxReadsRun + minMaxGbRun + minMaxReadsLane + \
                    minMaxGbLane + proportionUndetReadsLane + minMaxUndetLane +\
                    "</table>"
   
    return (tableString, allLaneReadsWithUndetFormatted, densityStats, laneQ30Stats, \
                                                                    firstBaseVClusDensStats)

def buildStatisticsTabsHTMLwithoutFirstBaseReport(runType, htmlTable):
    """Builds the tabs for the drop-down information in the run-overview tables.

    Input is the ouput from buildStatisticsDetails.
    HTML for the drop down in /gsuStats/stats
    
    """
    #generate our return string
    returnStr = '''
    <div id="subtabs" class="subtabs">
        <ul id="datasettabs">
            <li id="dataset%stab">
                <a href="#summary%stab-div">Summary Information</a>
            </li>
            <li id="laneReadsDist%stab">
                <a href="#laneReadsDist%stab-div">Reads/Lane Dist</a>
            </li>
            <li id="densityDiv%stab">
                <a href="#densityDiv%stab-div">Cluster Density/Reads</a>
            </li>
            <li id="laneQ30%stab">
                <a href="#laneQ30%stab-div">Density v Q30/Reads</a>
            </li>''' % (runType, runType, runType, runType, runType, runType, runType, runType)
#    for lane, content in laneDetailsDict.iteritems():
#        laneDiv = '<li id="run%slane%stab"><a href="#run%slane%stab-div">Lane %s</a></li>' \
#                    %( run_id, lane, run_id,lane, lane )
#        returnStr = returnStr + laneDiv
    returnStr = returnStr + '</ul>' 
    returnStr = returnStr + '''<div id="summary%stab-div" class="subtab">%s</div>
                                <div id="laneReadsDist%stab-div" class="subtab"></div>
                                <div id="densityDiv%stab-div" class="subtab"></div>
                                <div id="laneQ30%stab-div" class="subtab"></div>
                                </div>'''\
                     % (runType, htmlTable, runType, runType, runType) 
    
#    for lane, content in laneDetailsDict.iteritems():
#        laneTabContent = '<div id="r%sl%splot" class="laneplot"></div>' \
#                         '<div class="lanetable">%s</div>' \
#                      '' % (run_id, lane, content )
#   
#        laneStr = '<div id="run%slane%stab-div" class="subtab">%s</div>' \
#                                %(run_id,lane, laneTabContent)
#        returnStr = returnStr + laneStr
    #returnStr = returnStr + '</div>'
    #return it
 
    return(re.sub("\n", "", re.sub("\t", "", returnStr)))



def buildStatisticsTabsHTMLwithFirstBaseReport(runType, htmlTable):
    """Builds the tabs for the drop-down information in the run-overview tables.

    Input is the ouput from buildStatisticsDetails.
    HTML for the drop down in /gsuStats/stats
    
    """
    #generate our return string
    returnStr = '''
    <div id="subtabs" class="subtabs">
        <ul id="datasettabs">
            <li id="dataset%stab">
                <a href="#summary%stab-div">Summary Information</a>
            </li>
            <li id="laneReadsDist%stab">
                <a href="#laneReadsDist%stab-div">Reads/Lane Dist</a>
            </li>
            <li id="densityDiv%stab">
                <a href="#densityDiv%stab-div">Cluster Density/Reads</a>
            </li>
            <li id="laneQ30%stab">
                <a href="#laneQ30%stab-div">Density v Q30/Reads</a>
            </li>
            <li id="firstBase%stab">
                <a href="#firstBase%stab-div">First base density v actual density</a>
            </li>''' % (runType, runType, runType, runType, runType, runType, runType, runType,\
                        runType,runType)
#    for lane, content in laneDetailsDict.iteritems():
#        laneDiv = '<li id="run%slane%stab"><a href="#run%slane%stab-div">Lane %s</a></li>' \
#                    %( run_id, lane, run_id,lane, lane )
#        returnStr = returnStr + laneDiv
    returnStr = returnStr + '</ul>' 
    returnStr = returnStr + '''<div id="summary%stab-div" class="subtab">%s</div>
                                <div id="laneReadsDist%stab-div" class="subtab"></div>
                                <div id="densityDiv%stab-div" class="subtab"></div>
                                <div id="laneQ30%stab-div" class="subtab"></div>
                                <div id="firstBase%stab-div" class="subtab"></div>
                                </div>'''\
                     % (runType, htmlTable, runType, runType, runType, runType) 
    
#    for lane, content in laneDetailsDict.iteritems():
#        laneTabContent = '<div id="r%sl%splot" class="laneplot"></div>' \
#                         '<div class="lanetable">%s</div>' \
#                      '' % (run_id, lane, content )
#   
#        laneStr = '<div id="run%slane%stab-div" class="subtab">%s</div>' \
#                                %(run_id,lane, laneTabContent)
#        returnStr = returnStr + laneStr
    #returnStr = returnStr + '</div>'
    #return it
 
    return(re.sub("\n", "", re.sub("\t", "", returnStr)))

