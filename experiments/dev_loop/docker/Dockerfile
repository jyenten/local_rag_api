FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONUNBUFFERED=1 HOME=/tmp

COPY docker/requirements.txt /opt/dev-loop/requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/dev-loop/requirements.txt

COPY adapters.py /opt/dev-loop/adapters.py
COPY tasks.py /opt/dev-loop/tasks.py
COPY checks/ /opt/dev-loop/checks/
COPY docker/container_entry.py /opt/dev-loop/container_entry.py
RUN chmod -R a-w /opt/dev-loop

USER 10001:10001
WORKDIR /work
ENTRYPOINT ["python", "-I", "/opt/dev-loop/container_entry.py"]
