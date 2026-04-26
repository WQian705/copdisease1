# Deployment Guide

## Architecture

This project runs as four pieces on one server:

- `Nginx` exposes `80` and optionally `443`
- `Vue dist` is served by `Nginx`
- `SpringBoot` listens on `127.0.0.1:9999`
- `Flask + YOLO` listens on `127.0.0.1:5000`
- `MySQL` listens on `127.0.0.1:3306`

Recommended public exposure:

- Open in the security group: `22`, `80`, `443`
- Do not expose `5000`, `9999`, or `3306` to the public internet

## Frontend

The frontend production build already supports same-origin deployment through `Nginx`.

Build command:

```bash
npm install
npm run build
```

Generated files:

- `dist/`

## SpringBoot

Path:

- `../yolo_cropDisease_detection_springboot`

Important environment variables:

```bash
export SERVER_PORT=9999
export SPRING_DATASOURCE_URL='jdbc:mysql://127.0.0.1:3306/cropdisease?serverTimezone=Asia/Shanghai&useUnicode=true&characterEncoding=UTF-8'
export SPRING_DATASOURCE_USERNAME='root'
export SPRING_DATASOURCE_PASSWORD='123456'
export APP_PUBLIC_BASE_URL='http://YOUR_SERVER_IP_OR_DOMAIN'
export APP_FLASK_BASE_URL='http://127.0.0.1:5000'
```

Build and run:

```bash
./mvnw clean package -DskipTests
java -jar target/Ece-0.0.1-SNAPSHOT.jar
```

## Flask

Path:

- `../yolo_cropDisease_detection_flask`

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Important environment variables:

```bash
export FLASK_HOST='127.0.0.1'
export FLASK_PORT='5000'
export SPRING_API_BASE_URL='http://127.0.0.1:9999'
```

Run:

```bash
python3 main.py
```

## Nginx

Example server config:

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/yolo_cropDisease_detection_vue/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:9999/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /flask/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

## Minimum Bring-up Order

1. Install MySQL and import `cropdisease.sql`
2. Start SpringBoot on `127.0.0.1:9999`
3. Start Flask on `127.0.0.1:5000`
4. Build Vue and place `dist/` under Nginx root
5. Reload Nginx

## Port Summary

- Public: `80`, `443`, `22`
- Internal only: `9999`, `5000`, `3306`
