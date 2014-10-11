#! /bin/sh

#DATA="https://raw.githubusercontent.com/periodo/examples/master/data.json"
DATA="data.json"
BASE_URI="http://perio.do/temporary/"

jsonld normalize -q $DATA | rapper -i nquads -o turtle - $BASE_URI
