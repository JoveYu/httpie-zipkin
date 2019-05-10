
# HTTPie zipkin plugin

trace your request from HTTPie client

only for `http://` url

## Installation

### pip
```shell
$ pip install httpie-zipkin
or 
$ pip install -e .
```

### python
```shell
$ python setup.py install
```

## Usage

```shell
$ ZIPKIN_SERVER=http://zipkin.server/api/v2/spans http example.org
```
