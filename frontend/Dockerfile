# Stage 0, "build-stage", based on Bun, to build and compile the frontend
FROM oven/bun:1 AS build-stage

WORKDIR /app

COPY package.json bun.lock /app/
COPY packages/shared/package.json /app/packages/shared/
COPY frontend/package.json /app/frontend/
COPY extension/package.json /app/extension/

RUN bun install --frozen-lockfile

COPY packages/shared /app/packages/shared
COPY frontend /app/frontend

WORKDIR /app/frontend
ARG VITE_API_URL

RUN bun run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/frontend/dist/ /usr/share/nginx/html

COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./frontend/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
