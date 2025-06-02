import type { Metadata } from 'next'
import './globals.css'
import ClientBodyClass from './client-body-class'

export const metadata: Metadata = {
  title: 'EmoScan',
  description: 'EmoScan - 情感分析桌面应用',
  generator: 'EmoScan',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        <ClientBodyClass />
        {children}
      </body>
    </html>
  )
}
