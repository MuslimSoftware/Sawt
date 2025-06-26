import { useChat } from "@/contexts/ChatContext";
import { useMemo } from "react";

interface LatestMessageProps {
    role: "user" | "ai";
}

export const LatestMessage = ({role}: LatestMessageProps) => {
    const { messages } = useChat();
    const latestMessage = useMemo(() => messages.findLast(message => message.role === role)?.content, [messages, role]);

    return (
        <div style={{
            width: "20vw",
            height: "100%",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",

        }}>
            <p>{latestMessage}</p>
        </div>
    )
}