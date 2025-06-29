require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const cron = require('node-cron');

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.CHAT_ID;
const bot = new TelegramBot(token, { polling: false });

async function getRandomWord() {
  try {
    const res = await axios.get('https://random-word-api.herokuapp.com/word?number=1');
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

    for (const meaning of entry.meanings) {
      for (const def of meaning.definitions) {
        if (def.definition) {
          return {
            word: entry.word,
            partOfSpeech: meaning.partOfSpeech,
            definition: def.definition,
            example: def.example || 'No example found.',
            synonyms: def.synonyms?.slice(0, 5) || [],
            antonyms: def.antonyms?.slice(0, 5) || [],
            audio: entry.phonetics.find(p => p.audio)?.audio || null
          };
        }
      }
    }

    return null;
  } catch (err) {
    console.error(`No definitions found for: ${word}`);
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
  message += `*Synonyms:* ${wordData.synonyms.length ? wordData.synonyms.join(', ') : 'None found.'}\n`;
  message += `*Antonyms:* ${wordData.antonyms.length ? wordData.antonyms.join(', ') : 'None found.'}\n`;

  if (wordData.audio) {
    message += `🔊 [Pronunciation](${wordData.audio})\n`;
  }

  bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
  console.log(`✅ Sent word of the day: ${wordData.word}`);
}

console.log('🚀 Bot started and scheduled for daily message.');

// Schedule at 8:30 AM IST => 3:00 AM UTC
cron.schedule('0 3 * * *', () => {
  sendWordOfTheDay();
});
