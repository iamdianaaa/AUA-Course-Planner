/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Typography, Box } from "@mui/material";

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
}) => (
  <Box
    sx={{
      "& :not(pre) > code": { bgcolor: "grey.100", px: 0.5, borderRadius: 0.5 },
    }}
  >
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h2: ({ node, ...props }) => (
          <Typography variant="h6" gutterBottom {...props} />
        ),
        h3: ({ node, ...props }) => (
          <Typography variant="subtitle1" gutterBottom {...props} />
        ),
        p: ({ node, ...props }) => <Typography variant="body1" {...props} />,
        li: ({ node, ...props }) => (
          <li>
            <Typography component="span" variant="body1" {...props} />
          </li>
        ),
        strong: ({ node, ...props }) => (
          <Typography
            component="strong"
            sx={{ fontWeight: "bold" }}
            {...props}
          />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  </Box>
);
