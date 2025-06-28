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

    let definition = null;
    for (const meaning of entry.meanings) {
      for (const def of meaning.definitions) {
        if (def.definition) {
          definition = {
            word: entry.word,
            partOfSpeech: meaning.partOfSpeech,
            definition: def.definition,
            example: def.example || 'No example found.',
            synonyms: def.synonyms || [],
            antonyms: def.antonyms || [],
            audio: entry.phonetics.find(p => p.audio)?.audio || null
          };
          break;
        }
      }
      if (definition) break;
    }

    return definition || null;
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
  message += `*Synonyms:* ${wordData.synonyms.length > 0 ? wordData.synonyms.slice(0, 5).join(', ') : 'None found.'}\n`;
  message += `*Antonyms:* ${wordData.antonyms.length > 0 ? wordData.antonyms.slice(0, 5).join(', ') : 'None found.'}\n`;

  if (wordData.audio) {
    message += `🔊 [Pronunciation](${wordData.audio})\n`;
  }

  bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
  console.log(`Sent word of the day: ${wordData.word}`);
}

console.log('Bot started and scheduled for daily message.');

cron.schedule('30 3 * * *', () => {
  sendWordOfTheDay();
});

sendWordOfTheDay();