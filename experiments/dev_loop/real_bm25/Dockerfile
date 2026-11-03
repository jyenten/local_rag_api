FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 HOME=/tmp OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
COPY requirements.txt /opt/bm25/requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/bm25/requirements.txt
COPY vendor /opt/bm25/vendor
COPY benchmark.py /opt/bm25/benchmark.py
COPY container_entry.py /opt/dev-loop/container_entry.py
RUN chmod -R a-w /opt/bm25 /opt/dev-loop
USER 10001:10001
WORKDIR /work
ENTRYPOINT ["python", "-I", "/opt/dev-loop/container_entry.py"]
