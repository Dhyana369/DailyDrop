require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const cron = require('node-cron');

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.CHAT_ID;

const bot = new TelegramBot(token, { polling: false });

async function getRandomWord() {
  try {
    const res = await axios.get('https://random-word-api.herokuapp.com/word');
    return res.data[0];
  } catch (err) {
    console.error('Error fetching random word:', err);
    return null;
  }
}

async function getWordDefinition(word) {
  try {
    const res = await axios.get(`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`);
    const entry = res.data[0];
    const meaning = entry.meanings[0];
    const definition = meaning.definitions[0];

    return {
      word: entry.word,
      partOfSpeech: meaning.partOfSpeech,
      definition: definition.definition,
      example: definition.example || 'No example found.',
      synonyms: definition.synonyms || [],
      antonyms: definition.antonyms || [],
      audio: entry.phonetics.find(p => p.audio)?.audio || null
    };
  } catch (err) {
    console.error('No definitions found for:', word);
    return null;
  }
}

async function sendWordOfTheDay() {
  const word = await getRandomWord();
  if (!word) return;

  const wordData = await getWordDefinition(word);
  if (!wordData) {
    console.log(`Skipping word (no definitions): ${word}`);
    return;
  }

  let message = `🧠 *Word of the Day*\n\n`;
  message += `*${wordData.word}* (${wordData.partOfSpeech})\n`;
  message += `*Meaning:* ${wordData.definition}\n`;
  message += `*Example:* ${wordData.example}\n`;

  message += `*Synonyms:* ${wordData.synonyms.length > 0 ? wordData.synonyms.join(', ') : 'None found.'}\n`;
  message += `*Antonyms:* ${wordData.antonyms.length > 0 ? wordData.antonyms.join(', ') : 'None found.'}\n`;

  if (wordData.audio) {
    message += `🔊 [Pronunciation](${wordData.audio})\n`;
  }

  bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
  console.log(`Sent word of the day: ${wordData.word}`);
}

console.log('Bot started and scheduled for daily message.');

// Schedule daily at 9 AM IST (adjust if needed)
cron.schedule('30 2 * * *', () => {
  sendWordOfTheDay();
});

// Uncomment this for testing only
// sendWordOfTheDay();
