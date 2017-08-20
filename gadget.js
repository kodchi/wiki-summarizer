(function(d, $, mw) {
	var API_URL = 'http://localhost:8002',
		isMarkerLoaded = false,
		$button = $('<button>Summarize</button>');

	function fetchSummaries() {
		$.getJSON(
			API_URL,
			{ pageName: mw.config.get('wgPageName') },
			showSummary
		);
	}

	function loadMarkerAndFetchSummaries() {
		var script = d.createElement('script');

		script.type = 'text/javascript';
		script.async = true;
		script.onload = function() {
			isMarkerLoaded = true;
			fetchSummaries();
		};

		script.src = 'https://cdn.jsdelivr.net/mark.js/8.9.1/mark.min.js';
		d.getElementsByTagName('head')[0].appendChild(script);
	}


	function highlightSentences(sentences) {
		var markInstance = new Mark(document.querySelector("#mw-content-text")),
			options = {
				acrossElements: true,
				separateWordSearch: false,
				noMatch: function(s) {console.log(s);}
			},
			detachedElements = [],
			i;

		markInstance.unmark();

		// Detach some elements so that we can match sentences.
		$('.metadata,.reference,.IPA').each(function(i, el) {
			var $el = $(el);
			$('<span class="placeholder">').insertAfter($el);
			detachedElements.push($el.detach());
		});

		markInstance.mark(sentences, options);

		// Put back the detached elements
		$('.placeholder').each(function(i, el) {
			$(el).replaceWith(detachedElements[i++]);
		});
	}

	function showSummary(summarizedSections) {
		var sentences = [],
			heading;

		summarizedSections.forEach(function(section) {
			Array.prototype.push.apply(sentences, section.summary);
		});

		// highlight the sentences in the article
		highlightSentences(sentences);

		// also insert the sentences to the beginning of the article
		$('#mw-content-text').prepend('<ul><li>' + sentences.join('</li><li>') + '</li></ul>');

		$button.remove();
	}

	if (!mw.config.get('wgIsArticle') ||
		mw.config.get('wgNamespaceNumber') !== 0) {
		return;
	}

	$button.on('click', function () {
		if (isMarkerLoaded) {
			fetchSummaries();
		} else {
			loadMarkerAndFetchSummaries();
		}
		$button
			.text('Summarizing...')
			.attr('disabled', true);
	});

	$button.insertAfter($('#firstHeading'));

}(document, jQuery, mediaWiki));
