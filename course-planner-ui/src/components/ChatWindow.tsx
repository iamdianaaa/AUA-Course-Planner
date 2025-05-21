import { Paper, Stack, Box } from "@mui/material";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type { ChatMessage } from "../api/chat";
import { useStartChat, useContinueChat, useResetChat } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";
import { UserIdPrompt } from "./UserIdPrompt";
import { Button } from "./Button";
import { LoadingBubble } from "./LoadingBubble";

export const ChatWindow = () => {
  const [userId, setUserId] = useState<string | null>(null);
  const [started, setStarted] = useState(false);

  const start = useStartChat();
  const cont = useContinueChat();
  const reset = useResetChat();

  const { data: messages = [] } = useQuery<ChatMessage[]>({
    queryKey: ["chat", userId],
    queryFn: () => [],
    enabled: false,
    initialData: [],
  });

  const sendMessage = (msg: string) => {
    if (userId) {
      if (started) {
        cont.mutate({ user_id: userId, message: msg });
      } else {
        start.mutate({ user_id: userId, user_input: msg });
        setStarted(true);
      }
    }
  };

  if (!userId) {
    return (
      <UserIdPrompt
        onSubmit={(id) => {
          setUserId(id);
        }}
      />
    );
  }

  return (
    <Paper
      elevation={3}
      sx={{ p: 2, height: "80vh", display: "flex", flexDirection: "column" }}
    >
      <Stack spacing={1} flex={1} overflow="auto" mb={2}>
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {(start.isPending || cont.isPending) && <LoadingBubble />}
      </Stack>

      <MessageInput
        disabled={cont.isPending}
        onSend={(msg) => sendMessage(msg)}
      />

      <Box mt={1} textAlign="right">
        <Button
          size="small"
          onClick={() => {
            reset.mutate({ user_id: userId });
            setStarted(false);
            setUserId(null);
          }}
        >
          Reset
        </Button>
      </Box>
    </Paper>
  );
};
