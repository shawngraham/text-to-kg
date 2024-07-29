# text-to-kg
just an experiment

uses tesseract.js to do ocr, then passes the text to a local model via ollama to try to generate an ontology; then uses that ontology to extract a knowledge graph. Best results with openai models, but it'd be better for a variety of reasons if it used a local model. tinyllama is absolute crap but it's what I used to develop since I'm currently working on a laptop without a lot of juice. You'll want to change that up. Also, it'd be better if something more powerful than tesseract.js was used for the ocr'ing.
