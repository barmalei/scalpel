## Scalpel: Text Analyzing Engine 

Scalpel is text analyzing tool that implements and integrates various text analyzing and processing algorithms and packages. 
The approach and design of Scalpel tries to make the library maximal usable, clear and understandable for researchers and developers. 
One of the main goal is seamless integration various third-party text processing libraries (TNT, Lingpipe, Stanford, etc) under
common ruff with unified common interface. The following main text processing and analyzing tasks are embedded in Scalpel:
  * Named entity recognition:
    * Stanford NER
    * Lingpipe NER
    * TNT Dutch NER
    * LBJ NER
  * Part of speech tagging:
    * Stanford POS
    * TNT POS
  * Stemmer 
    * Basing on snowball 
  * Edit distance (Levenshtein) match and search 
  * Bitap search 
  * Episode distance 
  * Corpora manipulation:
     * CoNLL 2000
     * CoNLL 2002
     * CoNLL 2003
  * Tokenization and tokens manipulation
  * etc

To make live simpler Scalpel itself is implemented in Python. Beneath python API different third packages 
written in other programming languages are hidden. For instance Stanford and Lingpipe are Java based packages,
Snowball stemmer is C-baed package, TNT is binary package etc. Scalpel abstraction level allows developers
to access all these packages using the common interface/API. For instance, to recognize
entities by Stanford NER do the following:
 
		from gravity.tae.ner.stanford.ner import NER
		result = NER()("Text to where named entities have to be recognized")

In case of Lingpipe NER it looks practically the same:

		from gravity.tae.ner.lingpipe.ner import NER
		result = NER()("Text to where named entities have to be recognized")


## Scalpel installation

Just go to Scalpel home folder and type in terminal the following command:

	$ python ./.primus/deploy.py

Deployment cares about downloading all third party packages, compilation C and Java code, 
validation environment, configuring and testing. 

Than include "SCALPEL_HOME/lib" folder in your project PYTHONPATH and use it. It is possible
to see whether it is in workable state by typing the following commands:

    $ export PYTHONPATH=lib
    $ python lib/gravity/tae/ner/stanford/ner.py

Or, SURPRISE, run JAVA based NER under Jython what can significantly speedup your code:
	
	$ export JYTHONPATH=lib
	$ lib/jython/jython lib/gravity/tae/ner/stanford/ner.py



## License 
LGPL

Pay attention there is a bunch of third party packages used by Scalpel that are distributed under various licenses.
Be careful if Scalpel is going to be distributed as part of commercial project. 

For research purposes the project can be used as is. No special restrictions have been found :)


## More information

Take a look at Scalpel presentation:
   * In PDF: http://www.lw-zone.org/download/tae.pdf
   * As iWork KeyNote presentation: http://www.lw-zone.org/download/tae.key




