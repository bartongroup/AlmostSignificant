    function loadDatasetTable(DataTableIDTag) {
    /* Called for /gsuStats/run/
     * Calls ajax from /gsuStats/Ajax/run/
     * Generates Datatables for /gsuStats/run/
     */
 
        
        
        var table = {
            "sScrollY":"600px",
            "sScrollYInner":"100%",
            "bInfo":true,
            "bScrollAutoCss":false,
            "bLengthChange":true,
            "iDisplayLength":-1,
            "aLengthMenu":[[-1,25,50,100],["All",25,50,100]],
            "bProcessing":true,
            "bSort":true,
            "bJQueryUI":false,
            "bDeferRender":true,
            "bStateSave":true,
            "sDom":'<"#showRows"l><"#displayTableTools"T><"#searchBox"f><"#mainTable"rt><"#tableInfo"i><"#tablePagination"p>',
            "sPaginationType":"full_numbers",
        };
        
        /* 
 *       * add the functions to apply after every row is called. adding icons to every row
 *               * needs to go here or they will not be added beyond the first page of results.
 *                       */
        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
           // $('td:eq(0)', nRow).addClass("rankcell");
           // $('td:eq(0)', nRow).html('<div class="rank"><b>'+(iDisplayIndexFull+1)+'</b></div>');

            /* inserts arrow.svg into each openIcon span. Its added to every row
 *           * as it is draw, but only if its not been seen before. 
 *                       * Fuck me this was hard to get working!
 *                                   */
            var thisspan = d3.select($(".openIcon", nRow))[0][0];
            if (thisspan.hasClass('emptySpan')) {
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan[0]).classed("emptySpan", false);
                    d3.select(thisspan[0]).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            };
            return(nRow)
         }
        
        /* 
         *          * add sort tooltips for column headers
         *                   */
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
        
        /* Post-table load event managers */
        /* Turn off pagination if it's not needed */
        table["fnInitComplete"] = function(){
                /* turn off pagination if its not needed */
                   if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1)  {
                       $('.dataTables_paginate').css("display", "block");    
                   } else {
                       $('.dataTables_paginate').css("display", "none");
                   }
