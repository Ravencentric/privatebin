!!! note
    This page provides basic examples for using the `privatebin` command-line tool. 
    For detailed information and options, please refer to the `--help` flag 
    available with each command (e.g., `privatebin create --help`).

## Create a paste

**Direct text:**

```bash
privatebin create "Your secret text here."
```

**From a file:**

```bash
cat secret.txt | privatebin create
```

## Get a paste

```bash
privatebin get "https://privatebin.net/?pasteid#passphrase"
```

## Delete a paste

```bash
privatebin delete "https://privatebin.net/?pasteid" --token "your_delete_token"
```
