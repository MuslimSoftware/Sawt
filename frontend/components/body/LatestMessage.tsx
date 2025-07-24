import { useChat } from "@/contexts/ChatContext";
import { useMemo, useState, useEffect } from "react";
import styles from "./LatestMessage.module.css";

interface LatestMessageProps {
    role: "user" | "ai";
}

export const LatestMessage = ({ role }: LatestMessageProps) => {
    const { messages, isLoading } = useChat();
    const [faded, setFaded] = useState(false);
    const [prevMessage, setPrevMessage] = useState<string | undefined>(undefined);

    const latestMessage = useMemo(() => 
        messages.findLast(message => message.role === role)?.content, 
        [messages, role]
    );

    useEffect(() => {
        if (isLoading) setFaded(true);
    }, [isLoading]);

    useEffect(() => {
        if (latestMessage !== prevMessage) {
            setFaded(false);
            setPrevMessage(latestMessage);
        }
    }, [latestMessage, prevMessage]);

    const containerClassName = `${styles.container} ${styles[role]} ${faded ? styles.faded : ''}`;

    return (
        <div className={containerClassName}>
            {/* Text content */}
            <p className={styles.text}>
                {latestMessage || ""}
            </p>
        </div>
    );
};