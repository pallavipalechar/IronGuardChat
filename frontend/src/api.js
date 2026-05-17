import axios from "axios";

export const sendMessage = (message) => {
  return axios.post("http://127.0.0.1:5000/chat", { message });
};