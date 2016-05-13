/*
 * File:        dataDB_login.js
 * Version:     1.0
 * Description: functions for login popup div in dataDB webpage
 * Author:      Nick Schurch (Barton Group, CLS, Univ. of Dundee)
 * Language:    Javascript
 * License:     GPL
 * Project:     polyADB
 * 
 * Copyright 2013 Nick Schurch, all rights reserved.
 */

	function loadLoginScripts(token) {	

		var	showlogin = false;				
	    $('#logintext').click(function(e) {
	    	if (showlogin) {
	    		$(this).next('.loginpopup').hide();
	    		showlogin = false;
	    	} else {
				var loginLeft = $(window).width() - $("#loginpopup").width() -50;
			    var loginTop = $("#user-tools").position().top + $("#user-tools").height() - 5;
	    		$(this).next('.loginpopup').show()
		        	.css('top', loginTop)
		        	.css('left', loginLeft);
	    		$("#username").focus();
	    		showlogin = true;
	    	}
	    });
	    
	    $(window).resize(function() {
	    	if (showlogin) {
				var loginLeft = $(window).width() - $("#loginpopup").width() -50;
			    var loginTop = $("#user-tools").position().top + $("#user-tools").height() - 5;
			    $("#loginpopup").css('top', loginTop).css('left', loginLeft);
	    	}			    	
	    });
	    
        $("#cancellogin").click(function(){
        	$("#loginpopup").hide();
        	showlogin = false;
        });
       	
        $('#username').keyup(function (e) {
        	  var keyCode = e.keyCode || e.which;
        	  if (keyCode == 13) {
  		        $("#login").trigger('click')
        	  }
        });

        $('#password').keyup(function (e) {
        	  var keyCode = e.keyCode || e.which;
        	  if (keyCode == 13) {
  		        $("#login").trigger('click')
        	  }
        });
        		        
        $("#login").click(function(){
            var data = {"username": $('#username').val(),
            			"password": $('#password').val(),
            			"csrfmiddlewaretoken": token
            			};
            console.log(data);
			$.ajax({
    			"url": "Ajax/login/",
    			"success": function(response) {
    				if (response=="True") {
    					$("#loginerror").hide();
    					location.reload(false);
    				} else {
    					$("#loginerror").show();
    					$('#username').val("");
    					$('#password').val("");
    				}
    			},
    			"data": data,
    			"type": 'POST',
    			"cache": false,
    		});		        	
        });
        
	    $('#logouttext').click(function(e) {
			$.ajax({
    			"url": "Ajax/logout/",
    			"success": function(response) {
    				location.reload(false);
    			},
    			"data": {"logout":"yes",
    					 "csrfmiddlewaretoken": token
    					 },
    			"type": 'POST',
    			"cache": false,
    		});
	    });
	}