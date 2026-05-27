from uvicorn.workers import UvicornWorker

from pr_agent.servers.uvicorn_log_config import LOGGING_CONFIG


class GitlabWebhookUvicornWorker(UvicornWorker):
    # gunicorn imports gitlab_webhook:app directly and never calls start(), so the
    # LOGGING_CONFIG that start() passes to uvicorn.run() is bypassed. Apply it here
    # so GET / health-check access logs stay filtered when running under gunicorn.
    CONFIG_KWARGS = {"loop": "auto", "http": "auto", "log_config": LOGGING_CONFIG}
