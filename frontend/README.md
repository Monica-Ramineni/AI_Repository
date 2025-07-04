# AI Chat Frontend

A modern, responsive chat interface built with Next.js that connects to your FastAPI backend for real-time AI conversations.

## Features

- 🚀 **Real-time Streaming**: Experience AI responses as they're generated
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- 🔐 **Secure API Key Input**: Password-style input for your OpenAI API key
- ⚙️ **Customizable Settings**: Configure AI behavior and model selection
- 📱 **Mobile Responsive**: Works perfectly on all device sizes
- 🎯 **Calligrapher Typography**: Elegant font styling for headers
- 🔄 **Auto-scroll**: Messages automatically scroll to the latest
- ⌨️ **Keyboard Shortcuts**: Press Enter to send messages

## Prerequisites

- Node.js 18+ installed
- Your FastAPI backend running on `http://localhost:8000`
- OpenAI API key

## Quick Start

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server**
   ```bash
   npm run dev
   ```

3. **Open Your Browser**
   Navigate to `http://localhost:3000`

4. **Configure Settings**
   - Click the settings icon in the sidebar
   - Enter your OpenAI API key
   - Customize the developer message (system prompt)
   - Select your preferred AI model

5. **Start Chatting**
   - Type your message in the input field
   - Press Enter or click the send button
   - Watch as AI responses stream in real-time

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles and Tailwind config
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main chat interface
├── lib/
│   └── utils.ts             # Utility functions
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── next.config.js           # Next.js configuration
```

## Configuration

### Backend Connection
The frontend is configured to connect to your FastAPI backend at `http://localhost:8000`. If your backend runs on a different port, update the `next.config.js` file:

```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:YOUR_PORT/api/:path*',
    },
  ];
}
```

### Available Models
- GPT-4.1 Mini (default)
- GPT-4
- GPT-3.5 Turbo

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Key Technologies

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **clsx & tailwind-merge** - Conditional class names

## Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically

### Other Platforms
1. Build the project: `npm run build`
2. Start the production server: `npm run start`
3. Deploy the `.next` folder to your hosting platform

## API Integration

The frontend communicates with your FastAPI backend through the following endpoints:

- `POST /api/chat` - Send chat messages and receive streaming responses
- `GET /api/health` - Health check endpoint

### Request Format
```json
{
  "developer_message": "System instructions for the AI",
  "user_message": "User's message",
  "model": "gpt-4.1-mini",
  "api_key": "your-openai-api-key"
}
```

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure your FastAPI backend is running on port 8000
   - Check that CORS is properly configured

2. **API Key Issues**
   - Verify your OpenAI API key is valid
   - Ensure you have sufficient credits

3. **Streaming Not Working**
   - Check browser console for errors
   - Verify the backend is returning proper streaming responses

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of The AI Engineer Challenge.