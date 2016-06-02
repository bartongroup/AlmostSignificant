#! /bin/bash
#needs: fastqc folder/zip?, runName, Q30 length, 
################################################################################
################## LaTeX Function  ##################################
################################################################################
#Writes the latex file containing the fastQC images
#first arguement is the path of the _fastqc folder
#the second arguement is the runFolder ID. This is just for record Keeping
#third arguement is the Q30 length
function generateLatexFiles {
    #check we have pdflatex
    if hash pdflatex 2>/dev/null; then
	    #get the output folders, latex file name and paths for images.
        tempPath=$TMPDIR/genPDF/
	    fastqcInput=$1
        #if we're given a zip, extract it.
        #else if we have a folder, use its contents
        #otherwise exit
        if [[ ${fastqcInput: -4} == ".zip" ]]; then
	        sampleName=`basename $fastqcInput _fastqc.zip`
	        sampleFolder=`basename $fastqcInput .zip`
	        echo 'sampleName=basename $fastqcFolderPath _fastqc.zip'
            fastqcFolderPath=$TMPDIR/genPDF/$sampleFolder/
            imagePath=$TMPDIR/genPDF/$sampleFolder/Images/
            unzip -o $fastqcInput -d $tempPath
            if [ $? -ne 0 ]; then echo "Cannot unzip $fastqcFolderPath/($sampleName)_fastqc.zip";exit 1; fi
        elif [[ -d $fastqcInput ]]; then
            fastqcFolderPath=$fastqcInput
	        sampleName=`basename $fastqcFolderPath _fastqc`
	        imagePath=$fastqcFolderPath/Images/
        else 
            echo "Can't find fastqc images folder or .zip file"
            exit 1
            #errors!
        fi

	    latexOutFolder=$2
	    runFolderName=$3
	    #gets the q30 length for the sample
	    Q30Length=$4

	    latexFile=$latexOutFolder/$sampleName.tex
	    latexPrefix=$latexOutFolder/$sampleName #this is for passing to generate the 
	    parsedPath=`echo $fastqcFolderPath | sed -e s/_/\\\\\\\\_/g` # swaps underscores for escaped underscores. Yes, that many /
	    parsedRunFolderName=`echo $runFolderName | sed -e s/_/\\\\\\\\_/g` #again escapes underscores
	    parsedSampleName=`echo $sampleName | sed -e s/_/\\\\\\\\_/g` #again escapes underscores
	    #array containing all the image files to be used
	    declare -a imageFiles=('per_base_gc_content.png' \
	    					'kmer_profiles.png' \
	    					'duplication_levels.png' \
	    					'per_base_n_content.png' \
	    					'per_base_quality.png' \
	    					'per_base_sequence_content.png' \
	    					'per_sequence_gc_content.png' \
	    					'per_sequence_quality.png' \
	    					'sequence_length_distribution.png'\
                            'adapter_content.png' )

        #handle newer fastqc versions
        #if the images folder exists, use it
        #else if the zip files does, use that, 
        #otherwise error
	    # checks the files can be created
	    if ! touch $latexFile
	    	then echo "Writing latex file failed"
	    	exit 1
	    fi
	    if [ ! -e $latexFile ];
	    	then echo "but the file doesn't exist"
	    	exit 1
	    fi

	    #normal latex premable
        #packages used: graphicx, subfigure, color, helvet, geometry
	    echo '\documentclass[11pt,a4paper]{article}' > $latexFile
	    echo '\usepackage{graphicx, subfigure}' >>$latexFile
	    echo '\usepackage{color}' >>$latexFile
	    echo '\usepackage{helvet}' >>$latexFile
	    echo '\renewcommand\familydefault{\sfdefault}' >> $latexFile
	    echo '\usepackage[landscape,top=1cm,bottom=1cm,left=2cm,right=2cm]{geometry}' >>$latexFile
	    echo "\graphicspath{ {$imagePath} }" >>$latexFile
	    echo '\begin{document}' >> $latexFile

	    echo '\begin{figure}[ht]' >> $latexFile
	    echo "\caption{ $parsedSampleName,  $parsedRunFolderName }" >> $latexFile
	    echo '\begin{center}' >> $latexFile

	    #loop through all the image files
	    for image in "${imageFiles[@]}";
	    	do
	    	if [ -e $imagePath/$image ]; then
	    		echo '\subfigure{' >> $latexFile
	    		echo "\includegraphics[width=0.3\textwidth]{$image} }" >> $latexFile
	    	fi
	    done

	    echo '\end{center}' >> $latexFile
	    echo '\end{figure}' >> $latexFile
	    echo '\clearpage' >> $latexFile
	    #Richard Leggett's Code
	    #Adds the summary and parses the fastqc data to get the data for the summary
	    echo "\section*{Sample $parsedSampleName}" >> $latexFile 
	    echo "Run Name: $parsedRunFolderName" >> $latexFile 
        echo "\\subsection*{Basic Statistics}" >> $latexFile;
        echo "\\begin{table}[h!]" >> $latexFile
        echo "{\\footnotesize" >> $latexFile
        echo "\\begin{tabular}{l l}" >> $latexFile
        grep -A 8 'Basic Statistics' ${fastqcFolderPath}/fastqc_data.txt | grep -A 7 'Filename' | perl -nae 'my @arr=split(/\t/); print $arr[0], " & ", $arr[1], "\\\\\n"' | sed 's/\%/\\%/g' | sed 's/_/\\_/g' >> $latexFile
	    echo "Q30 Length & $Q30Length \\" >> $latexFile
        echo "\\end{tabular}" >> $latexFile
        echo "}" >> $latexFile
        echo "\\end{table}" >> $latexFile

        echo "\\subsection*{Module summary}" >> $latexFile;
        echo "\\begin{table}[h!]" >> $latexFile
        echo "{\\footnotesize" >> $latexFile
        echo "\\begin{tabular}{l l l l}" >> $latexFile
        cat ${fastqcFolderPath}/fastqc_data.txt | grep '>>' | grep -v 'END_MODULE' | sed 's/>>//' | perl -nae 'my @arr=split(/\t/); $arr[1]=~s/\n//; print $arr[0], " & ", $arr[1], " \\\\\n";' >> $latexFile
        echo "\\end{tabular}" >> $latexFile
        echo "}" >> $latexFile
        echo "\\end{table}" >> $latexFile

        echo "\\subsection*{Overrepresented sequences}" >> $latexFile;
        echo "\\begin{table}[h!]" >> $latexFile
        echo "{\\tiny" >> $latexFile
        echo "\\begin{tabular}{l l l l}" >> $latexFile
        awk '/Overrepresented sequences/,/END_MODULE/ {print}' ${fastqcFolderPath}/fastqc_data.txt | tail -n +3 | head -n -1 | head -n 45 | perl -nae 'my @arr=split(/\t/); print $arr[0], " & ", $arr[1]," & ", $arr[2], " & ", $arr[3], "\\\\\n"' | sed 's/\%/\\%/g' >> $latexFile
        echo "\\end{tabular}" >> $latexFile
        echo "}" >> $latexFile
        echo "\\end{table}" >> $latexFile
        echo "\\clearpage" >> $latexFile

        #add the per_tile_quality.png to the plots if it exists
        if [[ -e $imagePath/per_tile_quality.png ]]; then
	        echo '\begin{figure}[ht]' >> $latexFile
	        echo "\caption{ 'per tile sequence quality' }" >> $latexFile
	        echo '\begin{center}' >> $latexFile
	        echo '\subfigure{' >> $latexFile
	        echo "\includegraphics[width=0.3\textwidth]{$imagePath/per_tile_quality.png} }" >> $latexFile
	        echo '\end{center}' >> $latexFile
	        echo '\end{figure}' >> $latexFile

        fi

        

	    echo '\end{document}' >> $latexFile

        #running  
	    if [ -e $latexPrefix.tex ]; then
	    	pdflatex --shell-escape --file-line-error --interaction=batchmode --output-directory $latexOutFolder $latexPrefix.tex &> /dev/null 
	    else
	    	echo "Latex Prefix $latexPrefix.tex not found"
	    fi
	    #latex tidyup
	    rm $latexPrefix.tex 
	    rm $latexPrefix.aux 
	    rm $latexPrefix.log
        if [[ -e $TMPDIR/genPDF ]]; then
            #echo "Cleaned up temporary folder $TMPDIR/genPDF/"
            rm -r $TMPDIR/genPDF 
        fi

        return 0
    #if pdflatex isn't in path, errro
    else
        echo "Error: pdflatex not found in path"
        return 1
 fi
}

#first arguement is the path of the _fastqc folder or the zip
#second is the latex output folder
#the third arguement is the runFolder ID. This is just for record Keeping
#forth arguement is the Q30 length
if [ "$1" == "" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "This script generates a pdf for the fastqc output."
    echo "Arg 1: path to the *_fastqc folder or *_fastqc.zip."
    echo "Arg 2: output folder for the latex files."
    echo "Arg 3: run folder ID. Just for record keeping. Any string will do in a pinch."
    echo "Arg 4: Q30 length, just for record keeping again, if you don't know, write NA?"
    exit 0
    #help!
else
    generateLatexFiles $1 $2 $3 $4
fi

