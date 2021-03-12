var log_url = 'http://planetlab3.rutgers.edu:10005/log';
log_url = 'http://localhost:8080/log';
//generates random id;
let guid = (cond) => {
    let s4 = () => {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }
    //return id of format #_'aaaaaaaa'
    return cond+"_"+s4() + s4();
}

var pname = "NONE"
// var DEBUGME = null;
var SESSION_LOG_DATA = [];
var noteIdCounter = 0;
var myNotes = [];

var d = new Date();
var init_time = d.getTime();

/*
var promptNoteText_1 = "A new infectious disease started a pandemic in 2009. Analysts believe that the disease started in <b>Nigeria</b> in February of 2009, and then somehow spread to Kenya, Syria, Lebanon, Pakistan, Yemen, Saudi Arabia, Iran, Venezuela, and Columbia. Cases of sickness and death later peaked in May. The intelligence division wants you to investigate whether there is a connection between <b>illegal arms dealing</b> and the <b>disease</b>." +
									"<div><br></div>" +
									"Determine how the disease spread to different countries." +
									"<div><br></div>" +
									"Describe the associations and interactions among the players in the weapons dealings.";
									// +
									// "<div><br></div>" +
									// "<span> <img src = " + "images/0.jpg" + " > </span>";  
									
var promptNoteText_2 = "Intelligence analysts are looking for information related to potential <b> terrorist activity </b>in the region." +
									"<div><br></div>" +
									"We provide you with a text corpus containing news reports. Each news report is a plain text file containing a headline, the date of publication, and the content of the article." + 
									"<div><br></div>" +
									"Potential Threats: Identify any imminent terrorist threats in the Vastopolis metropolitan area. Provide detailed information on the threat or threats (e.g. who, what, where, when, and how) so that officials can conduct counterintelligence activities. Also, provide a list of the <b> evidential documents </b> supporting your answer";
									
var prompt_none = "The following documents all relate to arms dealing between countries across the world." +
						   "<div><br></div>" +
							"Tell us your own interpretation of the dataset. " + 
							'<br/><br/><button id="button" onClick="saveInteractionsToFile()"> Click HERE to end and print results. </button>';

var prompt_conclusion = "The following documents all relate to arms dealing between countries across the world." +
							"<div><br></div>" +
							"An analyst found that mention of car parts on message boards were used to discuss weapons and their price. A man named Mikhail Dombrovski was on here with an alias to discuss with a Nigerian man. Mikhail had arranged a meeting in Dubai with him. " +
							"<div><br></div>" +
							"Tell us your own interpretation of the dataset. " + 
							'<br/><br/><button id="button" onClick="saveInteractionsToFile()"> Click HERE to end and print results. </button>';


var prompt_workflow = "The following documents all relate to arms dealing between countries across the world." +
						"<div><br></div>" +
						"An analyst first went through the email and message board intercepts section to search for some direct dialogue between the arms dealers. The analyst highlighted a code word used to deal with arm dealings. The analyst traced some aliases and found the suspects names were mentioned in other documents. The analyst started focusing solely on the activity of Mikhail Dombrovski." +
						"<div><br></div>" +
						"Tell us your own interpretation of the dataset. " + 
						'<br/><br/><button id="button" onClick="saveInteractionsToFile()"> Click HERE to end and print results. </button>';
*/
var prompt_Jeremy = "The following documents relate to arms dealing between countries across the world." +
						"<div><br></div>" +
						"A previous analyst concluded that there were two weapon transfer attempts described in these documents. The first was initiated by Nicolai and was supposed to meet at the Burj hotel in Dubai, but due to suspicious flight plans, the shipment was discovered and delayed. In accommodation of this, Nicolai hired the boat MV Tanya to deliver the weapons by boat to the middle east." +
						"<div><br></div>" +
						"Using the resources you have available, tell us your own interpretation of the dataset. " + 
						'<br/><br/><button id="button" onClick="saveInteractionsToFile()"> Click HERE to end and print results. </button>';
var prov_history_file = '../explorer/data/interactionHistories/mouseless-history.json';

var prov_Coverage_file = "../explorer/data/coverage.json";

var thisDoc = './explorer/data/documents_1.json';  //  -or- documents_1.json  -or- documents_2.json  -or- documents_2.json -or- documents_test.json	 		
 
var query = window.location.search;
var promptNoteText = '';

if(query.includes('=1')){
	pname=guid(1);
	var load_prov_history = false;
	var prov_Coverage = false;
	promptNoteText = prompt_Jeremy;
}
else if(query.includes('=2')){
	pname=guid(2);
	var load_prov_history = false;
	var prov_Coverage = true;
	promptNoteText = prompt_Jeremy;
}
else if(query.includes('=3')){
	pname=guid(3);
	var load_prov_history = true;
	var prov_Coverage = false;
	promptNoteText = prompt_Jeremy;
}
else if(query.includes('=4')){
	pname=guid("debug");
	var load_prov_history = true;
	var prov_Coverage = true;
	promptNoteText = prompt_Jeremy;
}else{
	pname=guid("err");
	var load_prov_history = false;
	var prov_Coverage = false;
	promptNoteText = "ERROR - no condition specified"
	console.log('ERROR!');
}

