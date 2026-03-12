import argparse
import csv
import datetime
import json
import math
import os
import random
import uuid

def fake_ipv4():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def fake_user_name():
    first_names = ["john", "jane", "bob", "alice", "charlie", "diana", "eve", "frank"]
    last_names = ["smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis"]
    return f"{random.choice(first_names)}.{random.choice(last_names)}"

def fake_sentence():
    words = ["system", "process", "completed", "failed", "started", "stopped", "error", "warning",
             "connection", "timeout", "successful", "invalid", "missing", "found", "updated"]
    return " ".join(random.choices(words, k=random.randint(3, 8))).capitalize() + "."

def fake_file_path():
    dirs = ["var", "opt", "usr", "home", "tmp", "etc"]
    subdirs = ["lib", "bin", "share", "log", "config"]
    files = ["app.log", "system.conf", "data.db", "config.xml", "service.py"]
    return f"/{random.choice(dirs)}/{random.choice(subdirs)}/{random.choice(files)}"

def fake_uri_path():
    paths = ["/api/v1/users", "/dashboard", "/login", "/logout", "/settings", "/profile", "/search", "/admin", "/reports"]
    return random.choice(paths)

def fake_hostname():
    prefixes = ["web", "db", "api", "cache", "proxy", "mail", "app"]
    suffixes = ["01", "02", "03", "prod", "dev", "test", "staging"]
    return f"{random.choice(prefixes)}-{random.choice(suffixes)}.example.com"

def fake_word():
    words = ["users", "orders", "products", "sessions", "logs", "events", "metrics", "alerts", "reports", "data"]
    return random.choice(words)

def fake_uuid4():
    return str(uuid.uuid4())

def generate_app_logs(timestamp):
    levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
    return f"{timestamp} [{random.choice(levels)}] {fake_file_path()}: {fake_sentence()}"

def generate_security_logs(timestamp):
    return f"{timestamp} User {fake_user_name()} login attempt from {fake_ipv4()}"

def generate_network_logs(timestamp):
    protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS']
    actions = ['ACCEPT', 'DROP', 'REJECT']
    return f"{timestamp} {random.choice(protocols)} {fake_ipv4()}:{random.randint(1024, 65535)} -> {fake_ipv4()}:{random.randint(80, 8080)} {random.choice(actions)}"

def generate_docker_logs(timestamp):
    containers = ['web-app', 'database', 'redis', 'nginx', 'api-server']
    actions = ['started', 'stopped', 'restarted', 'failed', 'pulled']
    return f"{timestamp} Container {random.choice(containers)}-{fake_uuid4()[:8]} {random.choice(actions)}"

def generate_database_logs(timestamp):
    operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP']
    return f"{timestamp} {random.choice(operations)} query executed on table {fake_word()} by user {fake_user_name()} - {random.randint(1, 1000)}ms"

def generate_webserver_logs(timestamp):
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    status_codes = [200, 201, 400, 401, 403, 404, 500, 502, 503]
    return f"{fake_ipv4()} - - [{timestamp.strftime('%d/%b/%Y:%H:%M:%S +0000')}] \"{random.choice(methods)} {fake_uri_path()} HTTP/1.1\" {random.choice(status_codes)} {random.randint(100, 50000)}"

def generate_system_logs(timestamp):
    processes = ['systemd', 'kernel', 'cron', 'ssh', 'sudo']
    return f"{timestamp} {random.choice(processes)}[{random.randint(1000, 9999)}]: {fake_sentence()}"

def generate_api_logs(timestamp):
    endpoints = ['/api/users', '/api/orders', '/api/products', '/api/auth', '/api/payments']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    return f"{timestamp} {random.choice(methods)} {random.choice(endpoints)} from {fake_ipv4()} - Response: {random.choice([200, 400, 401, 500])} - {random.randint(10, 500)}ms"

def generate_error_logs(timestamp):
    errors = ['NullPointerException', 'ConnectionTimeout', 'OutOfMemoryError', 'ValidationError', 'AuthenticationError']
    return f"{timestamp} {random.choice(errors)} in {fake_file_path()}:{random.randint(1, 1000)} - {fake_sentence()}"

def generate_metrics_logs(timestamp):
    metrics = ['CPU', 'Memory', 'Disk', 'Network']
    return f"{timestamp} {random.choice(metrics)} usage: {random.randint(10, 95)}% - Host: {fake_hostname()}"

log_generators = {
    "app": generate_app_logs,
    "security": generate_security_logs,
    "network": generate_network_logs,
    "docker": generate_docker_logs,
    "database": generate_database_logs,
    "webserver": generate_webserver_logs,
    "system": generate_system_logs,
    "api": generate_api_logs,
    "error": generate_error_logs,
    "metrics": generate_metrics_logs
}

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOKUP_ENV_PATH = os.path.join(APP_ROOT, "lookups", "copycat_env.csv")
STATE_PATH = os.path.join(APP_ROOT, "var", "copycat_runtime_state.json")

DEFAULT_INTERVAL_SEC = 10

ENV_VAR_MAP = {
    "copycat_log_types": "COPYCAT_LOG_TYPES",
    "copycat_max_ingest_mb_day": "COPYCAT_MAX_INGEST_MB_DAY",
}

