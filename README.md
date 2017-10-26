# wiki-summarizer
Summarizer for Wikipedia articles

## Requirements
* Python 3.6
* See packages in requirements.txt
* ngrok - https://ngrok.com/

## Howto
* Install requirements: `pip install -r requirements.txt`;
* Download the stop words: `python -m nltk.downloader stopwords`

* Run the server: `python server.py`;
* Run ngrok: `ngrok http 8002` (8002 is the port the server is running on);
* Add the contents of `gadget.js` to
  https://meta.wikimedia.org/wiki/Special:MyPage/global.js;
* Make sure to update the server URL in the JS file with your ngrok URL.
* Go to an article page, e.g. https://en.wikipedia.org/wiki/Book and notice the new button called 'Summarize' appear just under the title. Click on it and wait. A list of sentences will show up at the top of the article. These sentences are also highlighted in the article where they appear.

## TODO
* Document files;
* Clean up.
