/*
 * File:        dataDB_base.js
 * Version:     1.0
 * Description: Settings for working with databables/ajax in polyADB mainpage
 * Author:      Nick Schurch (Barton Group, CLS, Univ. of Dundee)
 * Language:    Javascript
 * License:     GPL
 * Project:     Pyrwise
 * 
 * Copyright 2013 Nick Schurch, all rights reserved.
 */

/*(function ($, window, document) {*/
		
	/* Page Specific functions */
	
	/* 
	 * 
	 * Dataset Summary Page 
	 *
	 */
		
	function loadDatasetTable(DataTableIDTag) {
		
		/* 
		 * Builds the Datasets data table - note that 'data' is generated
		 * server side with an ajax call.
		 */
		
		/* get defaults for the sites tables, add columns and the url of the 
		 * view to get the data from.
		 */
		var table = {
				"sScrollY": "600px",
	    		"bInfo": true,
	    		"bLengthChange": true,
	    		"iDisplayLength": 25,
	    		"aLengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
	    		"bProcessing": true,
	    		"bsort": true,
	    		"bJQueryUI": false,
	    		"bDeferRender": true,
	    		"bStateSave":true,
	    		"sDom":	'<"#showRows"l><"#displayTableTools"T><"#searchBox"f><"#mainTable"rt><"#tableInfo"i><"#tablePagination"p>',
				"oTableTools": {
					"sSwfPath": "copy_cvs_xls_pdf.swf"
				},
	    		"sPaginationType": "full_numbers",
	    		"oLanguage": {"sSearch": 'Filter datasets: _INPUT_\
	    					  			 <br><span id="filtertoggle">Filter based on: \
	    									<form class="searchradio" action="">\
	    										<input type="radio" name="search" class="searchradiobutton" checked>entire database\
	    										<input type="radio" name="search" class="searchradiobutton">table fields\
	    									</form>\
	    								 </span>'}
	    };
						
    	/* 
    	 * add the functions to apply after every row is called. adding icons to every row
    	 * needs to go here or they will not be added beyond the first page of resuts.
    	 */
		table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    		$('td:eq(0)', nRow).addClass("rankcell");
    		$('td:eq(0)', nRow).html('<div class="rank"><b>'+(iDisplayIndexFull+1)+'</b></div>');
    		/*
    		 * This has been replaced by the processPrivateFlag function below 
    		$('td:eq(1)', nRow).html('<span class="openIcon" style="display:inline-block" title="show more details"></span>');*/
    		return(nRow)
    	 }
	    
		/* 
		 * add sort tooltips for column headers
		 */
		table["fnDrawCallback"] = function() {
			$('th').each(function(){
				if (!$(this).hasClass('sorting_disabled')){
		            if (($(this).hasClass('sorting')) || ($(this).hasClass('sorting_desc')))  {
		            	$(this).attr({title: 'Sort Ascending'});
		            } else {
		                $(this).attr({title: 'Sort Descending'});
		            }
				}
			});
		}
		
    	/* 
    	 * Add any post-table load event managers - this is the only way I can get 
    	 * a 'click-on-row' event to work with a direct ajax data source. Basically,
    	 * you have to wait for the table to be populated with data in order to register
    	 * the on click events.
    	 */
    	table["fnInitComplete"] = function(){
    		/* turn off pagination if its not needed */
    		if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1)  {
    			$('.dataTables_paginate').css("display", "block");	
    	    } else {
    	        $('.dataTables_paginate').css("display", "none");
    	    }
    		
    		/* inserts arrow.svg into each openIcon spam 
    		 * fuck me this was hard to get working!
    		 * */
    		d3.selectAll(".openIcon").each(function() {
        	    var thisspan = this;
    			d3.xml("static/polyADB/img/arrow.svg", "image/svg+xml", function(xml) {
        	    	d3.select(thisspan).select(function() {
        	    		return this.appendChild(xml.documentElement);
        	    	});
        	    });
    		});
    		
    		experimentExpandRow();
    		toggleKeywordSearch();
    		loadDataToIGB();
    	}
				    	
    	$.ajax({
			"url": "Ajax/datasets/",
			"success": function(json) {
				table["aoColumns"] = json.aoColumns;
				/* replace col6 data with appropriate icons*/ 
				table["aoColumns"][1]["mData"] = processPrivateFlag;
				table["asSorting"] = json.asSorting;
				table["aaData"] = json.aaData;
				/* get the table element by ID and draw the dataTable */
				var main= document.getElementById(DataTableIDTag);
				thisTable = $(main).not('.initialized')
								   .addClass('initialized')
								   .attr("id", "thisTable")
								   .dataTable(table);
		    	/* add dynamic resize and other functions. */
				$(window).resize(function(){thisTable.fnAdjustColumnSizing();});
				if($("#content-filter").height() < $("#container").height()){
				    $("#content-filter").height($("#container").height());
				}
			},
			"dataType":"json"
		});
	 }

    function processPrivateFlag( source, type, val ) {
    	
    	/* this function allows the display of an icon for the private/public 
    	 * status if a dataset, while allowing the column to be sortable 
    	 * based on the underlying value. It uses the mData datatables call, 
    	 * however the docs seem to be rubbish for it so I made this up myself 
    	 * ;)
    	 */
    	
    	source.img = '<span class="openIcon" style="display:inline-block" title="show more details"></span>'
    	if (source[1]==1) {
    		source.img = source.img+'<img class="privatedata" title="private dataset" src="static/polyADB/img/lock.svg"/>'
    	}
    	    
    	if (type === 'display') {
            return(source.img);
        } else {
	        // 'filter', 'sort' and 'type' both just use the raw data
	        return source[1];
        }
     }
	
    function toggleKeywordSearch() {
    	$(".searchradiobutton").live('click', function () {
    		if (thisTable.fnSettings().aoColumns[7].bSearchable){
    			thisTable.fnSettings().aoColumns[7].bSearchable=false;
    		} else {
    			thisTable.fnSettings().aoColumns[7].bSearchable=true;
    		}
    		thisTable.fnDraw();
    	});
    }
    
	function experimentExpandRow() {
		
		/* this function defines what to do for this page when the expand icon is clicked */
		$(".openIcon",window.mainTableElement).live('click', function () {
			
			/* toggle icon */
	    	$(this).toggleClass('openIcon closeIcon');
	    	$(this).rotate({animateTo:180});
	    	$(this).attr("title","hide more details");
	    	
	    	/* get row, then open new row and call getDatasetDetails */ 
	        var nTr = $(this).parents('tr')[0];	        
			var thisSubTable = thisTable.fnOpen(nTr, '<div class="innerDetails"><div class="loadingSpin"></div><div class="smallLoadingDiv">Retrieving information from the database...</div></div>', 'details');
            $('div.innerDetails', thisSubTable).slideDown();
            getDatasetDetails(thisTable, nTr, thisSubTable);

	    });
	    
	    $(".closeIcon",window.mainTableElement).live('click', function () {
	    		    	
	    	/* toggle icon */
	    	$(this).toggleClass('openIcon closeIcon');
	    	$(this).rotate({animateTo:0});
	    	$(this).attr("title","show more details");
	    		
	    	/* get row then close the next row */
	        var nTr = $(this).parents('tr')[0];	        
            $('div.innerDetails', $(nTr).next()[0]).slideUp(function(){thisTable.fnClose(nTr);});	        	
	    } );
	}

	/*
	function experimentNextPage() {
		
		/* this function defines what to do for this page when the Next Page icon is clicked 

		$(".nextPageIcon",window.mainTableElement).live('click', function () {
			var thisRow = this.parentNode.parentNode;
			var rowData = window.mainTable.fnGetData(thisRow);
			var urlstr = "/pyrwise/expDetails/id="+rowData["DT_RowId"];
			document.location.href = urlstr;
		});
	}
	
	function getExperimentProbes(exptid) {
		var urlstr = "/pyrwise/Ajax/main/subtable/getProbes/id="+exptid
		$.ajax({url:urlstr, dataType:"json", success:function(data){
			document.getElementById('exp'+exptid+'datapoints').innerHTML=data;
		}});		
	}
	
	function getExperimentGenes(exptid) {
		var urlstr = "/pyrwise/Ajax/main/subtable/getEGenes/id="+exptid
		$.ajax({url:urlstr, dataType:"json", success:function(data){
			document.getElementById('exp'+exptid+'ensgenes').innerHTML=data;
		}});		
	}

	function getExperimentTrans(exptid) {
		var urlstr = "/pyrwise/Ajax/main/subtable/getETrans/id="+exptid
		$.ajax({url:urlstr, dataType:"json", success:function(data){
			document.getElementById('exp'+exptid+'enstrans').innerHTML=data;
		}});		
	}

	function getExperimentGO(exptid) {
		var urlstr = "/pyrwise/Ajax/main/subtable/getGO/id="+exptid
		$.ajax({url:urlstr, dataType:"json", success:function(data){
			document.getElementById('exp'+exptid+'go').innerHTML=data;
		}});		
	}*/

	function getDatasetDetails(thisDataTable, thisRow, thisSubTable)
	{	
		
		/* get the dataset details based on the experiment id 
		 * (passed as DT_RowID in the JSON data */
        
		var rowData = thisDataTable.fnGetData(thisRow);
		var urlstr = "Ajax/dataset/id="+rowData["DT_RowId"]
		var thisLoadingTD = $("td div", thisSubTable);
		$.ajax({url:urlstr,
				dataType:"json",
				success: function(data)
					{
						$(thisLoadingTD).html(data["htmlTabs"]);
						$(thisLoadingTD).tabs();
						$(thisLoadingTD).tabs('option', 'active', 0);
					},
				complete: function()
					{
						/* inserts lock.svg into each unpopulated 
						 * tinyprivatedata span; fuck me this was hard to get 
						 * working!
						 */
						
						d3.selectAll(".tinyprivatedata").each(function() {
				    	    var thisspan = this;
				    	    if (thisspan.childNodes.length<1){
								d3.xml("static/polyADB/img/lock.svg", "image/svg+xml", function(xml) {
					    	    	d3.select(thisspan).select(function() {
					    	    		return this.appendChild(xml.documentElement);
					    	    	});
					    	    });
				    	    }
						});
					}
			});		
	}
	
/*})(jQuery, window, document);*/
