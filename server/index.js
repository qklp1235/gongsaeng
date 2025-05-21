require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Configuration, OpenAIApi } = require('openai');

const app = express();
app.use(cors());
app.use(express.json());

const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY
});
const openai = new OpenAIApi(configuration);

app.post('/api/translate', async (req, res) => {
    try {
        const { text, targetLanguage } = req.body;
        if (!text || !targetLanguage) {
            return res.status(400).json({ error: 'Missing text or targetLanguage' });
        }
        const prompt = `Translate the following medical text to ${targetLanguage}.\nKeep medical terms accurate and maintain the original meaning:\n"${text}"`;
        const completion = await openai.createChatCompletion({
            model: "gpt-3.5-turbo",
            messages: [
                {
                    role: "system",
                    content: "You are a medical translator. Translate the given text accurately, maintaining medical terminology."
                },
                {
                    role: "user",
                    content: prompt
                }
            ]
        });
        res.json({
            translatedText: completion.data.choices[0].message.content.trim()
        });
    } catch (error) {
        console.error('Translation error:', error);
        res.status(500).json({ error: 'Translation failed' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 