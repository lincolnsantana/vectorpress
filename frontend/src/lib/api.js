import axios from "axios";

// O free tier do ngrok intercepta requisicoes de navegador com uma pagina de
// aviso; o header abaixo entrega a resposta da API direto.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 60000,
  headers: { "ngrok-skip-browser-warning": "true" },
});

export async function fetchNews({ limit = 20, offset = 0 } = {}) {
  const { data } = await api.get("/news", { params: { limit, offset } });
  return data;
}

export async function askQuestion(question) {
  const { data } = await api.post("/ask", { question });
  return data;
}
