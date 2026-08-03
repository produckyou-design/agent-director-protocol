# Director Analysis — T-401 / T-402: Health Endpoint + Config Loader (new API service)

## Request

Stand up the first two pieces of a new Go API service: a `GET /health`
endpoint, and a YAML config file loader that the server's `main.go` uses at
startup. Both are needed before the service can run at all.

## Existing scaffold

`cmd/server/main.go` already exists (written during project bootstrap, not
part of either task below) and already calls both not-yet-implemented
functions in anticipation of this work:

```go
mux := http.NewServeMux()
health.RegisterRoutes(mux)
cfg, err := config.Load(configPath)
```

The binary will not build until both tasks land — that is expected and does
not block either task's own tests, which run against each package in
isolation (`go test ./internal/health/...` and `go test ./internal/config/...`).

## Conflict domain check (parallel-eligibility)

| Domain | T-401 (health) | T-402 (config) | Overlap? |
|---|---|---|---|
| files | `internal/health/handler.go`, `internal/health/handler_test.go` | `internal/config/config.go`, `internal/config/config_test.go`, `internal/config/testdata/sample-config.yaml` | none |
| data_structures | (none new) | `Config` struct | none |
| interfaces | `health.RegisterRoutes(mux *http.ServeMux)` | `config.Load(path string) (*Config, error)` | none |
| db_entities | — | — | none |
| shared_configs | — | — | none |
| state_stores | — | — | none |
| build_targets | `cmd/server` (read-only: neither task edits main.go) | `cmd/server` (read-only) | none — both only *read* main.go, listed in `must_read_files`, not `editable_files` |
| user_flows | GET /health request flow | server startup config loading | none |

No column has any overlap, and `cmd/server/main.go` is in `forbidden_files`
for both tasks rather than `editable_files` for either. **Parallel execution
approved**: T-401 and T-402 are delegated concurrently as independent task
contracts, each reviewed independently.

## Counter-example: a pair that would NOT be parallel-eligible

If a third task, hypothetically "add a `GET /metrics` endpoint that reports
the active `LogLevel` from config," were delegated alongside T-402, it would
need to both call `config.Load` and read the `Config.LogLevel` field —
overlapping T-402 on the `interfaces` domain (`config.Load`) and the
`data_structures` domain (`Config`'s fields). That pair would be sequential:
the config loader would need to land and be reviewed first, since the
metrics task's correctness depends on `Config`'s shape not changing out
from under it mid-flight.

## Delegation

Two task contracts, T-401 and T-402, issued together. Each is reviewed
independently against its own ten-check review; approval of one does not
depend on the other, since neither's tests or completion criteria reference
the other's package.
