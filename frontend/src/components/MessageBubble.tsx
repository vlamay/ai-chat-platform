import React from "react";
import { marked } from "marked";
import type { Message } from "../types";

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === "user";
  const isStreaming = message.id === "streaming";

  const htmlContent = marked(message.content, {
    breaks: true,
    gfm: true,
  });

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-100 rounded-bl-none"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : message.content || isStreaming ? (
          <div
            className="prose dark:prose-invert max-w-none text-sm"
            dangerouslySetInnerHTML={{ __html: htmlContent as string }}
          />
        ) : (
          <div className="flex gap-1 py-1">
            <span className="inline-block w-2 h-2 bg-current rounded-full animate-bounce" />
            <span className="inline-block w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
            <span className="inline-block w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
          </div>
        )}
        <p className="text-xs opacity-75 mt-1">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
};
