[![Build Status](https://travis-ci.org/hacktoon/infiniscribe.svg?branch=master)](https://travis-ci.org/hacktoon/infiniscribe)

# Infiniscribe

Infiniscribe is a general purpose data markup language which describes the metadata, context and relations in a data model. It can be used to generate data like HTML, CSS, XML, JSON and other tree structures, using a common language.


## Main objectives
 * Provide a uniform interface for building webapps
 * Build and represent different types of information
 * Automate data generation for different formats


## Documentation

 * [Grammar](docs/grammar.md)
 * [Literals](docs/literals.md)
 * [Keywords](docs/keywords.md)
 * [Objects](docs/objects.md)
 * [Queries](docs/queries.md)
 * [Lists](docs/lists.md)


## Installation

### Dependencies

 * Python 3.7+
 * Pip
 * GNU Make
 * Docker (optional)

It's recommended to use a virtual environment tool like [pyenv](https://github.com/pyenv/pyenv) and/or [pipenv](https://github.com/pypa/pipenv).

```
make install
make test
make inspect
```

## How to run

### Using system's Python

```
./bin/infiniscribe examples/person
```

### Using Docker

```
docker build -t infiniscribe .
docker run infiniscribe examples/thumbnail
```


## License

Infiniscribe is distributed under the terms of the **MIT** license. See [LICENSE](LICENSE.md).
