#! /bin/bash
#AlmostSignificant Install script

#check the the first arg is the install folder and is actually a folder

scriptDir=""
installFolder=$1
installLog=installLog.txt
set -o pipefail

getScriptDir () {
	#gets the directory ths script is run in. Must be run as a function otherwise
	#BASH_SOURCE isn't set?
	scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
}

getScriptDir

function printHelp {
	
	printf '\nThis script performs the install stages for deploying almostSignificant on the local machine.\n'
	printf 'AlmostSignificant is a data-aggregation framework for next-generation seuqencing data, and its associated quality control metrics.\n\n'
	printf 'The first, and only, arguement for this script is the folder that almostSignificant is to be installed in.\n\n'
	printf 'Stages of this script are:\nSetup a virtualenv folder.\nInstall almostSignificant into the virtualenv.\n'
	printf 'Setup django.\nConfigure Django.\nInstall the data loading scripts.\n\n'
	printf 'It is required to have python-dev, python-virtualenv, and some form of pdflatex (eg texlive package) installed.\n'
	printf 'It is recommended to have python-numpy and python-pandas installed prior to running this script; there have been install issues when this is not the case.\n\n'
	printf 'For more help, please contact jxward@dundee.ac.uk\n\n'
	exit 1
}

if [[ ! -d $installFolder ]]; then
	mkdir $installFolder
	if [[ $? -ne 0 ]]; then
		printf '\n Cannot create install folder $installFolder\n' 
		printHelp
	fi
fi
#elif [[ ! -w $installFolder ]]; then
#	echo "Cannot write to $installFolder" 
#	printHelp
cd $installFolder
touch $installLog	
#set virtualenv folder 
which virtualenv | tee $installLog #dependency
if [[ $? -ne 0 ]]; then
	echo "Virtualenv not found. Please install virtualenv. (e.g. sudo apt-get install python-virtualenv )."
	exit 1
fi

virtualenv --system-site-packages almostSignificant  | tee -a $installLog
cd almostSignificant
currentDir=$(pwd)

source bin/activate

#load almost significant into the lib folder of this
./bin/pip install $scriptDir/django-almostSignificant*.tar.gz | tee -a $installLog

if [[ $? -ne 0 ]]; then #dependency
	#virtualenv bug, trying the hard way. 
	printf "\nFailed to install almostSignificant using pip. Trying to work around the virtualenv bug...\n\n" | tee -a $installLog
	#wget https://bootstrap.pypa.io/get-pip.py | tee -a $installLog
	python $scriptDir/get-pip.py | tee -a $installLog
	./bin/pip install $scriptDir/django-almostSignificant*.tar.gz | tee -a $installLog

	if [[ $? -ne 0 ]]; then
		echo "Failed to install almostSignificant in the virtual environment. Please see the error message produced by pip. Is python-dev installed?"
		exit 1
	fi
fi

#initiate django instance 
django-admin startproject ASServer | tee -a $installLog
#change files as per install instructions.

#THIS
#settings
	#installed apps
	sed -i "/INSTALLED_APPS = \[/a \ \ \ \ 'almostSignificant'," ASServer/ASServer/settings.py
	#static root
	mkdir $currentDir/ASServer/ASServer/static/
	echo "STATIC_ROOT = '$currentDir/ASServer/ASServer/static/'" >> ASServer/ASServer/settings.py
	#media root
	mkdir $currentDir/ASServer/ASServer/media/
	echo "MEDIA_ROOT = '$currentDir/ASServer/ASServer/media/'" >> ASServer/ASServer/settings.py
	#media url
	echo "MEDIA_URL = '/media/'" >> ASServer/ASServer/settings.py
	#templates
	sed -i "/'context_processors': \[/a \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ 'django.core.context_processors.static'," ASServer/ASServer/settings.py
	
#urls
	#imports
	sed -i "/from django.contrib import admin/a from almostSignificant import urls as as_urls" ASServer/ASServer/urls.py
	sed -i "/from django.contrib import admin/a from django.conf.urls import include" ASServer/ASServer/urls.py
	sed -i "/from django.contrib import admin/a from django.conf.urls.static import static" ASServer/ASServer/urls.py
	sed -i "/from django.contrib import admin/a from django.contrib.staticfiles.urls import staticfiles_urlpatterns" ASServer/ASServer/urls.py
	sed -i "/from django.contrib import admin/a from django.conf import settings" ASServer/ASServer/urls.py
	sed -i "/from django.contrib import admin/a from django.views.generic.base import RedirectView" ASServer/ASServer/urls.py
	#urls lines
	sed -i "/urlpatterns = \[/a \ \ \ \ url(r'^$', RedirectView.as_view(url='/almostSignificant/', permanent=False), name='index')," ASServer/ASServer/urls.py
	sed -i "/urlpatterns = \[/a \ \ \ \ url(r'^almostSignificant/', include(as_urls))," ASServer/ASServer/urls.py
	#static patterns
	echo "urlpatterns += staticfiles_urlpatterns()" >> ASServer/ASServer/urls.py
	echo "urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)" >> ASServer/ASServer/urls.py

#migrations
#python ASServer/manage.py migrate #might need to do this first, or syncdb?
printf "Setting up Django server.\n\n"
python ASServer/manage.py makemigrations almostSignificant >> $installLog
python ASServer/manage.py migrate >> $installLog
#collectstatic
python ASServer/manage.py collectstatic --noinput >> $installLog 


#install dataloading
cp -v $scriptDir/dataLoading.py ./bin/ >> $installLog
if [[ $? -ne 0 ]]; then
	echo "Failed to move dataLoading.py from $scriptDir to $(pwd)/bin" | tee -a $installLog
	exit 1
fi
#fix a pythonpath issue
sed -i "/import argparse/a sys.path.append('$(pwd)/ASServer/')" bin/dataLoading.py
sed -i "/import argparse/a sys.path.append('$(pwd)/ASServer/ASServer/')" bin/dataLoading.py
#install pdfgenerator
cp -v $scriptDir/pdfGenerator.sh ./bin/ >> $installLog
if [[ $? -ne 0 ]]; then
	echo "Failed to move pdfGenerator.sh from $scriptDir to $(pwd)/bin" | tee -a $installLog
	exit 1
fi

#check for 
	#pdflatex and modules needed?
	#checkfiles

#boot into djangoServer	
	#check for anything running on port 8000?
#create file for launching the server just using sh runAlmostSignificant.sh
touch ./bin/runAlmostSignificant.sh
printf "#! /bin/bash\nsource $(pwd)/bin/activate\npython $(pwd)/ASServer/manage.py runserver" > ./bin/runAlmostSignificant.sh
echo ""
echo "Finished loading almostSignificant. Run using 'bash $(pwd)/bin/runAlmostSignificant.sh'." | tee -a $installLog