ESTIMATED_BYTES_PER_EVENT = {
    "app": 130,
    "security": 95,
    "network": 105,
    "docker": 100,
    "database": 140,
    "webserver": 115,
    "system": 100,
    "api": 120,
    "error": 150,
    "metrics": 90,
}

def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue

def parse_datetime(value):
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid datetime format: {value}. Use ISO format (e.g., 2024-01-01T12:00:00)")

def load_runtime_env_from_lookup():
    if not os.path.exists(LOOKUP_ENV_PATH):
        return
    try:
        with open(LOOKUP_ENV_PATH, "r", encoding="utf-8", newline="") as lookup_file:
            row = next(csv.DictReader(lookup_file), None)
    except OSError:
        return

    if not row:
        return

    for lookup_field, env_var in ENV_VAR_MAP.items():
        value = row.get(lookup_field)
        if value is not None:
            os.environ[env_var] = str(value).strip()

def get_enabled_log_types():
    raw = os.environ.get("COPYCAT_LOG_TYPES", "").strip()
    if raw == "":
        return set(log_generators.keys())

    selected = [log_type.strip() for log_type in raw.split(",")]
    selected = [log_type for log_type in selected if log_type in log_generators]
    if not selected:
        return set(log_generators.keys())
    return set(selected)

def get_max_ingest_mb_day():
    raw = os.environ.get("COPYCAT_MAX_INGEST_MB_DAY", "").strip()
    if raw == "":
        return None
    try:
        value = float(raw)
        if value > 0:
            return value
    except ValueError:
        return None
    return None

def compute_interval_sec_from_volume(enabled_types, max_ingest_mb_day):
    if max_ingest_mb_day is None:
        return DEFAULT_INTERVAL_SEC

    bytes_per_cycle = sum(ESTIMATED_BYTES_PER_EVENT.get(log_type, 0) for log_type in enabled_types)
    if bytes_per_cycle <= 0:
        return DEFAULT_INTERVAL_SEC

    max_day_bytes = max_ingest_mb_day * 1024 * 1024
    if max_day_bytes <= 0:
        return DEFAULT_INTERVAL_SEC

    required_interval = int(math.ceil((bytes_per_cycle * 86400) / max_day_bytes))
    return max(DEFAULT_INTERVAL_SEC, required_interval)

def load_runtime_state():
    if not os.path.exists(STATE_PATH):
        return {"last_emit_by_type": {}}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as state_file:
            state = json.load(state_file)
    except (OSError, json.JSONDecodeError):
        return {"last_emit_by_type": {}}

    if "last_emit_by_type" not in state or not isinstance(state["last_emit_by_type"], dict):
        state["last_emit_by_type"] = {}
    return state

def save_runtime_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as state_file:
        json.dump(state, state_file)

def should_emit_event(log_type):
    try:
        enabled_types = get_enabled_log_types()
        if log_type not in enabled_types:
            return False

        now_epoch = int(datetime.datetime.now().timestamp())
        interval_sec = compute_interval_sec_from_volume(enabled_types, get_max_ingest_mb_day())

        state = load_runtime_state()
        last_emit_by_type = state.get("last_emit_by_type", {})
        last_emit_epoch = int(last_emit_by_type.get(log_type, 0))
        if now_epoch - last_emit_epoch < interval_sec:
            return False

        last_emit_by_type[log_type] = now_epoch
        state["last_emit_by_type"] = last_emit_by_type
        save_runtime_state(state)
        return True
    except (OSError, ValueError, TypeError):
        # Preserve original behavior on filesystem issues.
        return True

def is_scripted_input_mode(args):
    return args.log_type is not None and args.count is None and args.start is None and args.end is None

def main():
    parser = argparse.ArgumentParser(description="Generate fake log data for Splunk testing")
    parser.add_argument(
        'log_type',
        nargs='?',
        choices=list(log_generators.keys()),
        help="Type of log to generate. If not specified, a random type will be selected"
    )
    parser.add_argument(
        '--count', '-n',
        type=positive_int,
        help="Number of log entries to generate. Must be a positive integer. If not specified, a random number from 1 to 5 will be used"
    )
    parser.add_argument(
        '--start',
        type=parse_datetime,
        help="Start datetime in ISO format (e.g., 2024-01-01T12:00:00). Requires --end"
    )
    parser.add_argument(
        '--end',
        type=parse_datetime,
        help="End datetime in ISO format (e.g., 2024-01-31T12:00:00). Requires --start"
    )
    args = parser.parse_args()

    if (args.start is None) != (args.end is None):
        parser.error("--start and --end must both be provided or both be omitted")
    if args.start and args.end and args.end <= args.start:
        parser.error("--end must be later than --start")

    load_runtime_env_from_lookup()

    log_type = args.log_type or random.choice(list(log_generators.keys()))
    num_entries = args.count or random.randint(1, 5)
    log_func = log_generators[log_type]
    scripted_input_mode = is_scripted_input_mode(args)

    if args.start and args.end:
        time_range = (args.end - args.start).total_seconds()
        timestamps = sorted([
            args.start + datetime.timedelta(seconds=random.uniform(0, time_range))
            for _ in range(num_entries)
        ])
    else:
        timestamps = [datetime.datetime.now() for _ in range(num_entries)]

    for timestamp in timestamps:
        event_line = log_func(timestamp)
        if scripted_input_mode and not should_emit_event(log_type):
            continue
        print(event_line)

if __name__ == "__main__":
    main()
