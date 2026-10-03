FROM node:24-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 git curl ca-certificates ripgrep build-essential && rm -rf /var/lib/apt/lists/*
RUN npm install -g @openai/codex@0.160.0 @github/copilot@1.0.91 @earendil-works/pi-coding-agent@1.0.0 @opencode/cli@2.0.22 @google/gemini-cli@0.62.0 openclaw@2026.9.8 @anthropic-ai/claude-code@2.1.286
RUN usermod --login evaluator --home /home/evaluator --move-home node
RUN mkdir -p /opt/cursor/bin && curl -fL --retry 3 https://downloads.cursor.com/lab/2026.10.01-e373342/linux/x64/agent-cli-package.tar.gz -o /tmp/cursor.tar.gz && echo 'a79726c6e644520e993970be4c45775a6889802b67abe461a677a53219ae28e8  /tmp/cursor.tar.gz' | sha256sum -c - && tar -xzf /tmp/cursor.tar.gz -C /opt/cursor/bin --strip-components=1 && rm /tmp/cursor.tar.gz
COPY entrypoint.py /opt/eval-entrypoint.py
ENV HOME=/home/evaluator PATH=/opt/cursor/bin:/usr/local/bin:/usr/bin:/bin CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 COPILOT_AUTO_UPDATE=false
USER evaluator
WORKDIR /workspace
ENTRYPOINT ["python3", "/opt/eval-entrypoint.py"]
