import axios from "axios";

// O free tier do ngrok intercepta requisicoes de navegador com uma pagina de
// aviso; o header abaixo entrega a resposta da API direto.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 60000,
  headers: { "ngrok-skip-browser-warning": "true" },
});

// A API roda em um homelab: quando ele esta desligado nao ha resposta HTTP, e
// quando o tunel esta no ar sem o backend atras dele vem um erro de gateway.
export function isApiOffline(error) {
  const status = error?.response?.status;
  return status === undefined || status === 502 || status === 503 || status === 504;
}

export async function checkHealth() {
  const { data } = await api.get("/health", { timeout: 8000 });
  return data;
}

export async function fetchNews({ limit = 20, offset = 0 } = {}) {
  const { data } = await api.get("/news", { params: { limit, offset } });
  return data;
}

export async function askQuestion(question) {
  const { data } = await api.post("/ask", { question });
  return data;
}
