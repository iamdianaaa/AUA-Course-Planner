FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN yarn install --immutable

COPY . .

CMD ["yarn", "dev"]
