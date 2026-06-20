# sandcastle-py sandbox image — Python-first.
#
# Node is present for ONE reason: to run the `pi` coding agent CLI inside the
# sandbox. The sandcastle-py engine, orchestration loop, and packaging are pure
# Python and never touch Node. Env injection uses the standalone (Node-free)
# dotenvx binary, not the npm package.

FROM node:22-bookworm AS node_runtime
FROM ghcr.io/astral-sh/uv:latest AS uv_runtime
FROM python:3-bookworm

# System dependencies.
RUN apt-get update && apt-get install -y \
  build-essential \
  ca-certificates \
  git \
  curl \
  jq \
  && rm -rf /var/lib/apt/lists/*

# Copy Node 22 from the official image — used ONLY to run the `pi` agent CLI.
COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node_runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
  && ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
  && ln -sf ../lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack

# uv/uvx for Python dependency management in the target repo.
COPY --from=uv_runtime /uv /usr/local/bin/uv
COPY --from=uv_runtime /uvx /usr/local/bin/uvx
RUN python -m pip install --upgrade pip setuptools wheel

# dotenvx as a standalone, Node-free binary (decrypts committed encrypted .env at runtime).
RUN curl -sfS https://dotenvx.sh | sh

# GitHub CLI.
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && apt-get update && apt-get install -y gh \
  && rm -rf /var/lib/apt/lists/*

# `sandcastle docker build-image` injects host UID/GID so bind-mounted files share an owner.
ARG AGENT_UID=1000
ARG AGENT_GID=1000

RUN if ! getent group "$AGENT_GID" > /dev/null; then groupadd -o -g "$AGENT_GID" agent; fi \
  && useradd -o -u "$AGENT_UID" -g "$AGENT_GID" -d /home/agent -m -s /bin/bash agent

# Install the `pi` coding agent globally via pnpm (the sole sanctioned Node usage).
ENV PNPM_HOME=/usr/local/share/pnpm
ENV COREPACK_HOME=/usr/local/share/corepack
ENV PATH=$PNPM_HOME/bin:$PNPM_HOME:$PATH

RUN mkdir -p "$PNPM_HOME/bin" "$COREPACK_HOME" \
  && corepack enable \
  && corepack prepare pnpm@11.5.2 --activate \
  && pnpm config set global-bin-dir "$PNPM_HOME/bin" \
  && pnpm add --global --ignore-scripts @earendil-works/pi-coding-agent \
  && chown -R "$AGENT_UID:$AGENT_GID" "$PNPM_HOME" "$COREPACK_HOME"

# Git identity for agent commits, set at runtime from these env vars by the loop.
ENV SANDCASTLE_GIT_USER_NAME="" \
  SANDCASTLE_GIT_USER_EMAIL=""

# Persist Pi OAuth + sessions across container restarts (bind-mounted by the loop).
ENV PI_CODING_AGENT_DIR=/home/agent/.pi/agent \
  PI_CODING_AGENT_SESSION_DIR=/home/agent/.pi/agent/sessions \
  PI_OAUTH_CALLBACK_HOST=0.0.0.0

RUN mkdir -p "$PI_CODING_AGENT_SESSION_DIR" \
  && chown -R "$AGENT_UID:$AGENT_GID" /home/agent/.pi

# Bind-mounted worktrees are owned by the host UID; trust them so git/gh work in-sandbox
# (avoids git's "detected dubious ownership" guard). Written as root before dropping user.
RUN git config --system --add safe.directory '*'

# Authenticate `git push` over HTTPS using GH_TOKEN. GH_TOKEN authenticates the gh API
# (gh pr create) but NOT git push; this credential helper feeds the token to git at
# runtime so the merge phase can push branches. ($GH_TOKEN expands when git runs it.)
RUN git config --system credential.helper \
  '!f() { test "$1" = get && echo username=x-access-token && echo "password=$GH_TOKEN"; }; f'

USER ${AGENT_UID}:${AGENT_GID}

WORKDIR /home/agent

# sandcastle-py bind-mounts the git worktree at /home/agent/workspace and runs there.
ENTRYPOINT ["sleep", "infinity"]
