FROM node:10

# Copy files
COPY ./src/ /src/

WORKDIR /src
RUN npm install
CMD ["npm","start"]
