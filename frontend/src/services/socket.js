class SocketService {
    constructor() {
        this.socket = null;
        this.messageHandlers = [];
        this.isConnecting = false;
        this.url = null;
    }

    connect(url) {
        if (this.socket && this.url === url && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
            console.log('Already connected or connecting to', url);
            return;
        }

        if (this.socket) {
            this.socket.close();
        }

        this.isConnecting = true;
        this.url = url;
        console.log('Connecting to WebSocket:', url);
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log('WebSocket Connected');
            this.isConnecting = false;
        };

        this.socket.onmessage = (event) => {
            const message = event.data;
            this.messageHandlers.forEach(handler => handler(message));
        };

        this.socket.onclose = (event) => {
            console.log(`WebSocket Disconnected: Code ${event.code}, Reason: ${event.reason}`);
            this.isConnecting = false;
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket Error:', error);
            this.isConnecting = false;
        }
    }

    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(message);
        } else {
            console.error('WebSocket is not open');
        }
    }

    onMessage(handler) {
        this.messageHandlers.push(handler);
        return () => {
            this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
        };
    }

    disconnect() {
        this.isConnecting = false;
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN;
    }
}

export const socketService = new SocketService();
