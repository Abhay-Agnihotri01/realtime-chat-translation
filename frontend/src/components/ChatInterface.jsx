import React, { useState } from 'react';
import { useChat } from '../hooks/useChat';
import { Send, Globe, Wifi, WifiOff, Languages, MessageCircle, Sparkles, Activity } from 'lucide-react';
import MetricsModal from './MetricsModal';

const ChatInterface = () => {
    const [userId] = useState(() => {
        // Get existing userId from sessionStorage or create new one
        let storedUserId = sessionStorage.getItem('chatUserId');
        if (!storedUserId) {
            storedUserId = "user_" + Math.floor(Math.random() * 1000);
            sessionStorage.setItem('chatUserId', storedUserId);
        }
        return storedUserId;
    });
    const [selectedLang, setSelectedLang] = useState("eng_Latn");
    const { messages, sendMessage, isConnected, status } = useChat(userId, selectedLang);
    const [inputValue, setInputValue] = useState("");
    const [showMetrics, setShowMetrics] = useState(false);

    const languages = [
        { code: "eng_Latn", name: "English", flag: "🇺🇸" },
        { code: "spa_Latn", name: "Spanish", flag: "🇪🇸" },
        { code: "fra_Latn", name: "French", flag: "🇫🇷" },
        { code: "deu_Latn", name: "German", flag: "🇩🇪" },
        { code: "ita_Latn", name: "Italian", flag: "🇮🇹" },
        { code: "zho_Hans", name: "Chinese (Simplified)", flag: "🇨🇳" },
        { code: "hin_Deva", name: "Hindi", flag: "🇮🇳" },
        { code: "jpn_Jpan", name: "Japanese", flag: "🇯🇵" }
    ];

    const handleSend = (e) => {
        e.preventDefault();
        if (inputValue.trim()) {
            sendMessage(inputValue);
            setInputValue("");
        }
    };

    const selectedLanguage = languages.find(lang => lang.code === selectedLang);

    return (
        <div className="flex flex-col h-full bg-gradient-to-b from-white to-slate-50 relative">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-200/60 bg-white/90 backdrop-blur-sm">
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                            <MessageCircle className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                Translation Chat
                            </h1>
                            <p className="text-sm text-slate-500">Real-time multilingual messaging</p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    {/* Metrics Toggle */}
                    <button
                        onClick={() => setShowMetrics(true)}
                        className="flex items-center space-x-2 px-3 py-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
                        title="View System Metrics"
                    >
                        <Activity className="w-5 h-5" />
                        <span className="text-sm font-medium">Metrics</span>
                    </button>

                    {/* Language Selector */}
                    <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-slate-500 hidden sm:inline">Language</span>
                        <div className="relative">
                            <select
                                value={selectedLang}
                                onChange={(e) => setSelectedLang(e.target.value)}
                                className="appearance-none bg-white border border-slate-200 rounded-xl px-4 py-2 pr-10 text-sm font-medium text-slate-700 hover:border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 cursor-pointer"
                            >
                                {languages.map(lang => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.flag} {lang.name}
                                    </option>
                                ))}
                            </select>
                            <Languages className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                        </div>
                    </div>

                    {/* Connection Status */}
                    <div className={`flex items-center space-x-2 px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 ${isConnected
                        ? 'bg-green-100 text-green-700 border border-green-200'
                        : 'bg-red-100 text-red-700 border border-red-200'
                        }`}>
                        {isConnected ? (
                            <Wifi className="w-4 h-4" />
                        ) : (
                            <WifiOff className="w-4 h-4" />
                        )}
                        <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                        <div className="p-4 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full">
                            <Globe className="w-12 h-12 text-blue-500" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-slate-700 mb-2">Start a conversation</h3>
                            <p className="text-slate-500 max-w-md">
                                Send a message in {selectedLanguage?.name} and watch it get translated in real-time for other participants.
                            </p>
                        </div>
                    </div>
                ) : (
                    messages.map((msg) => (
                        msg.sender === 'System' ? (
                            <div key={msg.id} className="flex justify-center my-2 animate-fade-in">
                                <div className="bg-slate-100 text-slate-500 text-xs px-3 py-1 rounded-full border border-slate-200">
                                    {msg.content}
                                </div>
                            </div>
                        ) : (
                            <div key={msg.id} className={`flex animate-slide-up ${msg.sender === 'me' ? 'justify-end' : 'justify-start'
                                }`}>
                                <div className={`message-bubble ${msg.sender === 'me'
                                    ? 'message-sent bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                                    : 'message-received bg-white border border-slate-200 text-slate-800 shadow-sm'
                                    } rounded-2xl px-4 py-3 relative`}>
                                    <div className="font-medium">{msg.content}</div>
                                    {msg.original && msg.original !== msg.content && (
                                        <div className={`text-xs mt-2 pt-2 border-t opacity-75 italic ${msg.sender === 'me'
                                            ? 'border-white/20 text-blue-100'
                                            : 'border-slate-200 text-slate-500'
                                            }`}>
                                            <Sparkles className="w-3 h-3 inline mr-1" />
                                            Original: {msg.original}
                                        </div>
                                    )}
                                    <div className={`text-xs mt-1 ${msg.sender === 'me' ? 'text-blue-100' : 'text-slate-400'
                                        }`}>
                                        {msg.sender === 'me' ? 'You' : `User #${msg.sender.slice(-4)}`}
                                    </div>
                                </div>
                            </div>
                        )
                    ))
                )}
            </div>

            {/* Status Indicator */}
            {
                status && (
                    <div className="px-6 py-2 bg-blue-50 border-t border-blue-100">
                        <div className="flex items-center space-x-2 text-blue-600">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                            <span className="text-sm font-medium">{status}</span>
                        </div>
                    </div>
                )
            }

            {/* Input Area */}
            <div className="p-6 border-t border-slate-200/60 bg-white/90 backdrop-blur-sm">
                <form onSubmit={handleSend} className="flex items-center space-x-4">
                    <div className="flex-1 relative">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder={`Type a message in ${selectedLanguage?.name}...`}
                            className="w-full px-4 py-3 pr-12 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200 placeholder-slate-400"
                        />
                        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-2xl">
                            {selectedLanguage?.flag}
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || !isConnected}
                        className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>

            {/* Metrics Modal */}
            {showMetrics && <MetricsModal onClose={() => setShowMetrics(false)} />}
        </div >
    );
};

export default ChatInterface;
