/*
 * File:        dataDB_logos.js
 * Version:     1.0
 * Description: functions for parsing svg logos and highlighting on mouseover
 * Author:      Nick Schurch (Barton Group, CLS, Univ. of Dundee)
 * Language:    Javascript
 * License:     GPL
 * Project:     almostSignificant
 * 
 * Copyright 2013 Nick Schurch, all rights reserved.
 */

function loadLogoScripts(STATIC_URL, highlightcol) {
	
	/* inserts arrow.svg into each openIcon spam 
	 * fuck me this was hard to get working!
	 * */

	d3.selectAll("#UODlogo").each(function() {
	    var thisspan = this;
		d3.xml(STATIC_URL+"almostSignificant/images/UODlogo.svg", "image/svg+xml", function(xml) {
	    	d3.select(thisspan).select(function() {
	    		return this.appendChild(xml.documentElement);
	    	});
	    });
	});
	d3.selectAll("#GSUlogo").each(function() {
	    var thisspan = this;
		d3.xml(STATIC_URL+"almostSignificant/images/GSUlogo.svg", "image/svg+xml", function(xml) {
	    	d3.select(thisspan).select(function() {
	    		return this.appendChild(xml.documentElement);
	    	});
	    });
	});


	$(".mainlogo").mouseover(function(){
		var collayer = d3.hsl(highlightcol);
		var t = d3.select(this);
		var svgobjs = ["path", "rect", "polyline", "line"];
		var attrs = ["fill"];
		for (var i=0; i<svgobjs.length; i++) {
			t.selectAll(svgobjs[i]).each(function() {
				for (var j=0; j<attrs.length; j++) {
					var currentcol = d3.select(this).attr(attrs[j]);
					d3.select(this).attr("old"+attrs[j], function(){
						return(currentcol);
					});
					if (currentcol!="none") {
						d3.select(this).attr(attrs[j], function(){
							var thiscolor = collayer;
							var shade = d3.hsl(currentcol).l
							if (shade>0.8) {
								thiscolor.l = 0.8;
							} else if (shade<0.4) {
								thiscolor.l = 0.4;
							} else {
								thiscolor.l = shade;
							}
							return(thiscolor);
						});
					}
				}
			});	
		}
	});
		    		
	$(".mainlogo").mouseout(function(){
		var t = d3.select(this);
		var svgobjs = ["path", "rect", "polyline", "line"];
		var attrs = ["fill", "stroke"];
		for (var i=0; i<svgobjs.length; i++) {
			t.selectAll(svgobjs[i]).each(function() {
				for (var j=0; j<attrs.length; j++) {
					var oldcol = d3.select(this).attr("old"+attrs[j]);
					d3.select(this).attr(attrs[j], function(){
						return(d3.select(this).attr("old"+attrs[j]));
					});
				}
			});	
		}
	});

	
	
	
}
