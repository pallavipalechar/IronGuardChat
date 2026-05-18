import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5001",
});

export const sendMessage = (message) => {
  return API.post("/chat", { message });
};