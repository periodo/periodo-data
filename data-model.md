## Period definitions

The PeriodO dataset is essentially a collection of period definitions.

### Labels and documentation

A period definition is a [`skos:Concept`](http://www.w3.org/TR/skos-reference/#concepts), “an idea or notion,” as the SKOS Reference puts it. We use a number of SKOS properties to describe period definitions:

* [`skos:prefLabel`](http://www.w3.org/TR/skos-reference/#prefLabel) is used for the name of the period exactly as given in the original source. The value of this property is a simple literal [xsd:string](http://www.w3.org/TR/xmlschema11-2/#string), with no language tag.

* [`skos:altLabel`](http://www.w3.org/TR/skos-reference/#altLabel) is used for language-specific names of the period, assigned by PeriodO curators. The value of this property is a [language-tagged string](http://www.w3.org/TR/rdf11-concepts/#dfn-language-tagged-string). The language tag consists of (at least)

    1. a three-character [primary language subtag](http://tools.ietf.org/html/bcp47#section-2.2.1), as defined in [ISO 639-2](https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes) or [ISO 639-3](https://en.wikipedia.org/wiki/ISO_639-3), and
    2. a four-character [script subtag](http://tools.ietf.org/html/bcp47#section-2.2.3), as defined in [ISO 15924](http://www.unicode.org/iso15924/codelists.html).

    There will always be at least one `skos:altLabel`, with the language tag `eng-latn`. If the source definition was not written in English, there will always be another `skos:altLabel` with a language tag indicating the language and script of the source definition.

* [`skos:note`](http://www.w3.org/TR/skos-reference/#note) is used for notes about the period definition that appeared in the original source. For example, the original Pleiades definition of “Ottoman Rise (AD 1300-1453)” includes the note “ends with the conquest of Constantinople.” The value of this property is a simple literal [xsd:string](http://www.w3.org/TR/xmlschema11-2/#string), with no language tag.

* [`skos:editorialNote`](http://www.w3.org/TR/skos-reference/#editorialNote) is used for administrative or editorial notes added by the PeriodO curators; these do *not* appear in the original source. The value of this property is a simple literal [xsd:string](http://www.w3.org/TR/xmlschema11-2/#string), with no language tag.

* [`skos:inScheme`](http://www.w3.org/TR/skos-reference/#inScheme) is used to link a period definition to the [period collection](#period-collections) of which it is a part.

### Source

Usually the bibliographic information about the source of a period definition is provided through properties of the [period collection](#period-collections) to which it belongs. However, in some cases there may be additional bibliographic information that is specific to an individual definition. In these cases, we use a [`dcterms:source`](http://dublincore.org/documents/dcmi-terms/#terms-source) to provide this additional information, and [`dcterms:isPartOf`](http://dublincore.org/documents/dcmi-terms/#terms-isPartOf) to link the source of the definition to the source of the collection to which it belongs. For example, we might use the following to indicate that the specific book page from which a definition was sourced:

    <p0tns5v4kdf>
        dcterms:source [
            dcterms:isPartOf <http://www.worldcat.org/oclc/63807908> ;
            bibo:locator "page 25"
        ] .

(`bibo` is the [Bibliographic Ontology](http://bibliontology.com).)

### Temporal extent

We use properties from the [Time Ontology](http://www.w3.org/TR/owl-time/) to describe the temporal extent of period definitions. A period definition is a [`time:ProperInterval`](http://www.w3.org/TR/owl-time/#relations), an interval of time with different beginning and end points. We assume that these (instantaneous) beginning and end points can never be precisely identified, hence our descriptions focus on describing the intervals that start and finish the period:

* [`time:intervalStartedBy`](http://www.w3.org/TR/owl-time/#relations) links the period definition to an (anonymous) time interval that has the same (unknown) beginning point as the period, and an (unknown) end point that comes before the end point of the period. We call this the *start* interval for the period.

* [`time:intervalFinishedBy`](http://www.w3.org/TR/owl-time/#relations) links the period definition to an (anonymous) time interval that has the same (unknown) end point as the period, and an (unknown) beginning point that comes after the beginning point of the period. We call this the *stop* interval for the period.

![Diagram showing the relation between a period and its start and stop intervals](start-stop-intervals.png?raw=true)

We describe the start and stop intervals in two ways. Both ways of describing the interval are required; these are complementary descriptions, not alternatives:

1. [`skos:prefLabel`](http://www.w3.org/TR/skos-reference/#prefLabel) is used to textually describe the interval exactly as given in the original source, for example “end of the first century BC”. The value of this property is a simple literal [xsd:string](http://www.w3.org/TR/xmlschema11-2/#string), with no language tag.

2. [`time:hasDateTimeDescription`](http://www.w3.org/TR/owl-time/#calclock) is used to describe the interval in a more structured fashion. This property links the interval to an (anonymous) [`time:DateTimeDescription`](http://www.w3.org/TR/owl-time/#calclock). These structured descriptions are created by PeriodO curators.

Currently we use the following properties in our datetime descriptions:

* [`time:year`](http://www.w3.org/TR/owl-time/#calclock) for descriptions of intervals that can be represented with a single year. For example, an interval with the textual description “600 BC” can be described with a datetime description having a `time:year` value of `-0599`.

* [`periodo:earliestYear`](http://n2t.net/ark:/99152/p0v#earliestYear) and [`periodo:latestYear`](http://n2t.net/ark:/99152/p0v#latestYear) for descriptions of intervals that need to be represented as ranges. For example, an interval with the textual description “eight century BC” can be described with a datetime description having a `periodo:earliestYear` value of `-0799` and a `periodo:latestYear` value of `-0700`.

The datatype for values of `time:year`, `periodo:earliestYear`, and `periodo:latestYear` is [`xsd:gYear`](http://www.w3.org/TR/xmlschema11-2/#gYear). Note that:

1. `xsd:gYear` values can have [any number of digits](http://www.w3.org/TR/xmlschema11-2/#partial-implementation).
2. `xsd:gYear` values [may be zero](http://www.w3.org/TR/xmlschema11-2/#dateTime-value-space). The value `0000` is interpreted as 1 BCE.
3. `xsd:gYear` values represent Gregorian calendar years and [“are not, in general, convertible to simple values corresponding to years in other calendars.”](http://www.w3.org/TR/xmlschema11-2/#gYear) We are comfortable with this limitation because we use these values only for the purposes of ordering and visualizing temporal extents of intervals. The `skos:prefLabel` of an interval should be considered the authoritative description.

We may use additional properties in our datetime descriptions in the future, for example to describe intervals at a finer temporal granularity than a year.

### Spatial extent

We use the following properties to describe the spatial extent of period definitions:

* [`periodo:spatialCoverageDescription`](http://n2t.net/ark:/99152/p0v#spatialCoverageDescription) is used to textually describe the spatial extent exactly as given in the original source, for example “Near East and Greece”. The value of this property is a simple literal [xsd:string](http://www.w3.org/TR/xmlschema11-2/#string), with no language tag.

* [`dcterms:spatial`](http://dublincore.org/documents/dcmi-terms/#terms-spatial) is used to link a period definition to descriptions of locations in gazetteers such as DBpedia/Wikidata, GeoNames, or Pleiades.

## <a name="period-collections"></a>Period collections

A period collection is simple a set of period definitions that share a source. We use [`dcterms:source`](http://dublincore.org/documents/dcmi-terms/#terms-source) to link period collections to bibliographic descriptions of their sources. Where possible we rely on external bibliographic databases such as WorldCat and CrossRef for bibliographic metadata.

A period collection is a [`skos:ConceptScheme`](http://www.w3.org/TR/skos-reference/#schemes), “an aggregation of one or more SKOS concepts”. Belonging to the same period collection does not imply any semantic relationship between period definitions, other than sharing a source. In particular, the period definitions belonging to a period collection do not constitute a *periodization*, meaning a single coherent, continuous division of historical time. In the future we plan to add additional properties for indicating when a set of period definitions constitute a periodization.

The [root resource](http://www.w3.org/TR/void/#root-resource) of the PeriodO dataset is an [rdf:Bag](http://www.w3.org/TR/rdf-schema/#ch_bag) (unordered collection) of period collections.




