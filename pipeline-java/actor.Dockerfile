FROM node:20-alpine

WORKDIR /opentest

RUN apk update && \
    apk add openjdk8 && \
    apk cache clean

COPY ./data/actor.yaml actor.yaml

RUN npm install opentest -g && \
    npm cache verify

RUN chown node:node ./

USER node

CMD [ "opentest", "actor" ]