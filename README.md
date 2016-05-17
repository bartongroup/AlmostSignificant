
AlmostSignificant
=====

AlmostSignificant is a platform to simplifying the quality control checks of Illumina HiSeq and
NextSeq sequencing runs. More detailed information is available in the docs folder.

Requires python 2.7, the illuminate package (available via pip install illuminate), and django >1.8 and pdflatex. 

Start
-----------
1.  After obtaining the gz file for almostSignificant, install it either globally, or into a folder that is readable by apache::
        pip install --user django-almostSignficant*.gz #local install
        pip install django-almostSignificant*.gz #global install. Likely requires root
    (NOTE: At writing, installing the illuminate dependency appears to produce a lot of errors, but install completes sucessfully. I'm unsure why this is.)

    Check pdflatex is installed. If it isn't, obtain it via the usual methods for your distro (available in the texlive package)::
        pdflatex --version
    NOTE: If you find that the pdf summaries are not produced, it's likely pdflatex isn't installed and on your path.

2.  Setup a new Django project::
        django-admin startproject ASTest
    This creates a folder in your current location called ASTest. Where you see /path/to/ASTest is seen you need to replace this with the path to the project that was just created.

    Make sure that this new location is in your pythonpath::
        export PYTHONPATH=/path/to/ASTest/:$PYTHONPATH
    You can make this permanent by adding this line to your ~/.bashrc file, so that it is set whenever you launch your terminal.

3.  Add "almostSignficant" to the 'installed_apps' section of settings.py in the new project. 
    Settings.py is located in /path/to/ASTest/ASTest/::
        INSTALLED_APPS = (
            ...
            'almostSignificant',
        )
    
    Add locations to handle media and static files. This location must be writable by apache::
        STATIC_ROOT = '/path/to/ASTest/ASTest/static/'
        MEDIA_ROOT = '/path/to/ASTest/ASTest/media/'

    Ensure::
        'django.core.context_processors.request',
    and::
        'django.core.context_processors.static',
    are in the 'context_processors' subsection of the TEMPLATES section, e.g.::
        TEMPLATES = [
            {
            ...
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.template.context_processors.static',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
            ...

4.  Add the following line to urls.py.
    urls.py is located in /path/to/ASTest/ASTest/::
        from almostSignificant import urls as as_urls
    and the following to urlpatterns in urls.py::
        url(r'^almostSignificant/', include(as_urls)),
    e.g.::
        urlpatterns = [
            url(r'^admin/', include(admin.site.urls)),
            url(r'^almostSignificant/', include(as_urls)),
        ]
    Add 'include' to the imported functions from django.conf.urls::
        from django.conf.urls import url, include
          
    Note: If later you have problems with CSS files not loading, add these to the end of urls.py::
        from django.contrib.staticfiles.urls import staticfiles_urlpatterns
        urlpatterns += staticfiles_urlpatterns()

    

5.  Start the project. From the project folder created in (2)::
        python manage.py migrate
        python manage.py makemigrations almostSignificant
        python manage.py migrate almostSignificant
    and collect the static files we need::
        python manage.py collectstatic
    You will be asked if you want to delete the current static files. Select 'yes'

6a. BASIC:Launch the server using the built in service provided by django::
        python /path/to/ASTest/manage.py runserver
    This command should indicate the address to go to using a browser to view almostSignificant; the default is 127.0.0.1:8000.

6b. ADVANCED:Setup the apache server on your target machine. Advice on this is beyond the scope of this readme, but below is an example of the config I use for apache2 when testing almostSignificant. 
    001-almostSignficant.conf::
        
    <VirtualHost *:8080>
    
    	ServerAdmin webmaster@localhost
    	DocumentRoot /home/User/djangoProjects/astest/astest
    
    	ErrorLog ${APACHE_LOG_DIR}/error.log
    	CustomLog ${APACHE_LOG_DIR}/access.log combined
    
    	Alias /static/ /home/User/Public/astest/astest/static/
    	Alias /media/ /home/User/Public/astest/astest/media/
    
    	<Directory /home/User/Public/astest/astest/static>
    		Options Indexes FollowSymLinks
    		AllowOverride None
    		Require all granted
    	</Directory>
    	<Location "/static/">
    		Options -Indexes
    	</Location>
    
    	<Directory /home/User/Public/astest/astest/media>
    		Require all granted
    	</Directory>
    
    	<Directory /home/User/Public/astest/astest>
    		<Files wsgi.py>
    			Require all granted
    		</Files>
    	</Directory>
    
    	WSGIDaemonProcess almostSignificant python-path=/home/User/Public/astest:/home/User/Public/astest/astest:/home/User/.local/lib/python2.7/site-packages:/usr/lib/python2.7
    	WSGIProcessGroup almostSignificant
    	WSGIScriptAlias / /home/User/Public/astest/astest/wsgi.py
    	
    	
    </VirtualHost>



DataLoading
----------

The dataloading script is supplied with the almostSignificant install, or can be downloaded from the github page. It is worth copying the dataLoading script and pdfGenerator.sh scripts into somewhere on your python path and path, respectively. The default location for a sudo install on ubuntu is::
    /usr/local/lib/python2.7/dist-packages/almostSignificant/dataLoading/

You'll also need the pocation of the django project in your python path, eg::
    export PYTHONPATH=/home/User/Public/ASTest/ASTest/:/usr/local/lib/python2.7/dist-packages/almostSignificant/dataLoading/:$PYTHONPATH

Usage::
    python dataLoading.py <runLocation> <rawLocation> <qcFolder> 
   
    where runLocation is the folder produced by bcl2fastq or bcl2fastq2
    rawLocation is the folder produced by the sequencing machine, and contains the sample sheet for the run, named SampleSheet.csv
    qcFolder is a folder containing all of the fastQC and/or fastQScreen output for all of the fastq files that are in the runLocation. 
    Tip: If you don't normally keep all of the QC output in a single folder (subfolders within this folder are permitted), try hard or soft linking the files into a single folder.

    Optional arguements:
        -m, --machineType takes either hiseq or nextseq. By default assumes runs are nextseq runs.
        -c, --checkUndets signifies that the script is to check what indexes are in the undetermined index files. By default it doesn't do this as it can take some time, depending on the total number of undetermined indexes. 

    example::
        python dataloading.py /data/nextseq/processed/160127_NS500001_0001_ARUNIDENT/ /data/nextseq/raw/160127_NS500001_0001_ARUNIDENT/ /data/nextseq/processed/160127_NS500001_0001_ARUNIDENT/QC_Data -c
    This would load in the data for a nextseq run and gather information on the undetermined indexes.

