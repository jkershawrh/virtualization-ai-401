FROM registry.access.redhat.com/ubi9/nodejs-22@sha256:90d19cd1a4ba03bcb63c46320862955fc1560511532ee35ff472289bf5fe2276 AS build
WORKDIR /opt/app-root/src
COPY --chown=1001:0 package*.json ./
RUN npm ci
COPY --chown=1001:0 . .
RUN npm run build

FROM cgr.dev/chainguard/nginx@sha256:57e924b3b177cf480ce53cdcad2982b44093494c217d2bc95f2fb5b6a0950a5a
COPY --from=build /opt/app-root/src/dist /usr/share/nginx/html
COPY nginx-main.conf /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/http.d/default.conf
EXPOSE 8080
