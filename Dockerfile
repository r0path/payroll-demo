FROM node:18-alpine
LABEL app="payment-app-1"
WORKDIR /app
COPY . .
CMD ["node", "index.js"]
