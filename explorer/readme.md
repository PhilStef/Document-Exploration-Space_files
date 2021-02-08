# Document Explorer
Document Explorer is an application for opening and organizing small documents in a visual spatial workspace.


##Usage
To use this, copy this folder and serve it using a web server, e.g. Apache. index.html uses information from a subset of the VAST challenge. Once started, the application loads documents from [documents.json](../../../../vislda/blob/master/tool/documents.json)

1. Edit [main.js](../../../../vislda/blob/master/tool/main.js) to set "log_url" the log service endpoint (defaults to localhost:8080).
2. Start the python log service in [plog](../../../../vislda/blob/master/tool/plog/) by running "python log_to_file.py". This starts the server on localhost:8080 and saves to output.json by default.
3. Open the served index.html in a Chrome browser.
4. If running a study, press hotkey "ctrl-l" to include the participant ID in log messages and create a "start" log entry. Press "ctrl-l" again, after continued use, to trigger a "stop" log entry.
5. View the log output to ensure it is working correctly.


## ISSUES
* There seems to be race condition. I suspect that it has to do with how jsPlumb is used.
* Log messages include ID of dialogue boxes, rather than the ID of documents.
* Right now, Document Explorer will report an error when the logging service is not started. This is good for ensuring logs are properly recorded. 
