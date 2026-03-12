[![Static Badge](https://img.shields.io/badge/8540-green?logo=splunk&logoSize=auto&labelColor=gray)](https://splunkbase.splunk.com/app/8540)


# ![Logo](copycat/static/appIcon.png) CopyCat

A lightweight, dependency-free Splunk app/add-on that generates realistic mock logs for testing AI agents, parsing rules, and data analysis workflows.

## Goal

This project provides a log generator designed to:

- Test AI agents against realistic data types and parsing scenarios
- Validate SPL queries, dashboards, and alerts without production data
- Simulate various infrastructure components (web servers, databases, containers, etc.)

### Features

- **Simple Splunk UI:** Choose enabled log types and target ingestion in MB/day
- **Auto pacing:** The app computes the effective log interval automatically from selected types and MB/day target
- **Safe defaults:** If no UI config is present, behavior stays as before
- **CLI Tool:** Standalone Python script for manual log generation
- **Backfill:** Generate historical logs with custom date ranges
- **Zero Dependencies:** Uses Python standard library only (Python 3.9 for full Splunk compatibility)
- **Realistic Data:** Includes IPs, usernames, hostnames, UUIDs, and more

## Generator Types

CopyCat generates various distinct log types, each with realistic formatting and data patterns:

| Log Type    | Description                                             | Index               | Sourcetype          |
| ----------- | ------------------------------------------------------- | ------------------- | ------------------- |
| `app`       | Application logs with levels (INFO, WARN, ERROR, DEBUG) | `copycat_app`       | `copycat:app`       |
| `security`  | Authentication and login attempt logs                   | `copycat_security`  | `copycat:security`  |
| `network`   | Network traffic logs (TCP/UDP/ICMP with actions)        | `copycat_network`   | `copycat:network`   |
| `docker`    | Container lifecycle events                              | `copycat_docker`    | `copycat:docker`    |
| `database`  | SQL query execution logs                                | `copycat_database`  | `copycat:database`  |
| `webserver` | Apache/Nginx-style access logs                          | `copycat_webserver` | `copycat:webserver` |
| `system`    | Linux system daemon logs                                | `copycat_system`    | `copycat:system`    |
| `api`       | REST API request/response logs                          | `copycat_api`       | `copycat:api`       |
| `error`     | Exception and error stack traces                        | `copycat_error`     | `copycat:error`     |
| `metrics`   | System resource metrics (CPU, memory, disk, network)    | `copycat_metrics`   | `copycat:metrics`   |

## Installation

### As a Splunk App / Add-on

1. Copy the `copycat/` directory to `$SPLUNK_HOME/etc/apps/`
2. Restart Splunk: `$SPLUNK_HOME/bin/splunk restart`
3. Open the **CopyCat** app
4. In `CopyCat - Configurazione`, choose:
   - enabled log types
   - target ingestion in `MB/giorno`
5. Click Submit to save

Notes:

- The app stores settings in `copycat/lookups/copycat_env.csv`.
- Runtime env vars used by the generator:
  - `COPYCAT_LOG_TYPES`
  - `COPYCAT_MAX_INGEST_MB_DAY`
- Effective interval is computed automatically from daily MB target and selected log types, with a minimum of 10 seconds.

### As a Standalone CLI Tool

We recommend using [uv](https://github.com/astral-sh/uv) to run CopyCat:

```bash
uv run copycat/bin/copycat.py [options] [log_type]
```

However, running it directly with `python` is also supported (we target Python 3.9 for compatibility with Splunk):

```bash
python copycat/bin/copycat.py [options] [log_type]
```

## CLI Usage

```
copycat.py [--help] [--count N] [--start ISO_DATE] [--end ISO_DATE] [log_type[,log_type...]]
```

### Arguments

- `log_type` (optional): Type of log to generate. Choices: `app`, `security`, `network`, `docker`, `database`, `webserver`, `system`, `api`, `error`, `metrics`. If omitted, a random type is selected.
- `--count`, `-n`: Number of log entries to generate (default: random 1–5)
- `--start`: Start datetime in ISO format (requires `--end`)
- `--end`: End datetime in ISO format (requires `--start`)
- `--help`: Show help message and exit

## Examples

### Generate 5 random application logs

```
$ uv run copycat/bin/copycat.py app --count 5
2026-01-19 10:23:45.123456 [INFO] /var/lib/app.log: System process completed.
2026-01-19 10:23:45.123456 [ERROR] /opt/config/service.py: Connection timeout invalid.
2026-01-19 10:23:45.123456 [WARN] /usr/bin/config.xml: Started found warning.
2026-01-19 10:23:45.123456 [DEBUG] /tmp/share/data.db: Process stopped successful.
2026-01-19 10:23:45.123456 [INFO] /home/log/system.conf: Updated completed.
```

### Generate historical logs with date range

```
$ uv run copycat/bin/copycat.py api --count 10 --start 2026-01-01T00:00:00 --end 2026-01-31T23:59:59
2026-01-05 14:32:18.456789 POST /api/orders from 10.20.30.40 - Response: 200 - 125ms
2026-01-08 09:15:42.123456 GET /api/users from 192.168.1.100 - Response: 200 - 89ms
...
```

## Lynx AI Agent

CopyCat is particularly useful for testing the capabilities of the [Lynx AI Agent](https://trylynx.ai):

- **Natural Language Querying:** Test how the agent interprets natural language questions across different log types and data patterns
- **SPL Query Generation:** Verify that the agent generates efficient, data-aware SPL queries following best practices for various log formats
- **Automated Dashboards:** Generate sample data to test instant visualization creation optimized for different search results
- **Anomaly Detection:** Create realistic historical and real-time data patterns to test the agent's ability to identify anomalies and critical patterns

Once CopyCat is installed and generating logs, you can interact with the Lynx AI Agent to query, analyze, and visualize the generated data just as you would with production logs.

## Contributing

Contributions are welcome! If you encounter any bugs or have suggestions for improvements, please open an issue in the [issue tracker](https://github.com/trylynx-ai/copycat/issues).

## License

This open-source project is available under the [MIT License](LICENSE). Feel free to use, modify, and distribute it under the terms of the license.
