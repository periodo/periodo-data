# PeriodO data dump (draft)

[`data.json`](data.json) is a draft of what we expect a dump of all PeriodO data to
look like. We have two goals for this dump format:

1. It should be easy to work with as
   [plain, simple JSON](http://hublog.hubmed.org/archives/001984.html).

2. It should use JSON-LD features to enable it to be used as Linked Data.

## Basic structure

The dump consists of a set (or JSON array, i.e. the value of the
[`@graph` property](data.json#L27)) of periodizations, where each
periodization is simply a set of period [definitions](data.json#L29-133).
(Note that the `definitions` property is [defined](data.json#L5-7) as
the reverse of
[`skos:inScheme`](http://www.w3.org/TR/skos-reference/#inScheme),
implying that each periodization is a
[`skos:ConceptScheme`](http://www.w3.org/TR/skos-reference/#ConceptScheme).)

Eventually, each periodization and period definition will have a
stable URI; we haven't gotten into minting these yet.

Each periodization has a [source](data.json#L134-162). Where possible,
we link to an authoritative source of metadata for the source. For
convenience, we include information about titles, creators /
contributors, and publication years in the dump.

Each [period definition](data.json#L30-49) has at least the folllowing properties:

* [`label`](data.json#L31) The name given to the period in the original source.
* [`originalLabel`](data.json#L32-34) A
  [language map](http://www.w3.org/TR/json-ld/#language-maps) indicating the language and region of the name given to the period in the original source.
* [`spatialCoverage`](data.json#L35-40) A set of modern-day places indicating the
  intended geographical scope of the period definition.
* `start` and `stop` indicating the temporal extent of the period definition.

`start` and `stop` are still in flux; don't pay too much attention to
them for now. We are in the process of developing a parser for
converting various historical date formats to a common normalized form
and collecting examples of date definitions to better understand how
best to express the values of these properties.



