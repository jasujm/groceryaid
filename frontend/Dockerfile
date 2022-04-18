FROM node:16-bullseye AS builder

WORKDIR /usr/src/app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.21

EXPOSE 80
COPY --from=builder /usr/src/app/nginx/conf.d /etc/nginx/conf.d/
COPY --from=builder /usr/src/app/build /var/www/groceryaid/
