import random
import datetime
import uuid
import argparse

def weighted_choice(options):
    return random.choices(list(options), weights=list(options.values()))[0]

def fake_ipv4():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def fake_user_name():
    first_names = ["john", "jane", "bob", "alice", "charlie", "diana", "eve", "frank"]
    last_names = ["smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis"]
    # earlier names are more common, so a few users dominate like in real environments
    weights = range(len(first_names), 0, -1)
    return f"{random.choices(first_names, weights)[0]}.{random.choices(last_names, weights)[0]}"

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
    levels = {'INFO': 75, 'DEBUG': 15, 'WARN': 7, 'ERROR': 3}
    return f"{timestamp} [{weighted_choice(levels)}] {fake_file_path()}: {fake_sentence()}"

def generate_security_logs(timestamp):
    return f"{timestamp} User {fake_user_name()} login attempt from {fake_ipv4()}"

def generate_network_logs(timestamp):
    protocols = {'TCP': 50, 'HTTPS': 25, 'UDP': 15, 'HTTP': 7, 'ICMP': 3}
    dest_ports = {443: 45, 80: 20, 53: 15, 22: 8, 3306: 5, 8080: 5, 3389: 2}
    actions = {'ACCEPT': 88, 'DROP': 8, 'REJECT': 4}
    return f"{timestamp} {weighted_choice(protocols)} {fake_ipv4()}:{random.randint(1024, 65535)} -> {fake_ipv4()}:{weighted_choice(dest_ports)} {weighted_choice(actions)}"

def generate_docker_logs(timestamp):
    containers = {'web-app': 35, 'api-server': 25, 'nginx': 20, 'redis': 12, 'database': 8}
    actions = {'started': 40, 'stopped': 25, 'pulled': 15, 'restarted': 15, 'failed': 5}
    return f"{timestamp} Container {weighted_choice(containers)}-{fake_uuid4()[:8]} {weighted_choice(actions)}"

def generate_database_logs(timestamp):
    operations = {'SELECT': 70, 'INSERT': 15, 'UPDATE': 10, 'DELETE': 4, 'CREATE': 0.7, 'DROP': 0.3}
    # log-normal: most queries take a few ms, with a long tail of slow ones
    return f"{timestamp} {weighted_choice(operations)} query executed on table {fake_word()} by user {fake_user_name()} - {int(random.lognormvariate(2.5, 1.2)) + 1}ms"

def generate_system_logs(timestamp):
    processes = {'systemd': 30, 'cron': 25, 'ssh': 20, 'kernel': 15, 'sudo': 10}
    return f"{timestamp} {weighted_choice(processes)}[{random.randint(1000, 9999)}]: {fake_sentence()}"

def generate_api_logs(timestamp):
    endpoints = {'/api/products': 35, '/api/users': 25, '/api/orders': 20, '/api/auth': 12, '/api/payments': 8}
    methods = {'GET': 70, 'POST': 20, 'PUT': 7, 'DELETE': 3}
    statuses = {200: 90, 404: 3, 400: 3, 401: 2.5, 500: 1.5}
    return f"{timestamp} {weighted_choice(methods)} {weighted_choice(endpoints)} from {fake_ipv4()} - Response: {weighted_choice(statuses)} - {int(random.lognormvariate(4, 0.6)) + 1}ms"

def generate_error_logs(timestamp):
    errors = {'ValidationError': 35, 'ConnectionTimeout': 25, 'AuthenticationError': 20, 'NullPointerException': 15, 'OutOfMemoryError': 5}
    return f"{timestamp} {weighted_choice(errors)} in {fake_file_path()}:{random.randint(1, 1000)} - {fake_sentence()}"

def generate_metrics_logs(timestamp):
    # (mean, stddev) of typical usage per resource
    metrics = {'CPU': (35, 15), 'Memory': (60, 12), 'Disk': (55, 15), 'Network': (20, 10)}
    metric = random.choice(list(metrics))
    usage = min(99, max(1, round(random.gauss(*metrics[metric]))))
    return f"{timestamp} {metric} usage: {usage}% - Host: {fake_hostname()}"

log_generators = {
    "app": generate_app_logs,
    "security": generate_security_logs,
    "network": generate_network_logs,
    "docker": generate_docker_logs,
    "database": generate_database_logs,
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
