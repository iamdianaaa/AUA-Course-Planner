import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api",
  headers: { "Content-Type": "application/json" },
});

export interface ChatMessage {
  role: "user" | "model";
  message: string;
}

export interface ChatResponse {
  response: string;
}

export interface StartChatPayload {
  user_id: string;
  user_input: string;
}
export interface ContinueChatPayload {
  user_id: string;
  message: string;
}
export interface ResetChatPayload {
  user_id: string;
}

export const startChat = (data: StartChatPayload) =>
  api.post<ChatResponse>("/start_chat", data).then((r) => r.data);
export const continueChat = (data: ContinueChatPayload) =>
  api.post<ChatResponse>("/continue_chat", data).then((r) => r.data);
export const resetChat = (data: ResetChatPayload) =>
  api.post("/reset_chat", data);
