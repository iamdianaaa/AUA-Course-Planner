import { Box, Typography } from "@mui/material";
import { useState } from "react";
import { Input } from "./Input";
import { Button } from "./Button";

interface Props {
  onSubmit: (userId: string) => void;
}

export const UserIdPrompt = ({ onSubmit }: Props) => {
  const [id, setId] = useState("");
  const [error, setError] = useState("");

  const trySubmit = () => {
    if (!id.trim()) {
      setError("Please enter a valid user ID.");
      return;
    }
    onSubmit(id.trim());
  };

  return (
    <Box textAlign="center" p={2}>
      <Typography variant="h6" gutterBottom>
        Enter your user ID
      </Typography>
      <Input
        value={id}
        onChange={(e) => {
          setId(e.target.value);
          setError("");
        }}
        helperText={error}
        error={!!error}
        placeholder="e.g. user_123"
      />
      <Box mt={2}>
        <Button onClick={trySubmit}>Start Chat</Button>
      </Box>
    </Box>
  );
};
