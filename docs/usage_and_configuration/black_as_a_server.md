# Black as a server (blackd)

`blackd` is a small HTTP server that exposes _Black_'s functionality over a simple
protocol. The main benefit of using it is to avoid the cost of starting up a new _Black_
process every time you want to blacken a file.

```{warning}
`blackd` should not be run as a publicly accessible server as there are no security
precautions in place to prevent abuse. **It is intended for local use only**.
```

## Usage

`blackd` is not packaged alongside _Black_ by default because it has additional
dependencies. You will need to execute `pip install 'black[d]'` to install it.

You can start the server on the default port, binding only to the local interface by
running `blackd`. You will see a single line mentioning the server's version, and the
host and port it's listening on. `blackd` will then print an access log similar to most
web servers on standard output, merged with any exception traces caused by invalid
formatting requests.

`blackd` provides even less options than _Black_. You can see them by running
`blackd --help`:

```{program-output} blackd --help

```

There is no official `blackd` client tool (yet!). You can test that blackd is working
using `curl`:

```sh
blackd --bind-port 9090 &  # or let blackd choose a port
curl -s -XPOST "localhost:9090" -d "print('valid')"
```

## Protocol

`blackd` only accepts `POST` requests at the `/` path. The body of the request should
contain the python source code to be formatted, encoded according to the `charset` field
in the `Content-Type` request header. If no `charset` is specified, `blackd` assumes
`UTF-8`.

There are a few HTTP headers that control how the source code is formatted. These
correspond to command line flags for _Black_. There is one exception to this:
`X-Protocol-Version` which if present, should have the value `1`, otherwise the request
is rejected with `HTTP 501` (Not Implemented).

The headers controlling how source code is formatted are:

- `X-Line-Length`: corresponds to the `--line-length` command line flag.
- `X-Skip-Source-First-Line`: corresponds to the `--skip-source-first-line` command line
  flag. If present and its value is not an empty string, the first line of the source
  code will be ignored.
- `X-Skip-String-Normalization`: corresponds to the `--skip-string-normalization`
  command line flag. If present and its value is not the empty string, no string
  normalization will be performed.
- `X-Skip-Magic-Trailing-Comma`: corresponds to the `--skip-magic-trailing-comma`
  command line flag. If present and its value is not an empty string, trailing commas
  will not be used as a reason to split lines.
- `X-Preview`: corresponds to the `--preview` command line flag. If present and its
  value is not an empty string, experimental and potentially disruptive style changes
  will be used.
- `X-Fast-Or-Safe`: if set to `fast`, `blackd` will act as _Black_ does when passed the
  `--fast` command line flag.
- `X-Python-Variant`: if set to `pyi`, `blackd` will act as _Black_ does when passed the
  `--pyi` command line flag. Otherwise, its value must correspond to a Python version or
  a set of comma-separated Python versions, optionally prefixed with `py`. For example,
  to request code that is compatible with Python 3.5 and 3.6, set the header to
  `py3.5,py3.6`.
- `X-Diff`: corresponds to the `--diff` command line flag. If present, a diff of the
  formats will be output.

If any of these headers are set to invalid values, `blackd` returns a `HTTP 400` error
response, mentioning the name of the problematic header in the message body.

Apart from the above, `blackd` can produce the following response codes:

- `HTTP 204`: If the input is already well-formatted. The response body is empty.
- `HTTP 200`: If formatting was needed on the input. The response body contains the
  blackened Python code, and the `Content-Type` header is set accordingly.
- `HTTP 400`: If the input contains a syntax error. Details of the error are returned in
  the response body.
- `HTTP 500`: If there was any other kind of error while trying to format the input. The
  response body contains a textual representation of the error.

The response headers include a `X-Black-Version` header containing the version of
_Black_.
