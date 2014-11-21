Example: "Early Dynastic period" defined as starting "3000 B.C. (+/- 150 years)" and ending "about 2330 B.C."

```json
{ label: "Early Dynastic period"
, start:
  { in:
    { "earliestYear": "-3149"
    , "latestYear": "-2849"
    }
  , label: "3000 B.C. (+/- 150 years)"
  }
  , stop:
  { in:
    { "year": "-2329" }
  , label: "about 2330 B.C."
  }
}
```

More examples of interval descriptions:

* seventeenth century B.C.
```json
{ "earliestYear": "-1699"
, "latestYear": "-1600"
}
```

* 675/650
```json
{ "earliestYear": "-675"
, "latestYear": "-650"
}
```

* mid 3rd century BC
```json
{ "earliestYear": "-274"
, "latestYear": "-224"
}
```

* at least from the beginning of the second millennium B.C.E.
```json
{ "latestYear": "-1999"
}
```

* 3000 B.C. (+/- 150 years)
```json
{ "earliestYear": "-3149"
, "latestYear": "-2849"
}
```

* 4th millennium B.C.E.
```json
{ "earliestYear": "-3999"
, "latestYear": "-3000"
}
```

* before 1000
```json
{ "latestYear": 1000
}
```

* 7th cent.
```json
{ "earliestYear": "600"
, "latestYear": "699"
}
```

Proposed changes to JSON-LD context:

1. `start` changes from `http://www.w3.org/2006/time#hasBeginning` to `http://www.w3.org/2006/time#intervalStartedBy`.

1. `stop` changes from `http://www.w3.org/2006/time#hasEnding` to `http://www.w3.org/2006/time#intervalFinishedBy`.

1. `in` changes from `http://www.w3.org/2006/time#inDateTime` to `http://www.w3.org/2006/time#hasDateTimeDescription`.

1. `earliestYear` is defined as follows:
```
:earliestYear
  a owl:DatatypeProperty ;
  rdfs:domain :DateTimeDescription ;
  rdfs:range xsd:gYear .

:DateTimeDescription
  rdfs:subClassOf [
    a owl:Restriction ;
    owl:maxCardinality "1"^^xsd:nonNegativeInteger ;
    owl:onProperty :earliestYear
  ]
```

1. `latestYear` is defined as follows:
```
:latestYear
  a owl:DatatypeProperty ;
  rdfs:domain :DateTimeDescription ;
  rdfs:range xsd:gYear .

:DateTimeDescription
  rdfs:subClassOf [
    a owl:Restriction ;
    owl:maxCardinality "1"^^xsd:nonNegativeInteger ;
    owl:onProperty :latestYear
  ]
```
