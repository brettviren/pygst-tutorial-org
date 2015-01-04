$( document ).ready (function () {
    $("pre.src-sh").each(function () {
	var lines = $( this ).text().split('\n');
	for (var ind = 0 ; ind < lines.length ; ind++) {
            if ( ! lines[ind] ) {
		continue;
	    }
	    lines[ind] = '<span class="shell-line"></span>' + lines[ind];
	}
	$( this ).html(lines.join("\n"));
    });


    // broken way to do things for now.
    $( "div.status" ).prepend( $('<br><a href="index.org">org source</a>') )
    $( "div.status" ).prepend( $('<hr></hr>') )

});

