const TelegramBot = require('node-telegram-bot-api');

const token = '7991600316:AAGYrCc2N3n7pZv7j7hOjT2VXQhzAwWVGN4';

const bot = new TelegramBot(token, { polling: true });

bot.on('message', (msg) => {
  console.log('Chat ID:', msg.chat.id);
  bot.sendMessage(msg.chat.id, 'Got your message! Your chat ID is logged in the console.');
});
