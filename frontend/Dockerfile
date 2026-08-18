FROM node:20-alpine AS build

ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf.template
COPY docker-entrypoint.d/40-render-nginx-conf.sh /docker-entrypoint.d/40-render-nginx-conf.sh
RUN chmod +x /docker-entrypoint.d/40-render-nginx-conf.sh

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]