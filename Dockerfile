FROM node
WORKDIR /usr/src/pelican-server
COPY . .
RUN npm install
EXPOSE 8080
CMD [ "npm", "run", "build" ]