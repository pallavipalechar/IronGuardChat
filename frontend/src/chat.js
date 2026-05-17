import React, { useState } from "react";
import { sendMessage } from "./api";

function Chat() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  const handleSend = async () => {
  if (!message) return;
  const currentMessage = message;

  /* ✅ CLEAR IMMEDIATELY */
  setMessage("");
  const userMsg = { role: "user", text: message };

  setChat((prev) => [...prev, userMsg]);

  try {
    const res = await sendMessage(message);

    const botMsg = {
      role: "bot",
      text: res.data.response,
    };

    setChat((prev) => [...prev, botMsg]);

  } catch (error) {

    console.log(error);
  }

  setMessage("");
};

  return (
    <div className="chat-container">
    

      <div className="chat-box">
        {chat.map((c, i) => (
          <div
            key={i}
            className={c.role === "user" ? "user-msg" : "bot-msg"}
          >
            <p>{c.text}</p>

            {c.risk && (
              <small>
                Risk: {c.risk.risk_level} | Blocked:{" "}
                {c.risk.blocked ? "YES" : "NO"}
              </small>
            )}
          </div>
        ))}
      </div>

      <div className="input-box">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
          if (e.key === "Enter") {
          handleSend();
    }
  }}
  placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default Chat;