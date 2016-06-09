#! /bin/bash
#Script to package up all of the files needed to install almostSignificant.
rm AlmostSignificant.tar.gz

asVersion=$(grep version='[0-9]*' setup.py | grep -o [0-9]\.[0-9]*)
declare -a filesToAdd=("$(pwd)/dist/django-almostSignificant-$asVersion.tar.gz" "$(pwd)/ACKNOWLEDGEMENTS" "$(pwd)/get-pip.py" "$(pwd)/installAlmostSignificant.sh" "$(pwd)/INSTALL.md" "$(pwd)/LICENSE" "$(pwd)/MANIFEST.in" "$(pwd)/README.md" "$(pwd)/almostSignificant/dataLoading/dataLoading.py" "$(pwd)/almostSignificant/dataLoading/pdfGenerator.sh")
mkdir AlmostSignificant-$asVersion

for currentFile in ${filesToAdd[@]}; do
	ln  $currentFile AlmostSignificant-$asVersion
done

tar -cf AlmostSignificant.tar AlmostSignificant-$asVersion

rm -r AlmostSignificant-$asVersion

gzip AlmostSignificant.tar
