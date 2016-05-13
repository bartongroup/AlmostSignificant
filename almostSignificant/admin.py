from django.contrib import admin
from almostSignificant.models import Sample, Project, Run

class sampleAdmin(admin.ModelAdmin):
    fields = ("QCStatus","overrepresentedSequences","sampleReference",\
            "sampleName", "readNumber","libraryReference","trimmed" )
    list_display = ("sampleReference","sampleName","readNumber","run","lane","project",\
                    "libraryReference","reads","overrepresentedSequences","QCStatus")
    search_fields = ("sampleReference","sampleName","libraryReference")

class runAdmin(admin.ModelAdmin):
    fields = ("runName","date","length","notes")
    list_display = ("runName","date","length")
    search_fields = ("date","runName")

class projectAdmin(admin.ModelAdmin):
    fields = ("project","projectPROID","notes")
    list_display = ("project","projectPROID")
    list_display = ("project","projectPROID")

admin.site.register(Sample, sampleAdmin)
admin.site.register(Run, runAdmin)
admin.site.register(Project, projectAdmin)
