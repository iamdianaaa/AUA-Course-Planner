// src/hooks/useChat.ts
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  startChat,
  continueChat,
  resetChat,
  type StartChatPayload,
  type ContinueChatPayload,
  type ResetChatPayload,
  type ChatResponse,
  type ChatMessage,
} from "../api/chat";

export const useStartChat = () => {
  const qc = useQueryClient();

  return useMutation<ChatResponse, Error, StartChatPayload>({
    mutationFn: (payload) => {
      qc.setQueryData<ChatMessage[]>(
        ["chat", payload.user_id],
        [{ role: "user", message: payload.user_input }]
      );
      return startChat(payload);
    },
    onSuccess(data, payload) {
      qc.setQueryData<ChatMessage[]>(["chat", payload.user_id], (old = []) => [
        ...old,
        { role: "model", message: data.response },
      ]);
    },
  });
};

export const useContinueChat = () => {
  const qc = useQueryClient();

  return useMutation<ChatResponse, Error, ContinueChatPayload>({
    mutationFn: (payload) => {
      qc.setQueryData<ChatMessage[]>(["chat", payload.user_id], (old = []) => [
        ...old,
        { role: "user", message: payload.message },
      ]);
      return continueChat(payload);
    },
    onSuccess(data, payload) {
      qc.setQueryData<ChatMessage[]>(["chat", payload.user_id], (old = []) => [
        ...old,
        { role: "model", message: data.response },
      ]);
    },
  });
};

export const useResetChat = () => {
  const qc = useQueryClient();

  return useMutation<unknown, Error, ResetChatPayload>({
    mutationFn: (payload) => resetChat(payload),
    onSuccess(_, payload) {
      qc.removeQueries({ queryKey: ["chat", payload.user_id] });
    },
  });
};
