// frontend/src/components/Terminal.js
"use client";
import { useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { Terminal as XTerm } from 'xterm';
import 'xterm/css/xterm.css';

export default function Terminal({ clusterId, onClose }) {
    const termRef = useRef(null);
    const xtermRef = useRef(null);
    const socketRef = useRef(null);
    const { token } = useSelector((state) => state.auth);

    useEffect(() => {
        if (!clusterId || !termRef.current) return;

        if (!xtermRef.current) {
            xtermRef.current = new XTerm({
                cursorBlink: true,
                theme: { background: '#1e1e1e', foreground: '#d4d4d4', cursor: '#d4d4d4' },
                rows: 30,
                cols: 120,
                fontFamily: 'monospace',
                fontSize: 14,
                convertEol: true,
            });
        }
        const xterm = xtermRef.current;

        const openTimeout = setTimeout(() => {
            if (termRef.current && !xterm.element) {
                xterm.open(termRef.current);
            }
        }, 100);

        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const host = process.env.NODE_ENV === 'development' ? 'localhost:8000' : window.location.host;
        const wsUrl = `${protocol}://${host}/api/v1/ws?token=${token}`;

        const socket = new WebSocket(wsUrl);
        socketRef.current = socket;

        socket.onopen = () => {
            socket.send(JSON.stringify({
                type: "start_terminal",
                cluster_id: clusterId,
            }));
            xterm.focus();
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case "terminal_data":
                    xterm.write(data.payload);
                    break;
                case "terminal_error":
                    xterm.writeln(`\r\n\x1b[31m❌ Error: ${data.payload}\x1b[0m`);
                    break;
            }
        };

        socket.onerror = (error) => {
            console.error("WebSocket Error:", error);
            xterm.writeln("\r\n\x1b[31m❌ A connection error occurred.\x1b[0m");
        };

        socket.onclose = () => {
            xterm.writeln("\r\n\x1b[90mConnection closed.\x1b[0m");
        };

        const onDataDisposable = xterm.onData((data) => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                    type: "terminal_data",
                    payload: data,
                }));
            }
        });

        return () => {
            clearTimeout(openTimeout);
            onDataDisposable.dispose();
            if (socket) {
                socket.close();
            }
        };
    }, [clusterId, token]);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-[#1e1e1e] rounded-lg shadow-2xl w-full h-full max-w-6xl max-h-[80vh] p-4 flex flex-col">
                <div className="flex justify-between items-center mb-2 flex-shrink-0">
                    <h3 className="text-white font-semibold">Cluster Terminal</h3>
                    <button onClick={onClose} className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                        Close
                    </button>
                </div>
                <div ref={termRef} className="flex-grow w-full h-full" />
            </div>
        </div>
    );
}