import { Box } from "@mui/material";
import type { ChatMessage } from "../api/chat";
import { MarkdownRenderer } from "./MarkdownRenderer";

export interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble = ({ message }: MessageBubbleProps) => (
  <Box
    sx={{
      alignSelf: message.role === "model" ? "flex-start" : "flex-end",
      bgcolor: message.role === "model" ? "grey.200" : "primary.main",
      color: message.role === "model" ? "text.primary" : "common.white",
      borderRadius: 1,
      p: 1,
      maxWidth: "75%",
    }}
  >
    <MarkdownRenderer content={message.message} />
  </Box>
);
