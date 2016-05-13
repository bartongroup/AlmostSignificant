from django.db import models

# Create your models here.
class Run(models.Model):
    """Run data model for the GSU statistics viewer.

    Contains the description of the run.

    """
    runName = models.CharField(max_length=50, verbose_name="RunName")
    #runID = models.CharField(max_length=255)
    machine = models.CharField(max_length=20)
    machineType = models.CharField(max_length=10)
    date = models.DateField()
    alias = models.TextField(blank=True)
    length = models.PositiveSmallIntegerField()
    fcPosition = models.CharField(max_length=1)
    notes = models.TextField(blank=True)

    pairedSingle = models.TextField(max_length=6)
    def __unicode__(self):
        return self.runName
    
class Sample(models.Model):
    """Sample Model for the GSU statistics viewer.

    Description of the sample and the results of its QC analysis
    
    """
    run = models.ForeignKey('Run')
    project = models.ForeignKey('Project')
    software = models.ManyToManyField('Software')
    lane = models.ForeignKey('Lane')
    sampleReference = models.CharField(max_length=255)
    sampleName = models.CharField(max_length=255,blank=True)
    readNumber = models.PositiveSmallIntegerField()
    reads = models.PositiveIntegerField()
    sequenceLength = models.TextField()
    sampleDescription = models.TextField(blank=True)
    libraryReference = models.CharField(max_length=255)
    barcode = models.CharField(max_length=17)
    species = models.CharField(max_length=255,blank=True)
    
    method = models.CharField(max_length=100)
    fastQLocation = models.TextField()
    md5hash = models.CharField(max_length=255,blank=True)
    QCStatus = models.CharField(max_length=10,blank=True)
    insertLength = models.PositiveIntegerField(null=True)
    contaminantsImage = models.TextField()
    fastQCSummary = models.TextField()
    filteredSequences = models.PositiveIntegerField(default=0,null=True)
    Q30Length = models.PositiveSmallIntegerField(null=True)
    percentGC = models.PositiveSmallIntegerField(null=True)

    sequenceQuality = models.CharField(max_length=4,blank=True)
    sequenceQualityScores = models.CharField(max_length=4,blank=True)
    sequenceContent = models.CharField(max_length=4,blank=True)
    GCContent = models.CharField(max_length=4,blank=True)
    baseNContent = models.CharField(max_length=4,blank=True)
    sequenceLengthDistribution = models.CharField(max_length=4,blank=True)
    sequenceDuplicationLevels = models.CharField(max_length=4,blank=True)
    overrepresentedSequences = models.CharField(max_length=4,blank=True)
    kmerContent = models.CharField(max_length=4,blank=True)
#    adapterContent = models.CharField(max_length=4,blank=True)
#    tileSequenceQuality = models.CharField(max_length=4,blank=True)
    
    trimmed = models.BooleanField(default=False,blank=True)

    def __unicode__(self):  # Python 3: def __str__(self):
           return self.sampleReference


class Project(models.Model):
    """Basic details of a project."""
    project = models.CharField(max_length=255)
    projectMISOID = models.PositiveSmallIntegerField(null=True)
    projectPROID = models.CharField(max_length=20,null=True)
    owner = models.CharField(max_length=255,blank=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.project
    

class Lane(models.Model):
    """ Models the lane. Keeps lane specific details such as cluster density"""
    run = models.ForeignKey('Run')
    lane = models.PositiveSmallIntegerField()
    ClusterPFDensity = models.PositiveIntegerField(null=True)
    clusterDensity = models.PositiveIntegerField(null=True)
    clusterPFDensityStdDev = models.PositiveIntegerField(null=True)
    clusterDensityStdDev = models.PositiveIntegerField(null=True)
    numClusters = models.PositiveIntegerField(null=True)
    numClustersStdDev = models.PositiveIntegerField(null=True)
    numClustersPF = models.PositiveIntegerField(null=True)
    numClustersPFStdDev = models.PositiveIntegerField(null=True)
    firstBaseDensity = models.PositiveIntegerField(null=True)
    percPassingFilter = models.FloatField(null=True)
    readsPassingFilter = models.PositiveIntegerField(null=True)
    percentOverQ30 = models.DecimalField(max_digits=5, decimal_places=3, null=True)
    totalUndetIndexes = models.BigIntegerField(null=True)

    def __unicode__(self):
        return str(self.lane)

class UndeterminedIndex(models.Model):
    """Stores the undetermined indices for Each lane."""
    lane = models.ForeignKey('Lane')
    index = models.CharField(max_length=17,default=0)
    occurances = models.PositiveIntegerField(blank=True)

class Software(models.Model):
    """Basic summary of the casava version and the parameters it was run with."""
    softwareName = models.TextField()
    version = models.TextField()
    parameters = models.TextField(blank=True)

class ContaminantsDetails(models.Model):
    """Basic summary of the contaminants breakdown."""
    sample = models.ForeignKey('Sample')
    organism = models.TextField()
    hitsNoLibraries = models.FloatField(null=True)
    percUnmapped = models.FloatField(null=True)
    oneHitOneLib = models.FloatField(null=True)
    manyHitOneLib = models.FloatField(null=True)
    oneHitManyLib = models.FloatField(null=True)
    manyHitManyLib = models.FloatField(null=True)


