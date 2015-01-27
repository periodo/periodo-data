#! /bin/sh

BASE_URI="http://n2t.net/ark:/99152/p0/"

jsonld normalize -q $1 | rapper -i nquads -o turtle \
                                   -f 'xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"' \
                                   -f 'xmlns:bibo="http://purl.org/ontology/bibo/"' \
                                   -f 'xmlns:dcterms="http://purl.org/dc/terms/"' \
                                   -f 'xmlns:foaf="http://xmlns.com/foaf/0.1/"' \
                                   -f 'xmlns:owl="http://www.w3.org/2002/07/owl#"' \
                                   -f 'xmlns:skos="http://www.w3.org/2004/02/skos/core#"' \
                                   -f 'xmlns:time="http://www.w3.org/2006/time#"' \
                                   -f 'xmlns:xsd="http://www.w3.org/2001/XMLSchema#"' \
                                   -f "xmlns:periodo=\"${BASE_URI}vocab#\"" \
                                   - "$BASE_URI"

