/*
 * File:        igbcontrols.js
 * Version:     1.0
 * Description: Settings for calling igb dataset loads from javascript
 * Author:      Nick Schurch (Barton Group, CLS, Univ. of Dundee)
 * Language:    Javascript
 * License:     GPL
 * Project:     polyADB
 * 
 * Copyright 2013 Nick Schurch, all rights reserved.
 */

	function loadDataToIGB()
	{	
		$(".igbIcon", window.mainTableElement).live('click', function () {
			
			/* call IGBs localhost URL to load data */
	        
			urlstr = "http://localhost:7085/UnibrowControl?version=H_sapiens_Feb_2009&seqid=chr1&start=152270949&end=152300347";
			urlstr2 = 'http://localhost:7085/UnibrowControl?version=C_elegans_Oct_2010&seqid=chrV&start=5856205&end=5856943';
			urlstr3 = 'http://localhost:7085/UnibrowControl?version=H_sapiens_Feb_2009&seqid=chr1&start=152270949&end=152300347&loadresidues=false&feature_url_0=http%3A%2F%2Figbquickload.org%2Fquickload%2FH_sapiens_Feb_2009%2FcytoBand.cyt&sym_method_0=__cytobands&sym_ypos_0=0&sym_yheight_0=50&sym_col_0=0x333399&sym_bg_0=0xDEE0E0&sym_name_0=__cytobands&feature_url_1=http%3A%2F%2Figbquickload.org%2Fquickload%2FH_sapiens_Feb_2009%2FH_sapiens_Feb_2009_refGene.bed.gz&sym_method_1=http%3A%2F%2Figbquickload.org%2Fquickload%2FH_sapiens_Feb_2009%2FH_sapiens_Feb_2009_refGene.bed.gz&sym_ypos_1=0&sym_yheight_1=50&sym_col_1=0x333399&sym_bg_1=0xDEE0E0&sym_name_1=RefGene&query_url=http%3A%2F%2Figbquickload.org%2Fquickload%2FH_sapiens_Feb_2009%2FcytoBand.cyt&query_url=http%3A%2F%2Figbquickload.org%2Fquickload%2FH_sapiens_Feb_2009%2FH_sapiens_Feb_2009_refGene.bed.gz&server_url=http%3A%2F%2Figbquickload.org%2Fquickload%2F&server_url=http%3A%2F%2Figbquickload.org%2Fquickload%2F&create=2013%2F06%2F05+18%3A10%3A48&modified=2013%2F06%2F05+18%3A10%3A48';
			console.log(urlstr3);
			
			$.ajax({url:urlstr3,
					type:"GET",
					success: function(response){
						console.log("done first ajax call");
						},
					error: function(jqXHR, textStatus, errorThrown) {
							console.log("errored");
					},
					complete: function(response){
						console.log("completed");
					},
					crossDomain: true,
					});
		});
	}
