# Security Policy

## Supported versions

This project is pre-1.0. Security fixes land on `main`; track the latest commit.

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's
[private vulnerability reporting](https://github.com/ahmeddoghri/contextpack/security/advisories/new)
or email the maintainer. Include a description of the issue and its impact,
steps to reproduce (a minimal proof-of-concept helps), and any suggested fix.

You can expect an acknowledgement within a few days. Once a fix is out you will
be credited unless you would rather stay anonymous.

## Scope notes

contextpack is a pure-stdlib library with no runtime dependencies and makes no
network calls. It compresses text you provide. One thing worth knowing: it is a
lossy compressor, so never use it on content where dropping a token changes the
meaning in a way you have not verified, such as legal or medical text, without
checking the output. That is exactly what the keyword-recall check in the
benchmark is for; use the same idea on your own critical fields before you trust
compressed output in production.
