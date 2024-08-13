FROM node:20-alpine

WORKDIR /opentest

COPY ./data /opentest

RUN npm install opentest -g && \
    npm cache verify

RUN chown node:node ./

USER node

EXPOSE 3000

CMD [ "opentest", "server" ]