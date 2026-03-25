# GlassBox Runner Container
# Playwright + Xvfb + x11vnc + noVNC
FROM mcr.microsoft.com/playwright:v1.50.0-noble

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    fluxbox \
    websockify \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# noVNC
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC \
    && ln -s /opt/noVNC/vnc_lite.html /opt/noVNC/index.html

WORKDIR /app

COPY apps/runner/package.json apps/runner/tsconfig.json ./
RUN npm install

COPY apps/runner/src ./src
RUN npx tsc

# Startup script
COPY infra/scripts/runner-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3001 5900 6080

ENTRYPOINT ["/entrypoint.sh"]