;(function() {
    


	var defaultUndoAction = function (){ return false; };
	var undoAction = defaultUndoAction;

	var resetUndo = function (){
		undoAction = defaultUndoAction;
	};

	var mouseX = 0;
	var mouseY = 0;	
	
	// Shortcut button 
	Mousetrap.bind('ctrl+l', function(){
		
		if(pname.length == 0){
			pname = prompt("enter tag of participant to start:");
			logData("start-study", pname, pname);
		}
		else
		{
			logData("end-study", pname, pname);
			
			alert("Study stopped logging!");
			// Now write a log for all existing notes based on note#  
			   			tempCounter = noteIdCounter;
 						
 						while (tempCounter>0){
                        var noteDialog = $(myNotes[tempCounter]); 
                        var text = noteDialog.find(".note-set").text();
                        console.log(text);
						var doc_id = noteDialog.find(".ui-dialog-title").text();
						logData("Notes", "Note" + tempCounter ,"Note" + tempCounter, doc_id,null);
						tempCounter--;
						}
		}
		
		});

	var scrunchOriginal = "original";	// code for original ID in data-id
	var scrunchedCode = "scrunched";
	var globalSearchTerm = "";
     
    //Read input JSON file 
	$.getJSON(thisDoc, function(data) {

        var jsonCounter = 0;
        var output="<div>";
        for (var i in data){
			jsonCounter++;  // document_id data[i].id
			 output +=
			//  '<div id="jsonDialog' + i + '" class="doc-set docSet" title="' + data[i].title + '" data-id="' + scrunchOriginal + '" data-source="' + data[i].type + '">' +
            // '<div class="doc-content" document_id="'+data[i].id+'">' + '</div>' +
            // '</div>';
            '<div id="jsonDialog' + i + '" class="doc-set docSet" title="' + data[i].title + '" data-id="' + scrunchOriginal + '" data-source="' + data[i].type + '">' +
            '<div class="doc-content" document_id="'+data[i].id+'">' + data[i].contents + '</div>' +
            '</div>';
            "<div><br></div>" + "<span style = float: left; margin:0 7px 50px 0; width:50px; height:50px;> <img src = images/" + jsonCounter.toString() + ".jpg> </span>"
        }
		// output += '<div onClick="saveInteractionsToFile()" id="jsonDialog' + 000 + '" class="doc-set docSet" title="' + 'END SESSION' + '" data-id="' + scrunchOriginal + '" data-source="' + 'random' + '">' +
		// '<div class="doc-content" document_id="'+000+'">' + 'Click HERE to end and print results.' + '</div>' +
		// '</div>';
        output+="</div>";
        document.getElementById("placeholder-div").innerHTML=output;

		console.log("Loaded documents from JSON: " + jsonCounter);
  	  });

	// Track mouse position
	$(document).mousemove(function(event){
		mouseX = event.pageX;
		mouseY = event.pageY;
	});
	
    
    // Writes log for interactions
    //logData("mouseenter-document-minimized", docDialog.attr("id"), docDialog.attr("id"), doc_id,text);
  	function logData(typeTag, message, element_id, document_id, text) {

		//number of milliseconds since midnight, January 1, 1970
		var d = new Date();
		var ms_timestamp = (d.getTime()-init_time)/(1000); //ms to mins
		var participant_tag = "NONE";
		if(pname.length > 0)
			participant_tag = pname;
		var jsonMessage = {
		  tags: [typeTag, document_id]   //tags: [typeTag, element_id]
		  , message: message
		  ,	timestamp: ms_timestamp
		  , type: typeTag
		 };
		 if(element_id && element_id.length > 0)
		 	jsonMessage["element_id"] = element_id; // = element_id;
		 if(document_id && document_id.length > 0)
		 	jsonMessage["document_id"] = document_id;
		 if(text && text.length > 0)
		 	jsonMessage["text"] = text;

      SESSION_LOG_DATA.push(jsonMessage);
      
      // Send the log to its destiny
	   if (log_url != 'http://localhost:8080/log') 
		  sendLogData(jsonMessage);     // if address is the localhost, don't attampt $.ajax		
		
	}//end logData


    // Sends log to assigned URL (global var) using ajax, if it's local address, just SESSION_LOG_DATA
	function sendLogData(message){
		  //SESSION_LOG_DATA.push(message);
 
		  $.ajax({
			    type: 'POST'
			  , url: log_url
			  , data: JSON.stringify(message)
			  , accepts: 'application/json'
			  , contentType: 'application/json'
			  , xhrFields: { withCredentials: false }
			  })
			  .done(function(data, status) {
			  	 //console.log('log succes: ' + data);
			  })
			  .fail(function(xhr, status, err) {
			     console.log('log failed');
			    // alert("log failed!");
			  });
	  

	}//end sendLogData

	function restoreDocFromScrunched(docDialog) {

		// start by removing existing scrunched summary div
	  	docDialog.find(".scrunch-doc").remove();

	  	// then restore id for original div
		var currentDocDiv = docDialog.find(".doc-set");
	  	currentDocDiv.attr( "id", currentDocDiv.attr("data-id"));	// restore original id
	  	currentDocDiv.attr( "data-id", scrunchOriginal);	// reset data-id code
        
       // console.log(currentDocDiv.find("id").toString());  // my test 
        
		// try to add back any removed dialog-ui classes
		currentDocDiv.addClass("ui-dialog-content ui-widget-content ui-resizable ui-dialog-normal");

		currentDocDiv.show();

		// toggle button style
  		docDialog.find(".scrunchy-button-active")
  			.removeClass("scrunchy-button-active")
  			.addClass("scrunchy-button");
	}
    // give me the dialoge, take the title&content
	function docDialogToText(element)
	{
		var ret = " ";
		ret += " " + element.find(".ui-dialog-title").text();
		ret += " " + element.find(".doc-content").text();
		return ret;
	}
	


	// write a log befre Restore (opening a doc )
	function handleDocBeforeRestore (evt) {
		var docDialog = $(evt.target).parents(".ui-dialog");
		var text = docDialogToText(docDialog);
		var doc_id = docDialog.find(".doc-content").attr("document_id");
		logData("open-document", docDialog.attr("id"), docDialog.attr("id"), doc_id,null); // error 

	/*
		var docDialog = $(evt.target).parents(".ui-dialog");
		var currentDocDiv = docDialog.find(".doc-set");

		//console.log('dataid ' + currentDocDiv.attr( "data-id"));

		if (currentDocDiv.attr( "data-id") != scrunchOriginal) {
			restoreDocFromScrunched(docDialog);
		}
	*/

	}
   
    // write a log before closing a doc  
	function handleDocBeforeCollapse(evt) {

		var docDialog = $(evt.target).parents(".ui-dialog");
		var currentDocDiv = docDialog.find(".doc-set");
		var text = docDialogToText(docDialog);
		var doc_id = docDialog.find(".doc-content").attr("document_id");
		logData("collapse-document", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
		
		// console.log('dataid ' + currentDocDiv.attr( "data-id"));

		if (currentDocDiv.attr( "data-id") != scrunchOriginal) {
			restoreDocFromScrunched(docDialog);	    //yes
			//docDialog.find(".scrunch-doc").dialogExtend("collapse");	// recursive overflow; calls before collapse
		}
	}
    
    //Scrunch the highlighted text, close the dialoge
	function scrunchHighlightView(docDialog) {

		var currentDocDiv = docDialog.find(".doc-set");	// get the doc content div
		var docCloneDiv = currentDocDiv.clone(true);	// deep copy the doc so we get all the attributes and junk(what are junks?)
	  	var scrunchedContent = currentDocDiv.find('.highlight-green');	// find highlighted stuff

	  	// only do scrunch if there is green highlighted stuff
	  	if (scrunchedContent.length != 0) {

	  		// toggle button style
	  		docDialog.find(".scrunchy-button")   // you can find it in demo.css
	  			.removeClass("scrunchy-button")
	  			.addClass("scrunchy-button-active");

	  		function highlightEntry(index, entryText) {
	  			this.index = index;
	  			this.entryText = entryText;
	  		}

	  		var entryList = [];
			var highlightSummary = "";

		  	// build summary of highlighted stuff
			for ( var i = 0; i < scrunchedContent.length; i++ ) {

			    var newEntry = '<span class="highlight-green">' + $(scrunchedContent[i]).html() + "</span><br>";

				if (highlightSummary.indexOf(newEntry) == -1) {
					highlightSummary += newEntry;	//this is just temporary to keep track of what we have
					entryList.push(new highlightEntry(currentDocDiv.text().indexOf(newEntry), newEntry));
				}
			}//end for

			highlightSummary = ""; //empty summary list so we can rebuild it in order

			// sort entries by index
		    entryList.sort(function(a,b){
		    		return (a.index > b.index);
		    	});

		    // rebuild list of entries in order
			for ( var i = 0; i < entryList.length; i++ ) {

			 	highlightSummary += entryList[i].entryText;
			    if (i < entryList.length - 1) {
			    	highlightSummary += "<br>";
			    }
			}

		  	// make changes to scrunched clone
			docCloneDiv.addClass("scrunch-doc");
			docCloneDiv.html(highlightSummary);

			// swap the doc content
			var realID = currentDocDiv.attr("id");
			currentDocDiv.attr( "data-id", realID);	// save id for later
			currentDocDiv.attr( "id", realID + "-hide");	// change id so there's only one div with that id
			docCloneDiv.attr( "id", realID);	// set the highlight clone with the original's id
			docDialog.append(docCloneDiv);

			// strip information from real div and hide
			currentDocDiv.removeClass("ui-dialog-content ui-widget-content ui-resizable ui-dialog-normal");
			currentDocDiv.hide();

			return docCloneDiv;

	  	}//--end if (scrunchedContent.length != 0)

	  	return 0;
	}//end scrunchHighlightView
    
    // re-creating scrunch view to avoid resizing problems
	function handleResizeScrunch(docDialog) {

		var scrunchDiv = docDialog.find(".scrunch-doc");

		// if in scrunched view, need to keep re-creating scrunch view to avoid resizing problems
	  	if(scrunchDiv != 0 && scrunchDiv.length != 0) {
		  	restoreDocFromScrunched(docDialog);
			scrunchHighlightView(docDialog);
		}

	}//end handleResizeScrunch
    
    // Write a log for Scrunching interaction 
	function logScrunchStuff(scrunchDiv, docDialog) {

		if(scrunchDiv != 0 && scrunchDiv.length != 0) {

			var scrunchStuff = scrunchDiv.find('.highlight-green');	// grab scrunch highlighted stuff

			if (scrunchStuff.length != 0) {
				var scrunchLog = "";
				for ( var i = 0; i < scrunchStuff.length; i++ ) {
					scrunchLog += $(scrunchStuff[i]).text() + ";;";
				}

				// console.log("LOG: " + scrunchLog); 
			 	//var text = docDialogToText(docDialog);
				//var doc_id = docDialog.find(".doc-content").attr("document_id");
				// logData("scrunch-highlight-view", scrunchLog, docDialog.attr("id"));
				var text = docDialogToText(docDialog);
				var doc_id = docDialog.find(".doc-content").attr("document_id");
				logData("scrunch-highlight-view", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
			}
		}
	}

    // What to do when you click the scrunch button 
	function handleScrunchClick($scrunchButton){

		var docDialog = $scrunchButton.parents(".ui-dialog");	// get the button's dialog box
		var currentDocDiv = docDialog.find(".doc-set");			// get the doc content div

	  	// taking advantage of fact that the dialog header is not resizable when collapsed/minimized
	  	var isOpen = false;
	  	isOpen = docDialog.hasClass("ui-resizable");

	  	if (isOpen)
	  	{
			  //todo: Convert this to expand width to 400 on open then shrink width back to 100 when done.
		  	if (currentDocDiv.attr( "data-id") == scrunchOriginal) {
				// showing original document. need to create scrunch view
				currentDocDiv.attr( "data-height", currentDocDiv.css("height"));	// save height for later
				currentDocDiv.attr( "data-width", currentDocDiv.css("width"));	// save width for later

				var scrunchDiv = scrunchHighlightView(docDialog);	// do the highlight scrunch thing

				if(scrunchDiv != 0 && scrunchDiv.length != 0)
				{
					scrunchDiv.css("height", "auto");
					scrunchDiv.dialog( "option", "height", "auto" );
					currentDocDiv.hide();

					logScrunchStuff(scrunchDiv, docDialog);
				}
			} else {
				// already in scrunched summary view; need to restore document
			  	restoreDocFromScrunched(docDialog);

			  	//reset height to saved height. resets currentDocDiv after restore
			  	currentDocDiv = docDialog.find(".doc-set");			// get the doc content div
			  	//currentDocDiv.css("height", currentDocDiv.attr( "data-height" ));
			  	//currentDocDiv.css("width", currentDocDiv.attr( "data-width" ));
			  	currentDocDiv.dialog( "option", "height", "auto" );	//works, but resizes to fit intead of restored size
			  	//currentDocDiv.dialog( "option", "height", currentDocDiv.attr( "data-height" ));
			  	// var docDialog = $(evt.target).parents(".ui-dialog");
				var docDialog = $(this);
				var text = docDialogToText(docDialog);
				var doc_id = docDialog.find(".doc-content").attr("document_id");
				logData("restore-from-scrunch", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
				// console.log("GBGB WE CARE SCRUNCH CRUNCH ");
				
				
			
			  	// logData("restore-from-scrunch", docDialog.attr("id"), docDialog.attr("id"));
			}
		}
		else
		{
			// when collapsed, clicking the scrunch button will expand the scrunch view
			currentDocDiv.dialogExtend("restore");
			var scrunchDiv = scrunchHighlightView(docDialog);

			if(scrunchDiv != 0 && scrunchDiv.length != 0)
			{
				scrunchDiv.css("height", "auto");
				scrunchDiv.dialog( "option", "height", "auto" );
				currentDocDiv.hide();

				logScrunchStuff(scrunchDiv, docDialog);
			}

		}//end if/else isOpen

	}//end handleScrunchClick
    
    // Animates the ....
	function jiggle($object, speedMilliseconds, distance) {

		var jiggleSpeed = speedMilliseconds;	//duration in milliseconds

		$object
			.animate({ "left": "-=" + distance + "px" }, jiggleSpeed )
			.animate({ "left": "+=" + distance + "px" }, jiggleSpeed )
			.animate({ "left": "+=" + distance + "px" }, jiggleSpeed )
			.animate({ "left": "-=" + distance + "px" }, jiggleSpeed );
    }

	// get selected (cursor-highlighted) text
	var cursorSelectedText = "";
	var cursorSelectedHtml = "";
	
	//Returns selected text on current window
	function getSelectionHtml() {
		var html = "";
		if (typeof window.getSelection !== "undefined") {
			var sel = window.getSelection();
			if (sel.rangeCount) {
				var container = document.createElement("div");
				for (var i = 0, len = sel.rangeCount; i < len; ++i) {
					container.appendChild(sel.getRangeAt(i).cloneContents());
				}
				html = container.innerHTML;
			}
		} else if (typeof document.selection !== "undefined") {
			if (document.selection.type == "Text") {
				html = document.selection.createRange().htmlText;
			}
		}
		return html;
		//alert(html);
	}

	// Custom case-insensitive contains method
	jQuery.expr[":"].Contains = jQuery.expr.createPseudo(function(arg) {
		return function( elem ) {
			return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
		};
	});

    // Highlighting the search term
	function searchHighlighting(searchTerm, $uiDialogBox)
	{
		// grab title and highlight its text
		var $titleSpan = $uiDialogBox.find('.ui-dialog-title');
		if (typeof $titleSpan !== "undefined") {
			$titleSpan.highlight($titleSpan.text(), "highlight-pink");
		}

		// highlight search term in body text
		var $docBody = $uiDialogBox.find('.doc-set');
		if (typeof $docBody !== "undefined") {
			$docBody.highlight(searchTerm, "highlight-pink");
		}

		//  highlight search term in note text
		var $noteBody = $uiDialogBox.find('.note-set');
		if (typeof $noteBody !== "undefined") {
			$noteBody.highlight(searchTerm, "highlight-pink");
		}
	}

	// search for searchTerm in dialog boxes and jsplumb overlay
	// highlight parts separately because highlighting within an already highlighted tag causes problems
	function search(searchTerm)
	{
		var foundSomething = false;

		if (searchTerm != "" && searchTerm != " ")
		{
			searchTerm = searchTerm.replace("<br>", "");
			searchTerm = searchTerm.replace("<b>", "");
			searchTerm = searchTerm.replace("</b>", "");

			// search without green highlighted span tags
			var re = /<span class="highlight-green">(.*?)<\/span>/g;
			var greenMatches = searchTerm.match(re);

			if (greenMatches != null){
				for (var i = 0; i < greenMatches.length; i++) {
					var stripped = greenMatches[i].replace('<span class="highlight-green">', '');
					stripped = stripped.replace('</span>', '');
					searchTerm = searchTerm.replace(greenMatches[i], stripped);
				}
			}
			globalSearchTerm = searchTerm;

			logData("search", searchTerm, "unknown");

			// remove existing search highlight
			$('.ui-dialog').removeHighlightAll("highlight-pink");
			$('._jsPlumb_overlay').removeHighlightAll("highlight-pink");

			// highlight in documents
			$( ".ui-dialog" ).each(function( index ) {
				 // $(this).attr('id','base' + counter++);

				 // if document content or title has search term, highlight whole title
				 if($(this).is(':Contains(' + searchTerm + ')')){

					// highlight the right things in the dialog box
					searchHighlighting(searchTerm, $(this));

					// jiggle dialog box
					jiggle($(this), 20, 30);

					foundSomething = true;

				 }

			});

			// highlight search term in plumb connections
			$('._jsPlumb_overlay').highlight(searchTerm, "highlight-pink");

		}//end if (searchTerm != "")

		return foundSomething;
	} //end search()

	
	// $(document).ready(
	//Some race condition exist... this is my workaound.
		
	setTimeout("big_function()", 50);    // To solve the race conditio
	
	
	big_function = (function() {
	
	console.log("DOCUMENT READY");
	
	
		// setup some defaults for jsPlumb connectors 
		var jsPlumbInstance = jsPlumb.getInstance({
			
			
			Endpoints : [ [ "Dot", { radius:7 } ], [ "Dot", { radius:5 } ] ],
  			EndpointStyles : [
    			{ fillStyle:"#225588" }, 
    			{ fillStyle:"#558822" }
    			],
			//Endpoint : ["Dot", {radius:5}],
			EndpointStyle : { fillStyle: "#567567"  },
			HoverPaintStyle : {strokeStyle:"#1e8151", lineWidth:1 },
			Anchor : [ "TopCenter", "BottomCenter" ], // "AutoDefault",
			Connector:[ "Bezier", { curviness: 15 } ], //[ "StateMachine", { curviness:20 } ],
			PaintStyle:{ strokeStyle:"#5c96bc", lineWidth:1, outlineColor:"transparent", outlineWidth:1 },  // strok "#5c96bc"   // color transparent
			DragOptions : { cursor: "crosshair" },
			Container:"main-div"
		});
 
		// determine position for dialog boxes based on doc type categories
		var docTypeList = [];
		function docTypeRecord(typeName){
			this.type = typeName;
			this.count = 0;
		}

		var groupingWidth = 100;  // was 235
		var groupingHeight = 40;

		// use content divs loaded from json to create the dialog boxes
		$( ".docSet" ).each(function( index ){
			var typeValue = $(this).attr("data-source"); // doc type saved under data-source
			var typeIndex = -1;							 // default index if not found in docType list
			var boxPosY = 0;							 // default to top

			// get index of type in typeList, maintain count of how many of each type. use type count for positioning
			for (var i = 0; i < docTypeList.length; i++){
				if (docTypeList[i].type == typeValue){
					docTypeList[i].count++;
					boxPosY = groupingHeight * docTypeList[i].count;
					typeIndex = i;
					//console.log('type ' + typeValue + ' ' + i);
				}
			}

			// if not in array, add it.
			// push returns the new array length, which we use to get the index of the added item
			if (typeIndex == -1){
				typeIndex = docTypeList.push(new docTypeRecord(typeValue))  - 1;
			}
			
			// create all dialog boxes
			var doccc = $(this).dialog(
				{
				minHeight: 400,
				width: 400,
				dialogClass: "close",  // "dlg-no-close"
			 	closeOnEscape: false,
			 	drag: function(event, ui){ jsPlumbInstance.repaintEverything(); },
			 	mouseenter: function(event,ui){console.log("mouse entered");},
			 	dragStart: function(event, ui) { 
			 			//console.log("drag started...");
			 			//console.log(event);
			 			//console.log(ui);
			 			////logData("newConnection", info.connection.sourceId + "," + info.connection.targetId, info.connection.sourceId);
			 			var docDialog = $(event.target).parents(".ui-dialog");
						//// logData("startdrag-document", docDialog.attr("id"), docDialog.attr("id")); 
						
						var text = docDialogToText(docDialog);
						var doc_id = docDialog.find(".doc-content").attr("document_id");
						logData("startdrag-document", docDialog.attr("id"), docDialog.attr("id") , doc_id,null);
			 		},
			 		
			 		dragStop: function() { 
			 			//console.log(event.clientX);
			 			//console.log(event.clientY);
			 			//console.log(event);
			 			//console.log(ui);
			 			////logData("newConnection", info.connection.sourceId + "," + info.connection.targetId, info.connection.sourceId);
			 			var docDialog = $(this); // $(event.target).parents(".ui-dialog");
			 			var text = docDialogToText(docDialog);
						var doc_id = docDialog.find(".doc-content").attr("document_id");
						logData("enddrag-document", docDialog.attr("id"), docDialog.attr("id"), doc_id, null);
					//// logData("enddrag-document", docDialog.attr("id"), docDialog.attr("id")); 
						//// logData("enddrag-document", docDialog.attr("id"), docDialog.attr("id")); 
					//// logData("enddrag-document", docDialog.attr("id"), docDialog.attr("id")); 
						//// logData("enddrag-document", docDialog.attr("id"), docDialog.attr("id")); 
					//// logData("enddrag-document", docDialog.attr("id"), docDialog.attr("id")); 
			 		},
		
             	resize: function(event, ui){
             		handleResizeScrunch($(event.target).parents(".ui-dialog"));
             		jsPlumbInstance.repaintEverything();
             	},
             	//width: 1000,
             	//load : function(evt, dlg) { $(evt.target).dialogExtend("collapse"),	// ?? start boxes collapsed
				position: [typeIndex * groupingWidth, boxPosY]   // Initial position of dialog box 
           })  // end each box 
           
			.resizable({handles: {'s': 'handle'}})
			.dialogExtend(
				{
	        	"maximizable" : false,
	        	"closable" : false,
	        	"collapsable" : true,
	        	"dblclick" : "collapse",
				"load" : function(evt, dlg) { $(evt.target).dialogExtend("collapse"); }	// ?? start boxes collapsed
      			});
				 
				$(this).dialog(  // Resize and reposition dialogs after loading
				{
				width: 100,
				minHeight: 500,
				position: [typeIndex * groupingWidth, boxPosY]   // Initial position of dialog box 
				}); 
				
				//.dialogExtend(
				//{
				$(this).dialogExtend("collapse");  // Collapse all dialoges after sceond resize
				//});
		}); //end $( ".docSet" ).each -- each dialog
		
		//For mouse overs
		
		
	  	
	  	
		$("div.ui-dialog").bind("mouseenter",function(){ // event,ui){  // $("div[role='dialog']").bind("mouseenter",function(event,ui){
			
			 			var docDialog = $(this);//.parents(".ui-dialog");
			 			
			 			if(docDialog.attr("id") == null)
			 			{
			 				docDialog = $(this.target);//.parents(".ui-dialog");
			 				console.log(docDialog );
			 				return;
			 			}
			 		    //Write this log only if the window was open  // taking advantage of fact that the dialog header is not resizable when collapsed/minimized
	  				if (docDialog.hasClass("ui-resizable")){
			 			// logData("mouseenter-document", docDialog.attr("id"), docDialog.attr("id")); 
			 			var text = docDialogToText(docDialog);
						var doc_id = docDialog.find(".doc-content").attr("document_id");
						logData("mouseenter-document", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
					//	console.log("mouseenter-document");
			 		}else{
			 		//Write this log only if the window was minimized  // taking advantage of fact that the dialog header is not resizable when collapsed/minimized
	  				//if (docDialog.hasClass("ui-resizable") == false){
			 			var text = docDialogToText(docDialog);
						var doc_id = docDialog.find(".doc-content").attr("document_id");
						logData("mouseenter-document-minimized", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
					//	console.log("mouseenter-document-minimized");  // var doc_id = docDialog.find(".doc-content").attr("document_id");
			 		}
			
			
			});
			
		$("div[role='dialog']").bind("mouseleave",function(){  // $("div[role='dialog']").bind("mouseexit",function(event,ui){
			
		     	 // console.log("mouose enter...");
			 			// console.log(event);
			 			// console.log(ui);
			 			var docDialog = $(this); //$(event.target);//.parents(".ui-dialog");
			 			if(docDialog.attr("id") == null)
			 			{
			 				// console.log("THOU SHALT NOT LOG!!!");
			 				return;
			 			}
			 			//Write log only if the window was open 
	  				if (docDialog.hasClass("ui-resizable")){			 			 
			 			var text = docDialogToText(docDialog);
						var doc_id = docDialog.find(".doc-content").attr("document_id");
						logData("mouseexit-document", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
					//		console.log("mouseenter-leave");
			 		}else{
			 			
			 			var text = docDialogToText(docDialog);
						var doc_id = docDialog.find(".doc-content").attr("document_id");
						logData("mouseexit-document-minimized", docDialog.attr("id"), docDialog.attr("id"), doc_id,null);
					//	console.log("mouseenter-leave-mini");
			 		}
			
			
			});
		
		// give dialog boxes unique id attributes. this is necessary for jsplumb connections
		var counter = 0;
		$( ".ui-dialog" ).each(function( index ) {
		  $(this).attr('id','dialog' + counter++);
		});


		$( ".doc-set" ).each(function( index ) {

		  //$(this).dialogExtend("collapse");	// now collapsing on load

		  // repaint connection lines on collapse/restore
		  $(this).bind("dialogextendrestore", function(evt) { jsPlumbInstance.repaintEverything(); });
		  $(this).bind("dialogextendcollapse", function(evt) { jsPlumbInstance.repaintEverything(); });
		  $(this).bind("dialogextendbeforecollapse", function(evt, dlg) { handleDocBeforeCollapse(evt); });
		  $(this).bind("dialogextendbeforerestore", function(evt, dlg) { handleDocBeforeRestore(evt); });
		  $(this).bind("dragend",function(){console.log("Stopped");});
		  
		});

		var plumbHandleHtml = "<a href='#' class='ep title-handle ui-corner-all ui-icon ui-icon-bullet' role='button' style='position: relative;  margin: 3px;'></a>";
		$(".ui-dialog-titlebar-buttonpane").append( plumbHandleHtml );

		var scrunchButHtml = "<a href='#' class='scrunchy-button ui-corner-all ui-icon ui-icon-lightbulb' role='button' style='position: relative;  margin: 3px;'></a>";
		$(".ui-dialog-titlebar-buttonpane").append( scrunchButHtml );

		$(".scrunchy-button").click( function() {

		  	handleScrunchClick($(this));

		});//end scrunchy click

		var windows = $(".ui-dialog");	// this is used somewhere below

		// limit connections
		jsPlumbInstance.bind("beforeDrop", function(c) {

			// don't allow connecting object to self
            if (c.sourceId == c.targetId)
           	{
                return false;
            }

            // don't allow multiple of the same connections (can't connect A to B multiple times)
            var connectionList = jsPlumbInstance.getConnections({source:[c.sourceId, c.targetId], target:[c.sourceId, c.targetId]}, true);
			if(connectionList != "")
            {
				return false;
        	}

           	return true;
        });

		// bind a connection listener. note that the parameter passed to this function contains more than
		// just the new connection - see the documentation for a full list of what is included in 'info'.
		// this listener sets the connection's internal
		// id as the label overlay's text.
        jsPlumbInstance.bind("connection", function(info) {

        	//console.log("overlay: " + info.connection.getOverlay("customOverlay").id);
        	//console.log("connection: " + info);

        	info.connection.addOverlay(["Custom", {
	                create:function(component) {
	                    //return $("<textarea class='connection-textarea' data-source='" + info.connection.sourceId + "' data-target='" + info.connection.targetId + "'>connected</textarea>");
	                    return $("<div class='connection-textarea' data-source='" + info.connection.sourceId + "' data-target='" + info.connection.targetId + "' contenteditable='true'>connected</div>");
	                },
	                location:0.7,
	                id:"customOverlay",
	                class:"custom-connection-label",
					events:{
						"click":function(label, evt){
								$(".body-class").contextMenu("hide");
							}
						}
	                }
	            ]);

        	resetUndo();
        	
        	// var docDialog = $(evt.target).parents(".ui-dialog");
			// var text = docDialogToText(docDialog);
			// var doc_id = docDialog.find(".doc-content").attr("document_id");
			// logData("open-document", docDialog.attr("id"), docDialog.attr("id"), doc_id,text);
			
			var docDialog1 = $("#"+info.connection.sourceId);
			var docDialog2 = $("#"+info.connection.targetId);
			var text = docDialogToText(docDialog1) + ' \n ' + docDialogToText(docDialog2);
			// console.log(docDialog);
			// console.log("that's all folks");
			var doubleid = info.connection.sourceId + "," + info.connection.targetId;
						
			if (docDialog2.find(".doc-content").attr("document_id") != null){
			   var doubleDocId = docDialog1.find(".doc-content").attr("document_id")+","+docDialog2.find(".doc-content").attr("document_id");
			}
			else{
					    var noteDialog = $(info.connection.target); 
     					var doc_id = noteDialog.find(".ui-dialog-title").text();
						console.log(doc_id);
			            var doubleDocId = docDialog1.find(".doc-content").attr("document_id")+","+doc_id;
			}
			
			logData("newConnection", doubleid, doubleid, doubleDocId  , null);

        });

		// suspend drawing and initialise.
		jsPlumbInstance.doWhileSuspended(function() {

			// make each ".ep" div a source and give it some parameters to work with.  here we tell it
			// to use a dynamic anchor and the StateMachine connectors, and also we give it the
			// connector's paint style.  note that in this demo the strokeStyle is dynamically generated,
			// which prevents us from just setting a jsPlumb.Defaults.PaintStyle.  but that is what i
			// would recommend you do. Note also here that we use the 'filter' option to tell jsPlumb
			// which parts of the element should actually respond to a drag start.
			jsPlumbInstance.makeSource(windows, {
				filter:".ep"				// only supported by jquery
			});

			// initialise all documents as connection targets.
	        jsPlumbInstance.makeTarget(windows);


		});

        // Creating a note 
		
		var createNote = function (noteHtml) {

			noteIdCounter++;
            
			var noteId = "note-id-" + noteIdCounter;

			// first append note placeholder content to the document

			var output="<div>";
			
			// different title for initial note and all other
             if (noteHtml !== promptNoteText){
             	
  	 	            	output += '<div id="' + noteId + '" class="note-set" title=" MyNotes '+ (noteIdCounter - 1)+'" contenteditable="true">' +
						noteHtml +
						// '<span style = float: left; margin:0 7px 50px 0; width:50px; height:50px;> <img src = "images/11.bmp"> </span>' +
	            	  '</div>';
	            	  
	        output+="</div>";
	        }
	        else{
	        
			output += '<div id="' + noteId + '" class="note-set" title=" Prompt Note  " contenteditable="false">' +
						noteHtml +
						// '<span style = float: left; margin:0 7px 50px 0; width:50px; height:50px;> <img src = "images/11.bmp"> </span>' +
						
	            	  '</div>';
	            	  
	        output+="</div>";
	        	
	        };
  
            //logData("createNote", noteId + "," + mouseX + "," + mouseY, noteId);
             
						logData("createNote", noteId,"Note" + (noteIdCounter -1), [ mouseX, mouseY ]);
             
             
			// need a div to base the dialog box off of. creating a new dialog box doesn't
			// depend on the placeholder after it's created, so it's ok to rewrite whatever was in there
	        document.getElementById("placeholder-div").innerHTML = output;
             
	        // then make new note div a dialog box
	        var noteDialog = $( "#" + noteId )
				.dialog(	
					{
					minHeight: 80,
					dialogClass: "dlg-no-close",
				 	closeOnEscape: false,
					position: [mouseX, mouseY],
				 	drag: function(event, ui){ jsPlumbInstance.repaintEverything(); },
	             	resize: function(event, ui){ jsPlumbInstance.repaintEverything(); }
	            	})
				.resizable({handles: {'s': 'handle'}})
				.dialogExtend(
					{
		        	"maximizable" : false,
		        	"closable" : false,
		        	"collapsable" : false
		        	//, "dblclick" : "collapse",
	      			});

			undoAction = function(){
				noteDialog.dialog('destroy').remove();
			};

			var noteDialogParent = noteDialog.parent();

			// set up jsPlumb stuff for note
			jsPlumbInstance.doWhileSuspended(function() {

				jsPlumbInstance.makeSource(noteDialogParent, {
					filter:".ep_note"
				});

				// initialise all documents as connection targets.
		        jsPlumbInstance.makeTarget(noteDialogParent);

				//console.log("selected: " + noteDialogParent.attr('id') + ", " + noteDialogParent.attr('class') );
			    myNotes[noteIdCounter] = noteDialogParent;
			    //console.log(myNotes[noteIdCounter]);	
				// noteDialogParent.find(".ui-dialog-titlebar-buttonpane").append( plumbHandleHtml );
			});

			// hide context menu when click on note to edit it
			noteDialogParent.find(".note-set").click(function() {
			  $(".body-class").contextMenu("hide");
			});
            
            
			return noteDialog;

		};// end create note dialog

		async function generateHistory(fileName){
			// let pickles = null;
			let output='<div id="provSummary" class="prov-set" title=" History" contenteditable="false"><ul>';
			await $.getJSON(fileName, function(data){
				for (var i in data) {
					if (data[i].type == "search"){
						output += "<li class='searchText'>" + data[i].message + "</li><br/>"
					} else if(data[i].type == "highlightText"){
						output += "<li class='highlightText'>" + data[i].message + "</li><br/>"
					}
				}
			}).done(()=>{
				output += "</ul></div>"
				document.getElementById("placeholder-div").innerHTML=output;
		
				var provDialog = $( "#provSummary" )
						.dialog(	
							{
							height: 400,
							 closeOnEscape: false,
							 drag: function(event, ui){ jsPlumbInstance.repaintEverything(); },
							 resize: function(event, ui){ jsPlumbInstance.repaintEverything(); },
							 position: [mouseX+400, mouseY]

							})
						.resizable({handles: {'s': 'handle'}})
						.dialogExtend(
							{
							"maximizable" : false,
							"closable" : false,
							"collapsable" : true,
							"dblclick" : "collapse",
							  });
		
					// set up jsPlumb stuff for note
					var provDialogParent = provDialog.parent();
					jsPlumbInstance.doWhileSuspended(function() {
						jsPlumbInstance.makeSource(provDialogParent, {
							filter:".ep_prov"
						});
						// initialise all documents as connection targets.
						jsPlumbInstance.makeTarget(provDialogParent);
					});
		
					// hide context menu when click on note to edit it
					provDialogParent.find(".prov-set").click(function() {
					  $(".body-class").contextMenu("hide");
					});
					return provDialog;
			})
			// $.ajax(
			// 	{
			// 		dataType:'json',
			// 		url: fileName,
			// 		data: pickles,
			// 		async: false}
					
			// 	).success(function(pickles) {
		
			// 			var jsonCounter = 0;
			// 			for (var i in pickles){
			// 				console.log(pickles[i].type)
			// 				jsonCounter++;
			// 				if (pickles[i].type == "search"){
			// 					console.log("here")
			// 					output += "<div class='search'>" + pickles[i].text + "</div>"
		
			// 				} else if(pickles[i].type == "highlightText"){
			// 					output += pickles[i].text + "Hilight!"
		
			// 				} else{
			// 					output += pickles[i]
			// 				}
			// 				//  output +=
			// 				// '<div id="jsonDialog' + i + '" class="doc-set docSet" title="' + data[i].title + '" data-id="' + scrunchOriginal + '" data-source="' + data[i].type + '">' +
			// 				// '<div class="doc-content" document_id="'+data[i].id+'">' + data[i].contents + '</div>' +
			// 				// '</div>';
			// 				// "<div><br></div>" + "<span style = float: left; margin:0 7px 50px 0; width:50px; height:50px;> <img src = images/" + jsonCounter.toString() + ".jpg> </span>"
			// 			}
			// 			// output += '<div onClick="saveInteractionsToFile()" id="jsonDialog' + 000 + '" class="doc-set docSet" title="' + 'END SESSION' + '" data-id="' + scrunchOriginal + '" data-source="' + 'random' + '">' +
			// 			// '<div class="doc-content" document_id="'+000+'">' + 'Click HERE to end and print results.' + '</div>' +
			// 			// '</div>';
			// 			console.log(output)
			// 			output+="</div>";
						
			// 			console.log("JSON loaded, analyst's interaction count: " + jsonCounter);
			// 		}).error(function(pickles){
			// 			console.error("I'm worthless", pickles)
			// 		}).complete(function(){
			// 			document.getElementById("placeholder-div").innerHTML=output;
			// 			return output;
			// 		});
			//return new Promise(resolve => {output});
		}
		
		// Creating a Provenance Representation 
		// Generate coverage Representation
		async function generateCoverage(fileName){
						let output='<div id="provSummary" class="prov-set body-class" title="Coverage" contenteditable="false"><ul>';
						await $.getJSON(fileName, function(data){
							for (var i in data) {
								if(data[i][1] > .4){
									output += "<li class='cov-line'><span> "+data[i][0]+"</span><div class='cov-bg'><div class='cov-fg' style='width: "+data[i][1]*160+"px' ></div></div> </li>"
								}
							}
						}).done(()=>{
							output += "</ul></div>"
							document.getElementById("placeholder-div").innerHTML=output;
					
							var provDialog = $( "#provSummary" )
									.dialog(	
										{
										height: 440,
										width: 225,										 closeOnEscape: false,
										 drag: function(event, ui){ jsPlumbInstance.repaintEverything(); },
										 resize: function(event, ui){ jsPlumbInstance.repaintEverything(); },
										 position: [mouseX+450, mouseY+120]
			
										})
									.resizable({handles: {'s': 'handle'}})
									.dialogExtend(
										{
										"maximizable" : false,
										"closable" : false,
										"collapsable" : true,
										"dblclick" : "collapse",
										  });
								// set up jsPlumb stuff for note
								var provDialogParent = provDialog.parent();
								jsPlumbInstance.doWhileSuspended(function() {
									jsPlumbInstance.makeSource(provDialogParent, {
										filter:".ep_prov"
									});
									// initialise all documents as connection targets.
									jsPlumbInstance.makeTarget(provDialogParent);
								});
					
								// hide context menu when click on note to edit it
								provDialogParent.find(".prov-set").click(function() {
								  $(".body-class").contextMenu("hide");
								});
								return provDialog;
						})
		}


		// right click menu for dialog boxes
		$.contextMenu({
	        selector: '.ui-dialog',
	        autoHide: true,
	        callback: function(key, options) {
	        	var docDialog = options.$trigger;
				var currentDocDiv = docDialog.find(".doc-set");	// get the doc content div
				var pinkContent = currentDocDiv.find('.highlight-pink');	// find search stuff

				//console.log("CURSOR SELECTED TEXT: " + cursorSelectedText);
				//console.log("CURSOR SELECTED HTML: " + cursorSelectedHtml);

				var clearSearchHighlightFromSelection = function () {
					docDialog.removeHighlightSelection(cursorSelectedHtml, "highlight-pink");

					// cut out pink highlighted span tags
					var re = /<span class="highlight-pink">(.*?)<\/span>/g;
					var pinkMatches = cursorSelectedHtml.match(re);

					if (pinkMatches != null){

						for (var i = 0; i < pinkMatches.length; i++) {
							//console.log("match " + i + ": " + pinkMatches[i]);
							var stripped = pinkMatches[i].replace('<span class="highlight-pink">', '');
							stripped = stripped.replace('</span>', '');
							//console.log("stripped " + i + ": " + stripped);
							cursorSelectedHtml = cursorSelectedHtml.replace(pinkMatches[i], stripped);
						}
					}
				};

				// then do the green highlighting
				if (key == "highlight") {
					//options.$trigger.attr("id")

					// first, need to unhighlight the pink search highlight in the selection

					// if there is pink highlight, remove it and cut it out of the selection html
					if (pinkContent.length != 0) {
						clearSearchHighlightFromSelection();
					}//end if pinkContent.length != 0


					// then, do green highlighting
					var splitHtml = cursorSelectedHtml.split("<br>");	// break into pieces by line breaks

					for (var i = 0; i < splitHtml.length; i++) {
						var highStuff = splitHtml[i].trim();

						if (highStuff != "") {
							docDialog.highlight( splitHtml[i], "highlight-green");
						}
					}

					logData("highlightText", cursorSelectedText, docDialog.attr("id"));

					// then restore the pink search highlighting
					if (pinkContent.length != 0) {
						searchHighlighting(globalSearchTerm, docDialog);
					}


				} else if (key == "unhighlight") {
					logData("unhighlight", cursorSelectedText, docDialog.attr("id"));

					// first, clear any pink content, if necessary
					// first, need to unhighlight the pink search highlight in the selection

					var pinkContent = currentDocDiv.find('.highlight-pink');	// find search stuff

										// if there is pink highlight, remove it and cut it out of the selection html
					if (pinkContent.length != 0) {
						clearSearchHighlightFromSelection();
					}//end if

					// then remove green highlight
					docDialog.removeHighlightSelection(cursorSelectedHtml, "highlight-green");

					// then restore the pink search highlighting
					if (pinkContent.length != 0) {
						searchHighlighting(globalSearchTerm, docDialog);
					}

				} else if (key == "selectSearch") {
					search(cursorSelectedHtml.trim());
				} else if (key == "clearSearch") {
					// remove existing search highlight
					$('.ui-dialog').removeHighlightAll("highlight-pink");
					$('._jsPlumb_overlay').removeHighlightAll("highlight-pink");
				}
	        },
	        items: {
	            "selectSearch": {name: "Search for selected", icon: "search"},
				"clearSearch": {name: "Clear Search", icon: "clear-search"},
	            "sep1": "---------",
	            "highlight": {name: "Highlight", icon: "edit"},
	            "unhighlight": {name: "Clear Highlight", icon: "delete"}
	        },
			events: {
				show: function(opt) {
					cursorSelectedHtml = getSelectionHtml();
					cursorSelectedText = window.getSelection().toString();

					if (cursorSelectedHtml == " " || cursorSelectedHtml == "  ") {
						cursorSelectedHtml = "";
					}
				},
				hide: function(opt) {
					cursorSelectedHtml = "";
					cursorSelectedText = "";
				}
			}
	    });

		// right click menu for jsplumb connectors
	    $.contextMenu({
	    	// _jsplumb_c_
	        selector: '._jsPlumb_overlay',
	        autoHide: true,
	        zIndex: 5000,
	        callback: function(key, options) {
	            //console.log("click: " + options.$trigger.attr("id"));
	            //console.log("click: " + key);

	            if (key == "delete")
	            {
	            	var sourceId = options.$trigger.attr("data-source");
	            	var targetId = options.$trigger.attr("data-target");
	            	var overlayText = options.$trigger.html();

	            	// get the connection by the source and target info saved in the overlay
		            var connList = jsPlumbInstance.getConnections({
					      source: sourceId,
					      target: targetId
					});
					//console.log("conn: " + connList[0].sourceId);

		            if (connList != null)
					{
		            	// delete connection and annotation
		            	jsPlumbInstance.detach(connList[0]);

		            	// set action for undo command
		            	undoAction = function(){
		            		var c = jsPlumbInstance.connect({
							    source: sourceId,
							    target: targetId
							});

							c.addOverlay(["Custom", {
				                create:function(component) {
				                    //return $("<textarea data-source='" + sourceId + "' data-target='" + targetId + "'>" + overlayText + "</textarea>");
				                    return $("<div class='connection-textarea' data-source='" + sourceId + "' data-target='" + targetId + "' contenteditable='true'>" + overlayText + "</div>");
				                },
				                location:0.7,
				                id:"customOverlay",
				                class:"custom-connection-label"
				                }
				            ]);
		            	};
		            }
	        	}
	        },
	        items: {
	            "delete": {name: "Delete connection", icon: "delete"}
	        }
	    });

		// right click menu for background
		$.contextMenu({
	        selector: '.body-class',
	        zIndex: 5000,
	        callback: function(key, options) {
	            var m = "clicked: " + key;

	            if (key == "new-note") {
	            	createNote("");
	            }
				else if (key == "clearSearch") {
					// remove existing search highlight
					$('.ui-dialog').removeHighlightAll("highlight-pink");
					$('._jsPlumb_overlay').removeHighlightAll("highlight-pink");
				}

	        },
	        items: {
	            "search": { name: "Search", icon: "search", type: 'text', value: "",
					events: {keyup: function(e) {

							var searchInput = $( "input[name='context-menu-input-search']" );
							searchInput.css("color", "black");

							//console.log("id: " + searchInput.attr("id"));

							if (e.keyCode == 13){
								// pressed enter

								var foundFlag = search(searchInput.val());

								if (!foundFlag) {
									searchInput.css("color", "red");
									jiggle($(".context-menu-list"), 5, 10);
								}
							}
						}
					}
				},
				"clearSearch": {name: "Clear Search", icon: "clear-search"},
				"sep1": "---------",
				"new-note": {name: "New note", icon: "add"}
	        },
			events: {
				show: function(opt) {
					// load states from data store to fill input with last search
					var $this = this;
					$.contextMenu.setInputValues(opt, $this.data());
				},
				hide: function(opt) {
					// save input search term for next context box
					var $this = this;
					$.contextMenu.getInputValues(opt, $this.data());
				}
			}
	    });

		// Add prompt note on initialization
		mouseX = 550; //$(window).width() - 700;
		mouseY = 80; // $(window).height() - 300;
		
		//var promptNote = createNote("A new infectious disease started a pandemic in 2009. Analysts believe that the disease started in <b>Nigeria</b> in February of 2009, and then somehow spread to Kenya, Syria, Lebanon, Pakistan, Yemen, Saudi Arabia, Iran, Venezuela, and Columbia. Cases of sickness and death later peaked in May. The intelligence division wants you to investigate whether there is a connection between <b>illegal arms dealing</b> and the <b>disease</b>." +
		//							"<div><br></div>" +
		//							"Determine how the disease spread to different countries." +
		//							"<div><br></div>" +
		//							"Describe the associations and interactions among the players in the weapons dealings." +
		//							"<div><br></div>");

		var promptNote = createNote(promptNoteText);

		if(load_prov_history){
			generateHistory(prov_history_file)
		}
		if (prov_Coverage){
			generateCoverage(prov_Coverage_file)
		}

		promptNote.parent().width(400);
	

	});    //end jsPlumb.ready end the  big function 

  
    // Undo Action shortcut
	Mousetrap.bind('alt+shift+z', function(e) {
	    undoAction();
	    resetUndo();
	});
    //  Another shortcut  
	Mousetrap.bind('alt+shift+k', function(e) {
	   	var htmlDump = "<html>" + document.getElementById("the-html").innerHTML + "</html>";
	   	logData("htmlDump", htmlDump, "global");
		//$('.ui-dialog').removeHighlightAll("highlight-pink");
	    $('.doc-set').css({ "color": "transparent"});			// hide the body text
	    $('.ui-dialog').find('span').css({ "color": "black"});	// show the highlighted text
	   	$('.context-menu-list').attr('style','display: none;'); // hide all context menus
	    console.log("K Hide: Moderate detail");
	});
    //  Another shortcut
	Mousetrap.bind('alt+shift+l', function(e) {

		var htmlDump = "<html>" + document.getElementById("the-html").innerHTML + "</html>";
	   	logData("htmlDump", htmlDump, "global");

	   	//$('.ui-dialog').removeHighlightAll("highlight-pink");

	    // hide all the text!
	    var docTitle = $('.ui-dialog-title');
	    //docTitle.css({ opacity: 0 });	// hides entire span (text and highlight)
	    $('.ui-dialog-title').css({ "color": "transparent"});	// hide the title text
	    $('.doc-set').css({ "color": "transparent"});			// hide the body text
		$('.note-set').css({ "color": "transparent"});			// hide the note text
		$('.note-textarea').val("");							// remove all note text
		$('._jsPlumb_overlay').css({ "color": "transparent"});	// hide the connection text
	   	$('.context-menu-list').attr('style','display: none;'); // hide all context menus

	   	// undoes K Hide so that L Hide works right even after K Hide
	   	$('.ui-dialog').find('span').css({ "color": "transparent"});	// show the highlighted text

	   	console.log("L Hide: Low detail");
	});

	//console.log("window height: " + $(window).height());

})();

function saveInteractionsToFile()
{
	function encode(s) 
{
    var out = [];
    for ( var i = 0; i < s.length; i++ ) {
        out[i] = s.charCodeAt(i);
    }
    return new Uint8Array( out );
	}
	function determineBrowser(usrAgnt){
		let sBrowser =""

		// The order matters here, and this may report false positives for unlisted browsers.
		
		if (sUsrAg.indexOf("Firefox") > -1) {
		sBrowser = "Mozilla Firefox";
		// "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"
		} else if (sUsrAg.indexOf("SamsungBrowser") > -1) {
		sBrowser = "Samsung Internet";
		// "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-G955F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/9.4 Chrome/67.0.3396.87 Mobile Safari/537.36
		} else if (sUsrAg.indexOf("Opera") > -1 || sUsrAg.indexOf("OPR") > -1) {
		sBrowser = "Opera";
		// "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 OPR/57.0.3098.106"
		} else if (sUsrAg.indexOf("Trident") > -1) {
		sBrowser = "Microsoft Internet Explorer";
		// "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; Zoom 3.6.0; wbx 1.0.0; rv:11.0) like Gecko"
		} else if (sUsrAg.indexOf("Edge") > -1) {
		sBrowser = "Microsoft Edge";
		// "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
		} else if (sUsrAg.indexOf("Chrome") > -1) {
		sBrowser = "Google Chrome or Chromium";
		// "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/66.0.3359.181 Chrome/66.0.3359.181 Safari/537.36"
		} else if (sUsrAg.indexOf("Safari") > -1) {
		sBrowser = "Apple Safari";
		// "Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1 980x1306"
		} else {
		sBrowser = "unknown";
		}
		return sBrowser;
	}

	let d = new Date();
	let ms_timestamp = (d.getTime()-init_time)/(1000);
	let sUsrAg = navigator.userAgent;
	

	//Create the-end object
	let jsonEnd = {
		tags: ["end-study",null],
		message: pname,
		timestamp: ms_timestamp,
		type: "endStudy",
		element_id: {
			windowSize:[window.innerWidth,window.innerHeight], //Size of tje view port they did the study in
			monitorResolution: [window.screen.width, window.screen.height], //The resolution ie pixels of the monitor they dod the study on
			availResolution: [window.screen.availWidth, window.screen.availHeight], //the size of the screen that they could expand the window into.
			pixelRatio: window.devicePixelRatio, //Ratio of css pixels to physical pixels. 1 would be 100% zoom 2 would be retina displays.
			zoom: (window.devicePixelRatio>1)? (window.devicePixelRatio)*100: window.devicePixelRatio*100,
			browser: determineBrowser(sUsrAg), //Browser name given the userAgent String
			userAgent: sUsrAg //Default user agent String
		}
	}
	SESSION_LOG_DATA.push(jsonEnd);
			
	// Now write a log for all the notes with their written content	
	for (tempCounter = 2; tempCounter <= noteIdCounter ;tempCounter ++){
		var noteDialog = $(myNotes[tempCounter]); 
		var noteContent = noteDialog.find(".note-set").text();
		var doc_id = noteDialog.find(".ui-dialog-title").text();
		let noteInfo = {
			tags: ["Notes", doc_id],
			message: noteContent,
			timestamp: ms_timestamp,
			type: "note-finish",
			participant_tag: pname,
			element_id: "Note"+(tempCounter-1)
		}
		SESSION_LOG_DATA.push(noteInfo)
	}

	var doc = JSON.stringify(SESSION_LOG_DATA);
	var data = encode(doc);
	var blob = new Blob( [ data ], {
        type: 'application/octet-stream'
	});
    
    url = URL.createObjectURL( blob );
    var link = document.createElement( 'a' );
    link.setAttribute( 'href', url );
    link.setAttribute('download', pname+'_interactions.json' );
    
    var event = document.createEvent( 'MouseEvents' );
    event.initMouseEvent( 'click', true, true, window, 1, 0, 0, 0, 0, false, false, false, false, 0, null);
    link.dispatchEvent(event);
}