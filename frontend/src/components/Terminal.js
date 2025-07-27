// frontend/src/components/Terminal.js
"use client";

import { useEffect, useRef, useState } from 'react';
import { useSelector } from 'react-redux';
import { Terminal as XTerm } from 'xterm';
import 'xterm/css/xterm.css';

export default function Terminal({ clusterId, onClose }) {
    // A ref to hold the DOM element where the terminal will be attached
    const termRef = useRef(null);
    // A ref to hold the XTerm instance itself to avoid re-renders
    const xterm = useRef(null);

    const { token } = useSelector((state) => state.auth);
    const [status, setStatus] = useState('CONNECTING'); // CONNECTING, OPEN, CLOSED

    // This effect runs once to initialize the terminal
    useEffect(() => {
        if (termRef.current && !xterm.current) {
            xterm.current = new XTerm({
                cursorBlink: true,
                theme: {
                    background: '#000000',
                    foreground: '#FFFFFF',
                    cursor: '#FFFFFF',
                },
            });
            xterm.current.open(termRef.current);
        }

        // Cleanup on unmount
        return () => {
            if (xterm.current) {
                xterm.current.dispose();
                xterm.current = null;
            }
        };
    }, []);

    // This effect handles the WebSocket connection
    useEffect(() => {
        if (!token || !clusterId || !xterm.current) {
            return;
        }

        const term = xterm.current;
        term.reset();
        term.writeln('Connecting to terminal...');

        const wsUrl = `ws://localhost:8000/api/v1/ws/terminal/${clusterId}?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Terminal WebSocket connected');
            setStatus('OPEN');
            term.writeln('\x1b[32mConnected!\x1b[0m\r\n');
            term.focus();
        };

        ws.onmessage = (event) => {
            if (event.data instanceof Blob) {
                event.data.arrayBuffer().then(buffer => {
                    term.write(new Uint8Array(buffer));
                });
            } else {
                term.write(event.data);
            }
        };

        ws.onerror = (error) => {
            console.error('Terminal WebSocket error:', error);
            setStatus('CLOSED');
            term.writeln('\r\n\x1b[31mConnection error.\x1b[0m');
        };

        ws.onclose = (event) => {
            console.log('Terminal WebSocket disconnected:', event.reason);
            setStatus('CLOSED');
            term.writeln(`\r\n\x1b[31mDisconnected: ${event.reason || 'Connection closed'}\x1b[0m`);
        };

        const onDataDisposable = term.onData((data) => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(data);
            }
        });

        return () => {
            onDataDisposable.dispose();
            if (ws.readyState !== WebSocket.CLOSED) {
                ws.close();
            }
        };

    }, [clusterId, token]);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-black rounded-lg shadow-2xl w-full h-full max-w-6xl max-h-[80vh] p-4 flex flex-col">
                <div className="flex justify-between items-center mb-2 flex-shrink-0">
                    <h3 className="text-white font-semibold">
                        Cluster Terminal
                        <span className={`ml-4 text-sm px-2 py-1 rounded ${status === 'OPEN' ? 'bg-green-600' : 'bg-red-600'}`}>
                            {status}
                        </span>
                    </h3>
                    <button onClick={onClose} className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                        Close
                    </button>
                </div>
                {/* This is the DOM element our terminal will attach to */}
                <div ref={termRef} className="flex-grow w-full h-full" />
            </div>
        </div>
    );
}