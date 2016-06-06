#AlmostSignificant Install script

#check the the first arg is the install folder and is actually a folder

installFolder=$1
scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function printHelp {
	
	printf '\nThis script performs the install stages for deploying almostSignificant on the local machine.\n'
	printf 'AlmostSignificant is a data-aggregation framework for next-generation seuqencing data, and its associated quality control metrics.\n\n'
	printf 'The first, and only, arguement for this script is the folder that almostSignificant is to be installed in.\n\n'
	printf 'Stages of this script are:\nSetup a virtualenv folder.\nInstall almostSignificant into the virtualenv.\n'
	printf 'Setup django.\nConfigure Django.\nInstall the data loading scripts.\n\n'
	printf 'For more help, please contact jxward@dundee.ac.uk'
	exit 1
}

if [[ ! -d $installFolder ]] || [[ ! -w $installFolder ]]; then
	printHelp
fi

cd $installFolder

#set virtualenv folder 
which virtualenv > /dev/null #dependency
if [[ $? -ne 0 ]]; then
	echo "Virtualenv not found. Please install virtualenv. (e.g. sudo apt-get install virtualenv )."
	exit 1
fi

virtualenv almostSignificant 
cd almostSignificant

source bin/activate

#load almost significant into the lib folder of this
./bin/pip install $scriptDir/almostSignificant.tar.gz

if [[ $? -ne 0 ]]; then #dependency
	echo "Failed to install almostSignificant in the virtual environment. Please see the error message produced by pip. Is python-dev installed?"
	exit 1
fi

#initiate django instance 
django-admin startproject ASServer
#change files as per install instructions.

#THIS
#settings
	#installed apps
	sed -i '/INSTALLED_APPS= (/a \ \ \ \ "almostSignificant",' ASServer/ASServer/settings.py
	#static root
	mkdir $pwd/ASServer/ASServer/static/
	echo "STATIC_ROOT = '$pwd/ASServer/ASServer/static/'" >> ASServer/ASServer/settings.py
	#media root
	mkdir $pwd/ASServer/ASServer/media/
	echo "MEDIA_ROOT = '$pwd/ASServer/ASServer/media/'" >> ASServer/ASServer/settings.py
	#media url
	echo "MEDIA_URL = '/media/'" >> ASServer/ASServer/settings.py
	#templates
	sed -i "/'context_processors': [/a \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ 'django.core.context_processors.static',/" ASServer/ASServer/settings.py
	
#urls
	#imports
	sed -i "/from django.contrib import admin/a from almostSignificant import urls as as_urls" ASServer/ASServer/urls.py
	sed -i "/from django.contrib import admin/a from django.conf.urls import include" ASServer/ASServer/urls.py
	#urls lines
	sed -i "/urlpatterns = [/a \ \ \ \ url(r'^almostSignificant/', include(as_urls))," ASServer/ASServer/urls.py
	#static patterns
	echo "urlpatterns += staticfiles_urlpatterns()" >> ASServer/ASServer/urls.py
	echo "urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOL)" >> ASServer/ASServer/urls.py

#migrations
#python ASServer/manage.py migrate #might need to do this first, or syncdb?
python ASServer/manage.py makemigrations almostSignificant
python ASServer/manage.py migrate
#collectstatic
python ASServer/manage.py collectstatic --noinput


#install dataloading
cp $scriptDir/dataLoading.py ./bin/
if [[ $? -ne 0 ]]; then
	echo "Failed to move dataLoading.py from $scriptDir to $pwd/bin"
	exit 1
fi
#install pdfgenerator
cp $scriptDir/pdfGenerator.sh ./bin/
if [[ $? -ne 0 ]]; then
	echo "Failed to move pdfGenerator.sh from $scriptDir to $pwd/bin"
	exit 1
fi

#check for 
	#pdflatex and modules needed?
	#checkfiles

#boot into djangoServer	
	#check for anything running on port 8000?
#create file for launching the server just using sh runAlmostSignificant.sh
touch ./bin/runAlmostSignificant.sh
echo "python $pwd/almostSignificant/manage.py runserver" > ./bin/runAlmostSignificant.sh
