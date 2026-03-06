# Probely Bulk Domain Add

Simple script to bulk add registered domains to Snyk API & Web for discovery using the Create Domain API.

Usage:

```bash
python3 probely_bulk_add.py -a <API_KEY> -f domains.txt [-o results.txt]
```

Arguments:

- `-a --api-key <your api key>` Your Snyk API & Web token (use the JWT token shown in the docs).
   If omitted the script will attempt to use the `SAW_API` environment variable.
- `-f --file <filename>`: Path to a newline-delimited file containing domains to add.
- `-o --output <filename>`: Optional path to append human-readable results.

Notes:

- The script posts to `https://api.probely.com/domains/` and expects the API key to be sent as `Authorization: JWT <token>`.
- Install dependencies with `pip install -r requirements.txt`.
