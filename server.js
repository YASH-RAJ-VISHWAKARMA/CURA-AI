// server.js
import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

// Replace these with your real values
const WHATSAPP_URL = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages";
const TOKEN = "YOUR_ACCESS_TOKEN";

// send message via WhatsApp Cloud API
// 
async function sendMessage(){
  const selected = $('#symptomSelect').val(); // array of symptoms

  if (!selected || selected.length === 0) {
    addBotBubble("⚠ Please select at least one symptom.");
    return;
  }

  // Show user’s selection as bubble
  addUserBubble(selected.map(s => s.replace(/_/g,' ')).join(', '));

  // Clear selection
  $('#symptomSelect').val(null).trigger('change');

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({message: selected})   // send as array, not just string
    });

    const data = await res.json();
    if (data.error) {
      addBotBubble("⚠ " + data.error);
    } else {
      let html = "<b>Top predictions:</b><br>";
      data.results.forEach(r => {
        html += `• <b>${r.disease}</b> — ${r.confidence.toFixed(2)}% (<i>${r.doctor}</i>)<br>`;
      });
      addBotBubble(html);
      speak(html);
    }
  } catch (e) {
    addBotBubble("⚠ Error connecting to server.");
    console.error(e);
  }
}


// webhook to receive messages from WhatsApp
app.post("/webhook/whatsapp", async (req, res) => {
  try {
    const data = req.body;
    // verify structure (may vary based on setup)
    if (data.entry && data.entry[0].changes && data.entry[0].changes[0].value.messages) {
      const message = data.entry[0].changes[0].value.messages[0];
      const from = message.from;
      const text = (message.text && message.text.body) ? message.text.body : "";

      console.log("WhatsApp incoming:", from, text);

      // forward to Flask AI
      const flaskRes = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const flaskJson = await flaskRes.json();

      // reply back to user (send concise text)
      const replyText = flaskJson.reply || "Sorry, couldn't compute prediction.";
      await sendMessage(from, replyText);
    }
    res.sendStatus(200);
  } catch (err) {
    console.error("Error in webhook:", err);
    res.sendStatus(500);
  }
});

app.listen(3000, () => console.log("WhatsApp gateway running on http://localhost:3000"));
