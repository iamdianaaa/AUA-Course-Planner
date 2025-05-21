import { Box, CircularProgress, Typography } from "@mui/material";

export const LoadingBubble = () => (
  <Box
    sx={{
      alignSelf: "flex-start",
      display: "inline-flex",
      alignItems: "center",
      bgcolor: "grey.200",
      borderRadius: 1,
      p: 1,
      maxWidth: "75%",
    }}
  >
    <CircularProgress size={16} thickness={5} />
    <Typography variant="body2" sx={{ ml: 1 }}>
      Loading…
    </Typography>
  </Box>
);
