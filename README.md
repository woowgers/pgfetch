[![Coverage Status](https://coveralls.io/repos/github/woowgers/pgfetch/badge.svg?branch=main)](https://coveralls.io/github/woowgers/pgfetch?branch=main)

# pgfetch - asynchronous gitea repository fetcher
## Features
- Fetches repository branch asynchronously
- Calculates checksums for files

## TODO
- Indicate progress
- Handle invalid checksums
- Handle last modification date
- Authentication for private repositories

## References
- [nitpick docs](https://nitpick.readthedocs.io/en/latest/index.html)
- [gitea api](https://gitea.com/api/swagger#/repository)
- [asyncio docs](https://docs.python.org/3/library/asyncio.html)
- [aiohttp docs](https://docs.aiohttp.org/en/stable/)
