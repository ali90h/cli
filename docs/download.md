# Download mode

HTTPie's `--download` option saves response bodies to files. When a server
returns a `Content-Encoding` (for example `gzip`), the `Content-Length` header
is treated as the size of the encoded payload as defined in RFC 9110 § 8.6.
HTTPie writes the body exactly as received and no longer compares the header to
the post-decompression size.

