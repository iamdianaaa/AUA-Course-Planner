import { Box } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { useState } from "react";
import { Input } from "./Input";
import { Button } from "./Button";

interface Props {
  disabled?: boolean;
  onSend: (msg: string) => void;
}

export const MessageInput = ({ disabled, onSend }: Props) => {
  const [text, setText] = useState("");

  const submit = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setText("");
  };

  return (
    <Box display="flex">
      <Input
        fullWidth
        multiline
        size="small"
        placeholder="Type your message…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
      />
      <Button onClick={submit} disabled={disabled || !text.trim()}>
        <SendIcon />
      </Button>
    </Box>
  );
};
