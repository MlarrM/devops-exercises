FROM node:20.12.0-bookworm-slim

WORKDIR /simplefolio

COPY ./simplefolio /simplefolio
#TODO: зависимости

RUN yarn \
    && yarn cache clean

CMD ["yarn", "start"]