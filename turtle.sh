#! /bin/sh

DATA="data.json"
BASE_URI="http://perio.do/temporary/"

jsonld normalize -q $DATA | rapper -i nquads -o turtle \
                                   -f 'xmlns:skos="http://www.w3.org/2004/02/skos/core#"' \
                                   -f 'xmlns:dcterms="http://purl.org/dc/terms/"' \
                                   -f 'xmlns:foaf="http://xmlns.com/foaf/0.1/"' \
                                   -f 'xmlns:time="http://www.w3.org/2006/time#"' \
                                   -f 'xmlns:xsd="http://www.w3.org/2001/XMLSchema#"' \
                                   -f 'xmlns:periodo="http://perio.do/temporary/"' \
                                   - $BASE_URI