/*            d3.selectAll(".openIcon").each(function() {
                var thisspan = this;
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            });*/
            runExpandRow();
          //  loadProcessingDetails()

        }

        //ajax call. Generates the data tables on sucess
        $.ajax({
            "url": "runs/Ajax/",
            "success": function(json) {
                table["aoColumns"] = json.aoColumns;
                /* replace col6 data with appropriate icons*/ 
                table["aoColumns"][0]["mData"] = processPrivateFlag;
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


    function loadRunTable(DataTableIDTag) {
    /*
     * Called for /gsuStats/run/<run name>
     * Gets ajax from /gsuStats/Ajax/run/<run name>
     * Generates the datatables for /gsuStats/run/<run Name>
     */
    
        
        /* gets the current url for the run name */
        var windowLoc = window.location
        var urlArray = String(windowLoc).split('/')
        var run_name = urlArray.slice(-2)[0]

        var table = {
            "sScrollY":"600px",
            "sScrollYInnder": "100%",
            "bInfo":true,
            "bScrollAutoCss":false,
            "bLengthChange":true,
            "iDisplayLength":-1,
            "aLengthMenu":[[-1,25,50,100],["All",25,50,100]],
            "bProcessing":true,
            "bSort":true,
            "bJQueryUI":false,
            "bDeferRender":true,
            "bStateSave":true,
            "sDom":'<"#showRows"l><"#displayTableTools"T><"#searchBox"f><"#mainTable"rt><"#tableInfo"i><"#tablePagination"p>',
            "sPaginationType":"full_numbers",
        };

    /* 
     *           add the functions to apply after every row is called. adding icons to every row
     *           needs to go here or they will not be added beyond the first page of resuts.
        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
               $('td:eq(0)', nRow).addClass("rankcell"); 
               $('td:eq(0)', nRow).html('<div class="rank"><b>'+(iDisplayIndexFull+1)+'</b></div>');
            return(nRow)
         }

     */
        /* 
 *       * add the functions to apply after every row is called. adding icons to every row
 *               * needs to go here or they will not be added beyond the first page of results.
 *                       */
        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {

            /* inserts arrow.svg into each openIcon span. Its added to every row
 *           * as it is draw, but only if its not been seen before. 
 *                       * Fuck me this was hard to get working!
 *                                   */
            var thisspan = d3.select($(".openIcon", nRow))[0][0];
            if (thisspan.hasClass('emptySpan')) {
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan[0]).classed("emptySpan", false);
                    d3.select(thisspan[0]).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            };
            return(nRow)
         }
        
        /* 
         *          * add sort tooltips for column headers
         *                   */
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
        
        /* Post-table load event managers */
        /* Turn off pagination if it's not needed */
        table["fnInitComplete"] = function(){
                /* turn off pagination if its not needed */
                   if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1)  {
                       $('.dataTables_paginate').css("display", "block");    
                   } else {
                       $('.dataTables_paginate').css("display", "none");
                   }
            /* Nick: inserts arrow.svg into each openIcon spam 
 *              *       fuck me this was hard to get working!
 *                Joe:  Thankfully, I didn't have to get this working.
 *                         Nick did the hard job. Winner.
 *                           * */
/*            d3.selectAll(".openIcon").each(function() {
                var thisspan = this;
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            });*/
            experimentExpandRow();
            //loadProcessingDetails();
        }
    
        //magical ajax call
        var urlString = "Ajax/";
        $.ajax({
            "url": urlString,
            "success": function(json) {
                table["aoColumns"] = json.aoColumns;
                /* replace col6 data with appropriate icons*/ 
                table["aoColumns"][0]["mData"] = processPrivateFlag;
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
    //Inserts the arrow for the drop down column in the datatables
    source.img = '<span class="openIcon emptySpan" style="display:inline-block" title="show more details"></span>'
           
       if (type === 'display') {
           return(source.img);
       } else {
       // 'filter', 'sort' and 'type' both just use the raw data
           return source[1];
    } 
}

    function getScrollbarWidth() {
        //Calculates the width of the scrollbar. This allows us to put the 
        //scrollbar at the side even when it isn't needed so that things look good 
        //when it is rendered then removed
        div = document.createElement('div');
        div.innerHTML = '<div style="width:50px;height:50px;position:absolute;left:-50px;top:-50px;overflow:auto;"><div style="width:1px;height:100px;"></div></div>';
        div = div.firstChild;
        document.body.appendChild(div);
        width = getScrollbarWidth.width = div.offsetWidth - div.clientWidth;
        document.body.removeChild(div);
        return width;
    };



    function experimentExpandRow() {
        /* this function defines what to do for this page when the expand icon is clicked */
        //This is for the sample drop down in /gsuStats/run/<run id>
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





    function getDatasetDetails(thisDataTable, thisRow, thisSubTable)
    {   //loads the information into the drop down items in /gsuStats/run/<run id> 
        /* get the dataset details based on the experiment id 
 *          * (passed as DT_RowID in the JSON data */
        
        var rowData = thisDataTable.fnGetData(thisRow);
        var urlstr = "sample/"+rowData["DT_RowId"]+"/Ajax/";
        var thisLoadingTD = $("td div", thisSubTable);
        $.ajax({url:urlstr,
                dataType:"json",
                success: function(data)
                    {
                        $(thisLoadingTD).html(data["htmlTabs"]);
                        $(thisLoadingTD).tabs();
                        $(thisLoadingTD).tabs('option', 'active', 0);
                    },
/*                complete: function()
                    {
                        /* inserts lock.svg into each unpopulated 
 *                          * tinyprivatedata span; fuck me this was hard to get 
 *                                                   * working!
 *                                                                            */
                        
/*                        d3.selectAll(".tinyprivatedata").each(function() {
                            var thisspan = this;
                            if (thisspan.childNodes.length<1){
                                d3.xml("static/almostSignificant/img/lock.svg", "image/svg+xml", function(xml) {
                                    d3.select(thisspan).select(function() {
                                        return this.appendChild(xml.documentElement);
                                    });
                                });
                            }
                        }); 
                    } */
            });        
    }

    function runExpandRow() {
        //handles the drop down for /gsuStats/run 
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
            getRunDetails(thisTable, nTr, thisSubTable);

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


    function getRunDetails(thisDataTable, thisRow, thisSubTable)
    {    
       //Handles  the content of the dropdown for /gsuStats/run
       //After it loads the first tab, it then launches into loading all of the lane
       //tabs using funcLaneDetails
        /* get the dataset details based on the experiment id 
 *          * (passed as DT_RowID in the JSON data */
        /* also populates all of the lane tabs with the read distribution graphs
 *          that are passed in the laneDetails section of the JSON as urls to 
 *          the json for the lane. It makes sense in my head */
        
        var rowData = thisDataTable.fnGetData(thisRow);
        var urlstr = "runs/"+rowData["DT_RowId"]+"/Ajax/";
        var thisLoadingTD = $("td div", thisSubTable);
        $.ajax({url:urlstr,
                dataType:"json",
                success: function(data)
                    {
                        $(thisLoadingTD).html(data["htmlTabs"]);
                        $(thisLoadingTD).tabs();
                        $(thisLoadingTD).tabs('option', 'active', 0);
                    },
                complete: function(data)
                    {
                    //populate the lane tabs with graphs
                    var json = jQuery.parseJSON(data.responseText);
                    //Size for the plot
                    for (laneDetails in json["laneDetails"]) 
                        {
                        var urlStr = json["laneDetails"][laneDetails];
                        var divID = "r" + json["runID"] + "l" + laneDetails +"plot"; 
                        var tabID = "lane" + laneDetails + "tab"; 
                        var myDiv = document.getElementById(divID);
                        //myDiv.innerHTML = "<script>$( document ).ready( function() {$('" + tabID + "').click(function(){ funcLaneDetails(" + laneDetails + "," + urlStr + ")}}</script>"
                        funcLaneDetails(laneDetails,json["runID"],urlStr);
                        }
                    }        
            });
    }

    function funcLaneDetails(laneDetails,runID,urlStr) 
        //this loads the graphs in the lane tabs for /gsuStats/run/
        //Loads my barchart function from barchart.js
        //D3 is awesome fun.
        {
        $.ajax({
        dataType:"json",
        url:urlStr,
        success: function(json)
               {
               var divID = "#r" + runID + "l" + laneDetails +"plot"; 
               //var myDiv = document.getElementById(divID);
               //myDiv = document.getElementById(divID);
               var dataset = json["aaData"];
               var lableArray = dataset[0]["lableArray"];
               var readArray = dataset[0]["readArray"];
               var baseArray = dataset[0]["baseArray"];
               //var read2Array = dataset[0]["value2Array"];
               //stackedBarchart(lableArray, valueArray, value2Array,divID);
               barchart(lableArray, readArray, divID);
               //numberedBarchart(lableArray, readArray, baseArray, divID);
               }
               });
        };


    /* For the project Overview */
    function loadProjectOverviewTable(DataTableIDTag) {
       //Loads the ajax and generates the datatables for /gusStats/project/
        /* inserts arrow.svg into each openIcon span. Its added to every row
 *       * as it is draw, but only if its not been seen before. 
 *               * Fuck me this was hard to get working!
 *                      */ 
        var table = {
            "sScrollY":"600px",
            "sScrollYInner":"100%",
            "bInfo":true,
            "bScrollAutoCss":false,
            "bLengthChange":true,
            "iDisplayLength":-1,
            "aLengthMenu":[[-1,25,50,100],["All",25,50,100]],
            "bProcessing":true,
            "bSort":true,
            "bJQueryUI":false,
            "bDeferRender":true,
            "bStateSave":true,
            "sDom":'<"#showRows"l><"#displayTableTools"T><"#searchBox"f><"#mainTable"rt><"#tableInfo"i><"#tablePagination"p>',
            "sPaginationType":"full_numbers",
        };

        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {

            /* inserts arrow.svg into each openIcon span. Its added to every row
 *           * as it is draw, but only if its not been seen before. 
 *                       * Fuck me this was hard to get working!
 *                                   */
            var thisspan = d3.select($(".openIcon", nRow))[0][0];
            if (thisspan.hasClass('emptySpan')) {
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan[0]).classed("emptySpan", false);
                    d3.select(thisspan[0]).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            };
            return(nRow)
         }
  
        /* 
         *          * add sort tooltips for column headers
         *                   */
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
        
        /* Post-table load event managers */
        /* Turn off pagination if it's not needed */
        table["fnInitComplete"] = function(){
                /* turn off pagination if its not needed */
                   if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1)  {
                       $('.dataTables_paginate').css("display", "block");    
                   } else {
                       $('.dataTables_paginate').css("display", "none");
                   }
            projectExpandRow();
        }
        //ajax magic
        $.ajax({
            "url": "Ajax/",
            "success": function(json) {
                table["aoColumns"] = json.aoColumns;
                /* replace col6 data with appropriate icons*/ 
                table["aoColumns"][0]["mData"] = processPrivateFlag;
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

    function projectExpandRow() {
        /* this function defines what to do for this page when the expand icon is clicked */
        //This is for the sample drop down in /gsuStats/projects/
        $(".openIcon",window.mainTableElement).live('click', function () {
            /* toggle icon */
            $(this).toggleClass('openIcon closeIcon');
            //$(this).removeClass('openIcon').addClass('closeIcon');
            $(this).rotate({animateTo:180});
            $(this).attr("title","hide more details");
            
            /* get row, then open new row and call getDatasetDetails */ 
            var nTr = $(this).parents('tr')[0];            
            var thisSubTable = thisTable.fnOpen(nTr, '<div class="innerDetails"><div class="loadingSpin"></div><div class="smallLoadingDiv">Retrieving information from the database...</div></div>', 'details');
            $('div.innerDetails', thisSubTable).slideDown();
            getProjectDetails(thisTable, nTr, thisSubTable);

        });
        
        $(".closeIcon",window.mainTableElement).live('click', function () {
            /* toggle icon */
            $(this).toggleClass('openIcon closeIcon');
           // $(this).removeClass('closeIcon').addClass('openIcon');
            $(this).rotate({animateTo:0});
            $(this).attr("title","show more details");
                
            /* get row then close the next row */
            var nTr = $(this).parents('tr')[0];            
            $('div.innerDetails', $(nTr).next()[0]).slideUp(function(){thisTable.fnClose(nTr);});                
        } );
    }

    function getProjectDetails(thisDataTable, thisRow, thisSubTable)
    {    
       //Handles  the content of the dropdown for /gsuStats/projects/
       //After it loads the first tab, it then launches into loading all of the lane
       //tabs using funcLaneDetails
        /* get the dataset details based on the experiment id 
 *          * (passed as DT_RowID in the JSON data */
        /* also populates all of the lane tabs with the read distribution graphs
 *          that are passed in the laneDetails section of the JSON as urls to 
 *          the json for the lane. It makes sense in my head */
        
        var rowData = thisDataTable.fnGetData(thisRow);
        var urlstr = rowData["DT_RowId"]+"/id/Ajax/";
        var thisLoadingTD = $("td div", thisSubTable);
        $.ajax({url:urlstr,
                dataType:"json",
                success: function(data)
                    {
                        $(thisLoadingTD).html(data["htmlTabs"]);
                        $(thisLoadingTD).tabs();
                        $(thisLoadingTD).tabs('option', 'active', 0);
                    },
//                complete: function(data)
//                    {
//                    //populate the lane tabs with graphs
//                    var json = jQuery.parseJSON(data.responseText);
//                    //Size for the plot
//                    for (laneDetails in json["laneDetails"]) 
//                        {
//                        var urlStr = json["laneDetails"][laneDetails];
//                        var divID = "r" + json["runID"] + "l" + laneDetails +"plot"; 
//                        var tabID = "lane" + laneDetails + "tab"; 
//                        var myDiv = document.getElementById(divID);
//                        //myDiv.innerHTML = "<script>$( document ).ready( function() {$('" + tabID + "').click(function(){ funcLaneDetails(" + laneDetails + "," + urlStr + ")}}</script>"
//                        funcLaneDetails(laneDetails,json["runID"],urlStr);
//                        }
//                    }        
            });
    }



    /* Presents the view for the project details */
    function loadProjectTable(DataTableIDTag) {
        //Loads the ajax and datatables for /gsuStats/project/<project name> 
        /* gets the current url for the run name */
        var windowLoc = window.location
        var urlArray = String(windowLoc).split('/')
        var project_name = urlArray.slice(-2)[0]

        var table = {
            "sScrollYInner":"100%",
            "sScrollY":"600px",
            "bScrollAutoCss":false,
            "bInfo":true,
            "bLengthChange":true,
            "iDisplayLength":-1,
            "aLengthMenu":[[-1,25,50,100],["All",25,50,100]],
            "bProcessing":true,
            "bSort":true,
            "bJQueryUI":false,
            "bDeferRender":true,
            "bStateSave":true,
            "sDom":'<"#showRows"l><"#displayTableTools"T><"#searchBox"f><"#mainTable"rt><"#tableInfo"i><"#tablePagination"p>',
            "sPaginationType":"full_numbers",
        };

    /* 
     *           add the functions to apply after every row is called. adding icons to every row
     *           needs to go here or they will not be added beyond the first page of resuts.
        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
               $('td:eq(0)', nRow).addClass("rankcell"); 
               $('td:eq(0)', nRow).html('<div class="rank"><b>'+(iDisplayIndexFull+1)+'</b></div>');
            return(nRow)
         }

     */
        /* 
 *       * add the functions to apply after every row is called. adding icons to every row
 *               * needs to go here or they will not be added beyond the first page of results.
 *                       */
        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {

            /* inserts arrow.svg into each openIcon span. Its added to every row
 *           * as it is draw, but only if its not been seen before. 
 *                       * Fuck me this was hard to get working!
 *                                   */
            var thisspan = d3.select($(".openIcon", nRow))[0][0];
            if (thisspan.hasClass('emptySpan')) {
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan[0]).classed("emptySpan", false);
                    d3.select(thisspan[0]).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            };
            return(nRow)
         }
        
        /* 
         *          * add sort tooltips for column headers
         *                   */
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
        
        /* Post-table load event managers */
        /* Turn off pagination if it's not needed */
        table["fnInitComplete"] = function(){
                /* turn off pagination if its not needed */
                   if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1)  {
                       $('.dataTables_paginate').css("display", "block");    
                   } else {
                       $('.dataTables_paginate').css("display", "none");
                   }
            /* Nick: inserts arrow.svg into each openIcon spam 
 *              *       fuck me this was hard to get working!
 *                Joe:  Thankfully, I didn't have to get this working.
 *                         Nick did the hard job. Winner.
 *                           * */
/*            d3.selectAll(".openIcon").each(function() {
                var thisspan = this;
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            });*/
           experimentExpandRow();
           // loadProcessingDetails();

        }
    
        var urlString = "Ajax/";
        $.ajax({
            "url": urlString,
            "success": function(json) {
                table["aoColumns"] = json.aoColumns;
                /* replace col6 data with appropriate icons*/ 
                table["aoColumns"][0]["mData"] = processPrivateFlag;
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

/*    function loadProcessingDetails() {
        $(".proclink", window.mainTableElement).live({
            mouseenter: function (){
                displaydiv = this.id;
                $("div#"+displaydiv)[0].innerHTML=$(this).attr("data-value");
                $(this).css("color", "#9fda58");
                
            },
            mouseleave: function(){
                $(this).css("color", "white");
            }
        });
    };
*/

/*################################################################################
        Statistics page stuff
################################################################################*/
    function loadStatisticsTable(DataTableIDTag) {
    /* Called for /gsuStats/stats/
     * Calls ajax from /gsuStats/Ajax/stats/
     * Generates Datatables for /gsuStats/stats/
     */
 
        
        
        var table = {
            "sScrollY":"600px",
            "sScrollYInner":"100%",
            "bInfo":true,
            "bScrollAutoCss":false,
            "bLengthChange":true,
            "iDisplayLength":-1,
            "aLengthMenu":[[-1,25,50,100],["All",25,50,100]],
            "bProcessing":true,
            "bSort":true,
            "bJQueryUI":false,
            "bDeferRender":true,
            "bStateSave":true,
            "sDom":'<"#showRows"l><"#displayTableTools"T><"#searchBox"f><"#mainTable"rt><"#tableInfo"i><"#tablePagination"p>',
            "sPaginationType":"full_numbers",
        };
        
        /* 
 *       * add the functions to apply after every row is called. adding icons to every row
 *               * needs to go here or they will not be added beyond the first page of results.
 *                       */
        table["fnRowCallback"] = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
           // $('td:eq(0)', nRow).addClass("rankcell");
           // $('td:eq(0)', nRow).html('<div class="rank"><b>'+(iDisplayIndexFull+1)+'</b></div>');

            /* inserts arrow.svg into each openIcon span. Its added to every row
 *           * as it is draw, but only if its not been seen before. 
 *                       * Fuck me this was hard to get working!
 *                                   */
            var thisspan = d3.select($(".openIcon", nRow))[0][0];
            if (thisspan.hasClass('emptySpan')) {
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan[0]).classed("emptySpan", false);
                    d3.select(thisspan[0]).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            };
            return(nRow)
         }
        
        /* 
         *          * add sort tooltips for column headers
         *                   */
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
// FOR THE DROPDOWN        
        /* Post-table load event managers */
        /* Turn off pagination if it's not needed */
        table["fnInitComplete"] = function(){
                /* turn off pagination if its not needed */
                   if (Math.ceil((this.fnSettings().fnRecordsDisplay()) / this.fnSettings()._iDisplayLength) > 1)  {
                       $('.dataTables_paginate').css("display", "block");    
                   } else {
                       $('.dataTables_paginate').css("display", "none");
                   }
/*            d3.selectAll(".openIcon").each(function() {
                var thisspan = this;
                d3.xml("/static/almostSignificant/img/arrow.svg", "image/svg+xml", function(xml) {
                    d3.select(thisspan).select(function() {
                        return this.appendChild(xml.documentElement);
                    });
                });
            });*/
            statsExpandRow();
          //  loadProcessingDetails()

        }

        //ajax call. Generates the data tables on sucess
        $.ajax({
            "url": "Ajax/",
            "success": function(json) {
                table["aoColumns"] = json.aoColumns;
                /* replace col6 data with appropriate icons*/ 
                table["aoColumns"][0]["mData"] = processPrivateFlag;
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

    function getStatisticsDetails(thisDataTable, thisRow, thisSubTable)
    {    
       //Handles  the content of the dropdown for /gsuStats/projects/
       //After it loads the first tab, it then launches into loading all of the lane
       //tabs using funcLaneDetails
        /* get the dataset details based on the experiment id 
 *          * (passed as DT_RowID in the JSON data */
        /* also populates all of the lane tabs with the read distribution graphs
 *          that are passed in the laneDetails section of the JSON as urls to 
 *          the json for the lane. It makes sense in my head */
        
        var rowData = thisDataTable.fnGetData(thisRow);
        var urlstr = rowData["DT_RowId"] + "/Ajax/";
        var thisLoadingTD = $("td div", thisSubTable);
        $.ajax({url:urlstr,
                dataType:"json",
                success: function(data)
                    {
                        $(thisLoadingTD).html(data["htmlTabs"]);
                        $(thisLoadingTD).tabs();
                        $(thisLoadingTD).tabs('option', 'active', 0);
                    },
                complete: function(data)
                    {
                        //parse the json!
                        var json = jQuery.parseJSON(data.responseText);
                        //lane reads distribution plot
                        divIDlaneReads="#laneReadsDist" + rowData["DT_RowId"] + "tab-div";
                        premadeHist(json["laneReads"],divIDlaneReads);

                        //cluster density distribution plot
                        divIDdensityPlot="#densityDiv" + rowData["DT_RowId"] + "tab-div";
                        densityScatterGraph(json["densityStats"],divIDdensityPlot,
                                "Cluster Density k/mm2","Number of Reads in the Lane");
                        divID="#laneReadsDist" + rowData["DT_RowId"] + "tab-div";
                        divIDdensityPlot="#laneQ30" + rowData["DT_RowId"] + "tab-div";
                        densityScatterGraph(json["laneQ30"],divIDdensityPlot,
                                "Cluster Density k/mm2","Mean Q30 Length for the Lane");
                        divID="#laneReadsDist" + rowData["DT_RowId"] + "tab-div";
                        //first base report
                        if(rowData["DT_RowId"].indexOf("MiSeq") < 0) {
                            divIDfbrPlot="#firstBase" + rowData["DT_RowId"] + "tab-div";
                            densityScatterGraph(json["firstBase"],divIDfbrPlot,
                                    "Cluster Density k/mm2","First Base Report Cluster Density");
                        };
//                    //Size for the plot
//                    for (laneDetails in json["laneDetails"]) 
//                        {
//                        var urlStr = json["laneDetails"][laneDetails];
//                        var divID = "r" + json["runID"] + "l" + laneDetails +"plot"; 
//                        var tabID = "lane" + laneDetails + "tab"; 
//                        var myDiv = document.getElementById(divID);
//                        //myDiv.innerHTML = "<script>$( document ).ready( function() {$('" + tabID + "').click(function(){ funcLaneDetails(" + laneDetails + "," + urlStr + ")}}</script>"
//                        funcLaneDetails(laneDetails,json["runID"],urlStr);
//                        }
                    }        
            });
    }

    function statsExpandRow() {
        //handles the drop down for /gsuStats/run 
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
            getStatisticsDetails(thisTable, nTr, thisSubTable);

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

//    function getDensityDetails(thisDataTable, thisRow, thisSubTable)
//    {    
//       //Handles  the content of the dropdown for /gsuStats/projects/
//       //After it loads the first tab, it then launches into loading all of the lane
//       //tabs using funcLaneDetails
//        /* get the dataset details based on the experiment id 
// *          * (passed as DT_RowID in the JSON data */
//        /* also populates all of the lane tabs with the read distribution graphs
// *          that are passed in the laneDetails section of the JSON as urls to 
// *          the json for the lane. It makes sense in my head */
//        
//        var rowData = thisDataTable.fnGetData(thisRow);
//        var urlstr = "/gsuStats/Ajax/stats/density"+rowData["DT_RowId"];
//        var thisLoadingTD = $("td div", thisSubTable);
//        $.ajax({url:urlstr,
//                dataType:"json",
//                success: function(data)
//                    {
//                        $(thisLoadingTD).html(data["htmlTabs"]);
//                        $(thisLoadingTD).tabs();
//                        $(thisLoadingTD).tabs('option', 'active', 0);
//                        console.log(data["htmlTabs"]);
//                    },
//                complete: function(data)
//                    {
//                        //parse the json!
//                        var json = jQuery.parseJSON(data.responseText);
//                        //lane reads distribution plot
//                        divIDlaneReads="#laneReadsDist" + rowData["DT_RowId"] + "tab-div";
//                        premadeHist(json["laneReads"],divIDlaneReads);
//                        //cluster density distribution plot
//                        divIDDensityPlot="#densityDiv" + rowData["DT_RowId"] + "tab-div";
//                        densityScatterGraph(json["densityStats"],divIDdensityPlot);
////                    //Size for the plot
////                    for (laneDetails in json["laneDetails"]) 
////                        {
////                        var urlStr = json["laneDetails"][laneDetails];
////                        var divID = "r" + json["runID"] + "l" + laneDetails +"plot"; 
////                        var tabID = "lane" + laneDetails + "tab"; 
////                        var myDiv = document.getElementById(divID);
////                        //myDiv.innerHTML = "<script>$( document ).ready( function() {$('" + tabID + "').click(function(){ funcLaneDetails(" + laneDetails + "," + urlStr + ")}}</script>"
////                        funcLaneDetails(laneDetails,json["runID"],urlStr);
////                        }
//                    }        
//            });
//    }
//
//
