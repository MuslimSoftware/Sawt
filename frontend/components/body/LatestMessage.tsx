import { useChat } from "@/contexts/ChatContext";
import { useMemo } from "react";
import { colors } from "@/theme/colors";

interface LatestMessageProps {
    role: "user" | "ai";
}

export const LatestMessage = ({ role }: LatestMessageProps) => {
    const { messages } = useChat();
    
    const latestMessage = useMemo(() => 
        messages.findLast(message => message.role === role)?.content, 
        [messages, role]
    );

    return (
        <div 
            style={{
                width: "clamp(250px, 20vw, 400px)",
                height: "100vh",
                position: "relative",
                overflow: "auto",
                display: "flex",
                justifyContent: "center",
                alignItems: "flex-start",
                padding: "50vh 20px 20px 20px",
                boxSizing: "border-box",
                scrollbarWidth: "none",
                msOverflowStyle: "none",
            }}
        >
            {/* Text content */}
            <p style={{
                color: colors.text.primary,
                fontSize: "clamp(0.9rem, 1.1rem, 1.3rem)",
                lineHeight: "1.6",
                textAlign: "center",
                margin: 0,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                maxWidth: "100%",
                fontFamily: "system-ui, -apple-system, sans-serif",
            }}>
                {latestMessage || ""}
            </p>
            
            {/* Hide scrollbar for Webkit browsers */}
            <style jsx>{`
                div::-webkit-scrollbar {
                    display: none;
                }
            `}</style>
        </div>
    );
};