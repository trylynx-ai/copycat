import random
import datetime
import uuid
import argparse

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

    log_type = args.log_type or random.choice(list(log_generators.keys()))
    num_entries = args.count or random.randint(1, 5)
    log_func = log_generators[log_type]

    if args.start and args.end:
        time_range = (args.end - args.start).total_seconds()
        timestamps = sorted([
            args.start + datetime.timedelta(seconds=random.uniform(0, time_range))
            for _ in range(num_entries)
        ])
    else:
        timestamps = [datetime.datetime.now() for _ in range(num_entries)]

    for timestamp in timestamps:
        print(log_func(timestamp))

if __name__ == "__main__":
    main()
