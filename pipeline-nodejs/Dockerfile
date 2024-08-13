FROM node:20.12.0-bookworm-slim

WORKDIR /simplefolio

COPY ./simplefolio /simplefolio

RUN yarn \
    && yarn cache clean

CMD ["yarn", "start"]