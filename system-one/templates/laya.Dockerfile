# Build from the skill root after staging a pinned checkpoint in model/.
# Pass PYTHON_IMAGE as a digest-pinned image and LAYA_VERSION as an exact release.
ARG PYTHON_IMAGE
FROM ${PYTHON_IMAGE}
ARG LAYA_VERSION
RUN test -n "$LAYA_VERSION" && python -m pip install --no-cache-dir "laya==$LAYA_VERSION"
WORKDIR /service
COPY scripts/laya_service.py scripts/systemone_probe.py ./
COPY model/ /service/model/
RUN python -m py_compile laya_service.py systemone_probe.py && \
    test -f /service/model/rl_agent_config.json && test -f /service/model/model.safetensors
ENV PYTHONUNBUFFERED=1
EXPOSE 8788
CMD ["python", "laya_service.py", "--model-path", "/service/model", "--host", "0.0.0.0", "--port", "8788", "--device", "cpu"]
