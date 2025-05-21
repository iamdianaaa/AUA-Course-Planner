import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Container, CssBaseline, Typography } from "@mui/material";
import { ChatWindow } from "./components/ChatWindow";

const qc = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={qc}>
      <CssBaseline />
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          AUA Course Planner Chat
        </Typography>
        <ChatWindow />
      </Container>
    </QueryClientProvider>
  );
}
