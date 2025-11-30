import { useState, useEffect, useCallback } from 'react';
import { socketService } from '../services/socket';

export const useChat = (userId, selectedLang = "eng_Latn") => {
    const [messages, setMessages] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [status, setStatus] = useState(null);

    useEffect(() => {
        // Use 127.0.0.1 to avoid IPv6 resolution issues with localhost
        const wsUrl = `ws://127.0.0.1:8000/ws/${userId}?lang=${selectedLang}`;

        // const wsUrl = `wss://${window.location.host}/ws/${userId}?lang=${selectedLang}`;


        // Only connect if not already connected to the same URL
        if (!socketService.isConnected() || socketService.url !== wsUrl) {
            socketService.connect(wsUrl);
        }

        // Monitor connection state
        const checkConnection = () => {
            setIsConnected(socketService.isConnected());
        };

        const interval = setInterval(checkConnection, 1000);
        checkConnection();

        // Listen for messages
        const messageHandler = (data) => {
            console.log('Received WebSocket message:', data);
            try {
                const parsed = JSON.parse(data);
                console.log('Parsed message:', parsed);

                if (parsed.type === 'status') {
                    setStatus(parsed.content);
                } else {
                    setStatus(null); // Clear status when a real message arrives
                    setMessages(prev => [...prev, {
                        sender: parsed.sender,
                        content: parsed.translated || parsed.content,
                        original: parsed.original,
                        id: parsed.id || (Date.now() + Math.random())
                    }]);
                }
            } catch (e) {
                console.error("Error parsing message", e);
                setMessages(prev => [...prev, {
                    sender: 'server',
                    content: data,
                    id: Date.now() + Math.random()
                }]);
            }
        };

        const unsubscribe = socketService.onMessage(messageHandler);

        return () => {
            unsubscribe();
            clearInterval(interval);
            // Don't disconnect on cleanup - keep connection alive
            // socketService.disconnect();
        };
    }, [userId, selectedLang]);

    const sendMessage = useCallback((content) => {
        if (!socketService.isConnected()) {
            console.error('Cannot send message: WebSocket not connected');
            return;
        }

        // Add the sent message to local messages immediately
        setMessages(prev => [...prev, {
            sender: 'me',
            content: content,
            original: content,
            id: Date.now() + Math.random()
        }]);

        const messagePayload = {
            content: content
        };

        try {
            socketService.sendMessage(JSON.stringify(messagePayload));
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }, []);

    return { messages, sendMessage, isConnected, status };
};
