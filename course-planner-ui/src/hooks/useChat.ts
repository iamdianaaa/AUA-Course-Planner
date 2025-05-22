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

interface ChatContext {
  previous: ChatMessage[];
}

export const useStartChat = () => {
  const qc = useQueryClient();

  return useMutation<ChatResponse, Error, StartChatPayload, ChatContext>({
    onMutate: async (payload) => {
      await qc.cancelQueries({ queryKey: ["chat", payload.user_id] });
      const previous =
        qc.getQueryData<ChatMessage[]>(["chat", payload.user_id]) ?? [];
      qc.setQueryData<ChatMessage[]>(
        ["chat", payload.user_id],
        [...previous, { role: "user", message: payload.user_input }]
      );
      return { previous };
    },
    mutationFn: (payload) => startChat(payload),
    onError: (_err, payload, context) => {
      if (context?.previous) {
        qc.setQueryData<ChatMessage[]>(
          ["chat", payload.user_id],
          context.previous
        );
      }
    },
    onSuccess: (data, payload) => {
      qc.setQueryData<ChatMessage[]>(["chat", payload.user_id], (old = []) => [
        ...old,
        { role: "model", message: data.response },
      ]);
    },
    onSettled: (_data, _err, payload) => {
      qc.invalidateQueries({ queryKey: ["chat", payload.user_id] });
    },
  });
};

export const useContinueChat = () => {
  const qc = useQueryClient();

  return useMutation<ChatResponse, Error, ContinueChatPayload, ChatContext>({
    onMutate: async (payload) => {
      await qc.cancelQueries({ queryKey: ["chat", payload.user_id] });
      const previous =
        qc.getQueryData<ChatMessage[]>(["chat", payload.user_id]) ?? [];
      qc.setQueryData<ChatMessage[]>(
        ["chat", payload.user_id],
        [...previous, { role: "user", message: payload.message }]
      );
      return { previous };
    },
    mutationFn: (payload) => continueChat(payload),
    onError: (_err, payload, context) => {
      if (context?.previous) {
        qc.setQueryData<ChatMessage[]>(
          ["chat", payload.user_id],
          context.previous
        );
      }
    },
    onSuccess: (data, payload) => {
      qc.setQueryData<ChatMessage[]>(["chat", payload.user_id], (old = []) => [
        ...old,
        { role: "model", message: data.response },
      ]);
    },
    onSettled: (_data, _err, payload) => {
      qc.invalidateQueries({ queryKey: ["chat", payload.user_id] });
    },
  });
};

export const useResetChat = () => {
  const qc = useQueryClient();

  return useMutation<unknown, Error, ResetChatPayload>({
    mutationFn: (payload) => resetChat(payload),
    onSuccess: (_data, payload) => {
      qc.removeQueries({ queryKey: ["chat", payload.user_id] });
    },
  });
};
