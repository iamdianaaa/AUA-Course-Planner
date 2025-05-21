import { Alert, Paper, Stack, Box } from "@mui/material";
import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import type { ChatMessage } from "../api/chat";
import { useStartChat, useContinueChat, useResetChat } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";
import { UserIdPrompt } from "./UserIdPrompt";
import { Button } from "./Button";
import { LoadingBubble } from "./LoadingBubble";

export const ChatWindow: React.FC = () => {
  const [userId, setUserId] = useState<string | null>(null);
  const [started, setStarted] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<string | null>(null);

  const start = useStartChat();
  const cont = useContinueChat();
  const reset = useResetChat();

  const { data: messages = [] } = useQuery<ChatMessage[]>({
    queryKey: ["chat", userId],
    queryFn: () => [],
    enabled: false,
    initialData: [],
  });

  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, start.isPending, cont.isPending, errorMsg]);

  const sendMessage = (msg: string): void => {
    if (!userId) return;

    setErrorMsg(null);
    setLastMessage(msg);

    if (started) {
      cont.mutate(
        { user_id: userId, message: msg },
        {
          onError: (err: Error) => {
            setErrorMsg(err.message);
          },
        }
      );
    } else {
      start.mutate(
        { user_id: userId, user_input: msg },
        {
          onError: (err: Error) => {
            setErrorMsg(err.message);
          },
          onSuccess: () => {
            setStarted(true);
          },
        }
      );
    }
  };

  const retry = (): void => {
    if (lastMessage) {
      sendMessage(lastMessage);
    }
  };

  if (!userId) {
    return <UserIdPrompt onSubmit={(id: string) => setUserId(id)} />;
  }

  return (
    <Paper
      elevation={3}
      sx={{ p: 2, height: "80vh", display: "flex", flexDirection: "column" }}
    >
      <Stack spacing={1} flex={1} overflow="auto" mb={2}>
        {messages.map((message: ChatMessage, index: number) => (
          <MessageBubble key={index} message={message} />
        ))}

        {(start.isPending || cont.isPending) && <LoadingBubble />}

        {errorMsg && (
          <Alert
            severity="error"
            action={
              <Button size="small" onClick={retry}>
                Retry
              </Button>
            }
            sx={{ alignSelf: "flex-start" }}
          >
            {errorMsg}
          </Alert>
        )}

        <div ref={bottomRef} />
      </Stack>

      <MessageInput disabled={cont.isPending} onSend={sendMessage} />

      <Box mt={1} textAlign="right">
        <Button
          size="small"
          onClick={() => {
            setErrorMsg(null);
            reset.mutate(
              { user_id: userId },
              {
                onError: (err: Error) => {
                  setErrorMsg(err.message);
                },
                onSuccess: () => {
                  setStarted(false);
                  setUserId(null);
                },
              }
            );
          }}
        >
          Reset
        </Button>
      </Box>
    </Paper>
  );
};
