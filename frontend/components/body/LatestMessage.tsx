import { useChat } from "@/contexts/ChatContext";
import { useMemo, useRef, useEffect } from "react";
import { colors } from "@/theme/colors";

interface LatestMessageProps {
    role: "user" | "ai";
}

export const LatestMessage = ({ role }: LatestMessageProps) => {
    const { messages } = useChat();
    const containerRef = useRef<HTMLDivElement>(null);
    
    const latestMessage = useMemo(() => 
        messages.findLast(message => message.role === role)?.content, 
        [messages, role]
    );

    // Auto-scroll text to center when it's too long
    useEffect(() => {
        if (containerRef.current && latestMessage) {
            const container = containerRef.current;
            const textElement = container.querySelector('p');
            
            if (textElement) {
                // If text is taller than container, scroll to center it
                if (textElement.scrollHeight > container.clientHeight) {
                    const scrollToMiddle = (textElement.scrollHeight - container.clientHeight) / 2;
                    container.scrollTop = scrollToMiddle;
                } else {
                    // Reset scroll position for shorter text
                    container.scrollTop = 0;
                }
            }
        }
    }, [latestMessage]);

    return (
        <div 
            ref={containerRef}
            style={{
                width: "20vw",
                height: "100vh",
                position: "relative",
                overflow: "auto",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                padding: "20px",
                boxSizing: "border-box",
                scrollbarWidth: "none",
                msOverflowStyle: "none",
            }}
        >
            {/* Top gradient fade */}
            <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: "20%",
                background: `linear-gradient(to bottom, ${colors.background.primary}, transparent)`,
                zIndex: 2,
                pointerEvents: "none",
            }} />
            
            {/* Bottom gradient fade */}
            <div style={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                height: "20%",
                background: `linear-gradient(to top, ${colors.background.primary}, transparent)`,
                zIndex: 2,
                pointerEvents: "none",
            }} />
            
            {/* Text content */}
            <p style={{
                color: colors.text.primary,
                fontSize: "1.1rem",
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