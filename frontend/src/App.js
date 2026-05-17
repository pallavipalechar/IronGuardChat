import React from "react";
import Chat from "./chat";
import "./styles.css";

function App() {
  return (
    <div>
     <div className="logo">
     <h1>IronGuard Chatbot</h1>
     </div>

      <div className="chat-wrapper">
        <Chat />
      </div>
    </div>
  );
}


export default App;
