import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
  timeout: 60000,
});

export async function fetchNews({ limit = 20, offset = 0 } = {}) {
  const { data } = await api.get("/news", { params: { limit, offset } });
  return data;
}

export async function askQuestion(question) {
  const { data } = await api.post("/ask", { question });
  return data;
}
