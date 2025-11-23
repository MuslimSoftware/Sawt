import { ChatProvider } from "@/contexts/ChatContext";
import { colors } from "@/theme/colors";

export const metadata = {
  title: 'Sawt (demo)',
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
        <link rel="icon" href="/assets/sawt_logo.png" type="image/png" />
        <script defer src="https://analytics.younesbenketira.com/script.js" data-website-id="98dccd7e-df4c-433f-9028-3a21a795776b"></script>
      </head>
      <body style={{ 
        fontFamily: 'Roboto, sans-serif', 
        background: colors.background.primary, 
        color: colors.text.primary, 
        margin: 0, 
        overflow: 'hidden', 
        width: "100vw", 
        height: "100vh" 
      }}>
        <ChatProvider>{children}</ChatProvider>
      </body>
    </html>
  )
}
