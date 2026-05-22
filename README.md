# envoy-config-lint

Static analysis tool for catching common misconfigurations in dotenv and environment variable setups across projects.

---

## Installation

```bash
pip install envoy-config-lint
```

Or install from source:

```bash
git clone https://github.com/yourname/envoy-config-lint.git
cd envoy-config-lint && pip install -e .
```

---

## Usage

Run against a `.env` file or directory:

```bash
envoy-lint .env
```

```bash
envoy-lint ./my-project --recursive
```

Example output:

```
.env:3  [WARN]  Variable DB_PASSWORD has no value set
.env:7  [ERROR] Duplicate key detected: API_KEY
.env:12 [WARN]  Quoted value contains unescaped special characters: SECRET_TOKEN
.env:15 [ERROR] Variable name contains invalid characters: 1INVALID_VAR

4 issues found (1 warning, 3 errors)
```

### Options

| Flag | Description |
|------|-------------|
| `--recursive` | Scan all `.env` files in subdirectories |
| `--strict` | Treat warnings as errors |
| `--format json` | Output results as JSON |
| `--ignore RULE` | Skip a specific rule by ID |

---

## Rules

- Duplicate keys
- Missing or empty values
- Invalid variable naming conventions
- Unsafe secret patterns (e.g., hardcoded tokens)
- Inconsistency between `.env` and `.env.example`

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE)