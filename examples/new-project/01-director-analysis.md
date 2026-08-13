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

The binary will not build until both tasks land — that is a separate post-batch
integration check and does not block either task's own tests, which run against
each package in isolation (`go test ./internal/health/...` and
`go test ./internal/config/...`). It is not a cross-group dependency for the
two implementation groups because neither group consumes the other's output.

## Conflict domain check (parallel-eligibility)

| Domain | T-401 (health) | T-402 (config) | Overlap? |
|---|---|---|---|
| files | `internal/health/handler.go`, `internal/health/handler_test.go` | `internal/config/config.go`, `internal/config/config_test.go`, `internal/config/testdata/sample-config.yaml` | none |
| data_structures | (none new) | `Config` struct | none |
| interfaces | `health.RegisterRoutes(mux *http.ServeMux)` | `config.Load(path string) (*Config, error)` | none |
| db_entities | — | — | none |
| shared_configs | — | — | none |
| state_stores | — | — | none |
| build_targets | `internal/health` package tests | `internal/config` package tests | none |
| user_flows | GET /health request flow | server startup config loading | none |

No column has any overlap, and the two contracts do not share a required
context file. **Parallel execution approved**: T-401 and T-402 are two independently verifiable groups with
disjoint domains, an empty `dependency_edges` list, and isolated write state.
The batch work contract records:

```json
{
  "independent_groups": [
    {
      "group_id": "G-401",
      "scope": ["internal/health"],
      "independently_verifiable": true,
      "conflict_domains": {
        "files": ["internal/health/handler.go", "internal/health/handler_test.go"],
        "code_regions": [],
        "interfaces": ["health.RegisterRoutes(mux *http.ServeMux)"],
        "schemas": [],
        "generated_artifacts": [],
        "shared_configs": [],
        "state_stores": [],
        "data_structures": [],
        "db_entities": [],
        "build_targets": ["go test ./internal/health/..."],
        "user_flows": ["GET /health request flow"]
      }
    },
    {
      "group_id": "G-402",
      "scope": ["internal/config"],
      "independently_verifiable": true,
      "conflict_domains": {
        "files": ["internal/config/config.go", "internal/config/config_test.go"],
        "code_regions": [],
        "data_structures": ["Config"],
        "interfaces": ["config.Load(path string) (*Config, error)"],
        "schemas": [],
        "generated_artifacts": [],
        "shared_configs": [],
        "state_stores": [],
        "db_entities": [],
        "build_targets": ["go test ./internal/config/..."],
        "user_flows": ["server startup config loading"]
      }
    }
  ],
  "dependency_edges": [],
  "planned_workers": 2,
  "capacity_source": "observed_native_runtime",
  "observed_capacity": 2,
  "write_isolation": "isolated",
  "why_fewer_workers_cannot_absorb": "Each package has its own tests and review evidence; one worker would remove the independent group boundary."
}
```

`planned_workers` is `min(2, 2)`. If native capacity were unknown, the
deterministic fallback would be one sequential worker with
`capacity_source: "unknown"`; no project capacity would be invented. Each
contract is reviewed independently.

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
