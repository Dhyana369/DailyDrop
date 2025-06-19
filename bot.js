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
    const meanings = res.data[0].meanings[0];
    const definitionData = meanings.definitions[0];

    return {
      word: res.data[0].word,
      partOfSpeech: meanings.partOfSpeech,
      definition: definitionData.definition,
      example: definitionData.example || 'No example found.',
      synonyms: definitionData.synonyms || [],
      antonyms: definitionData.antonyms || []
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

  let message = `🧠 Word of the Day\n\n`;
  message += `${wordData.word} (${wordData.partOfSpeech})\n`;
  message += `Meaning: ${wordData.definition}\n`;
  message += `Example: ${wordData.example}\n`;

  if (wordData.synonyms.length > 0) {
    message += `Synonyms: ${wordData.synonyms.join(', ')}\n`;
  } else {
    message += `Synonyms: None found.\n`;
  }

  if (wordData.antonyms.length > 0) {
    message += `Antonyms: ${wordData.antonyms.join(', ')}\n`;
  } else {
    message += `Antonyms: None found.\n`;
  }

  bot.sendMessage(chatId, message);
  console.log(`Sent word of the day: ${wordData.word}`);
}

console.log('Bot started and scheduled for daily message.');

// Schedule daily at 9 AM (adjust timezone if needed)
cron.schedule('30 2 * * *', () => {
  sendWordOfTheDay();
});

// Optional: send immediately for testing (remove later)
// sendWordOfTheDay();
