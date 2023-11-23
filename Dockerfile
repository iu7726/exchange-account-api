FROM nikolaik/python-nodejs:python3.11-nodejs18

MAINTAINER OG_XYZ <OG@OG.XYZ>

RUN mkdir -p /var/www/exchange

WORKDIR /var/www/exchange

COPY . .

RUN pip3 install -r requirements.txt

RUN yarn global add pm2

CMD ["pm2-runtime", "start", "./ecosystem.config.js"]

EXPOSE 8201