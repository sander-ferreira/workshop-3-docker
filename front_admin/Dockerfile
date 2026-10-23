# Front statique : nginx sert simplement les fichiers HTML/CSS/JS
FROM nginx:1.30.6-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY public/ /usr/share/nginx/html/

EXPOSE 80
