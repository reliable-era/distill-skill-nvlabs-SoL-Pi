FROM node:22-bookworm-slim
ARG CLAUDE_CODE_VERSION=2.1.286
RUN apt-get update && apt-get install -y --no-install-recommends python3 git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}
RUN useradd --create-home validator
COPY --chown=validator:validator .claude-plugin /plugin/.claude-plugin
COPY --chown=validator:validator skills /plugin/skills
COPY --chown=validator:validator tests/scripts/validate_plugin.py /plugin/tests/scripts/validate_plugin.py
USER validator
WORKDIR /plugin
ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
CMD ["python3", "tests/scripts/validate_plugin.py"]
