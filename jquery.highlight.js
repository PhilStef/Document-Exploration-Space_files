/*
MODIFIED FROM THIS VERSION -ER
-added highlightStyle parameter to you can add/remove multiple highlight styles


highlight v4

Highlights arbitrary terms.

<http://johannburkard.de/blog/programming/javascript/highlight-javascript-text-higlighting-jquery-plugin.html>

MIT license.

Johann Burkard
<http://johannburkard.de>
<mailto:jb@eaio.com>

*/

jQuery.fn.highlight = function(pat, highlightStyle) {
	function innerHighlight(node, pat) {
		  var skip = 0;
		  if (node.nodeType == 3) {
		   var pos = node.data.toUpperCase().indexOf(pat);
		   if (pos >= 0) {
			var spannode = document.createElement('span');
			spannode.className = highlightStyle;
			var middlebit = node.splitText(pos);
			var endbit = middlebit.splitText(pat.length);
			var middleclone = middlebit.cloneNode(true);
			spannode.appendChild(middleclone);
			middlebit.parentNode.replaceChild(spannode, middlebit);
			skip = 1;
		   }
		  }
		  else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
		   for (var i = 0; i < node.childNodes.length; ++i) {
			i += innerHighlight(node.childNodes[i], pat);
		   }
		  }
		  return skip;
	}
 

	//mine: clear highlighted text within a selection before trying to highlight new text
	this.find("span." + highlightStyle).each(function()	{
		if (pat.indexOf($(this).text()) > -1) {
			with (this.parentNode) {
				replaceChild(this.firstChild, this);
				normalize();
			}
		}
	})

 
	 return this.length && pat && pat.length ? this.each(function() {
		innerHighlight(this, pat.toUpperCase());
	 }) : this;
};

jQuery.fn.removeHighlightAll = function(highlightStyle) {
 return this.find("span." + highlightStyle).each(function() {
  //this.parentNode.firstChild.nodeName; //this line was uncommented in original. why? -ER
  with (this.parentNode) {
   replaceChild(this.firstChild, this);
   normalize();
  }
 }).end();
};

jQuery.fn.removeHighlightSelection = function(pat, highlightStyle) {
 return this.find("span." + highlightStyle).each(function() {
	if (pat.indexOf($(this).text()) > -1) {
		with (this.parentNode) {
			replaceChild(this.firstChild, this);
			normalize();
		}
	}
 }).end();
};