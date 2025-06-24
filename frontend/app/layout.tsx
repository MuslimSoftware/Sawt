import { ChatProvider } from "@/contexts/ChatContext";

export const metadata = {
  title: 'Sawt',
  description: 'An AI powered real-time voice assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ background: '#1a1a1d', color: '#f5f5f5', margin: 0, overflow: 'hidden' }}>
        <ChatProvider>{children}</ChatProvider>
      </body>
    </html>
  )
}
