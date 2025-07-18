import { useChat } from "@/contexts/ChatContext";
import { useMemo } from "react";
import styles from "./LatestMessage.module.css";

interface LatestMessageProps {
    role: "user" | "ai";
}

export const LatestMessage = ({ role }: LatestMessageProps) => {
    const { messages } = useChat();
    
    const latestMessage = useMemo(() => 
        messages.findLast(message => message.role === role)?.content, 
        [messages, role]
    );

    const containerClassName = useMemo(() => {
        return `${styles.container} ${styles[role]}`;
    }, [role]);

    return (
        <div className={containerClassName}>
            {/* Text content */}
            <p className={styles.text}>
                {latestMessage || ""}
            </p>
        </div>
    );
};