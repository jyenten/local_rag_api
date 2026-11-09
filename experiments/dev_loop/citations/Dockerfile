FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 HOME=/tmp
COPY requirements.txt /opt/citations/requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/citations/requirements.txt
COPY checks /opt/citations/checks
COPY probe.py /opt/citations/probe.py
COPY container_entry.py /opt/dev-loop/container_entry.py
RUN chmod -R a-w /opt/citations /opt/dev-loop
USER 10001:10001
WORKDIR /work
ENTRYPOINT ["python", "-I", "/opt/dev-loop/container_entry.py"]
