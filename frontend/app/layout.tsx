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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet" />
      </head>
      <body style={{ fontFamily: 'Roboto, sans-serif', background: '#1a1a1d', color: '#f5f5f5', margin: 0, overflow: 'hidden', width: "100vw", height: "100vh" }}>
        <ChatProvider>{children}</ChatProvider>
      </body>
    </html>
  )
}
