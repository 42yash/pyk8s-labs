// frontend/src/components/Terminal.js
"use client";
import { useExecuteClusterCommandMutation } from '@/lib/store/apiSlice';
import { useState } from 'react';

export default function Terminal({ clusterId, onClose }) {
    const [command, setCommand] = useState('');
    const [history, setHistory] = useState([]); // To store { command, output, error }

    const [executeCommand, { isLoading }] = useExecuteClusterCommandMutation();

    const handleCommandSubmit = async (e) => {
        e.preventDefault();
        if (!command || isLoading) return;

        const currentCommand = command;
        setCommand(''); // Clear input field immediately

        try {
            const result = await executeCommand({ clusterId, command: currentCommand }).unwrap();
            setHistory(prev => [...prev, { command: currentCommand, output: result.output, error: result.error }]);
        } catch (err) {
            const errorMsg = err.data?.detail || "An unexpected error occurred.";
            setHistory(prev => [...prev, { command: currentCommand, output: null, error: errorMsg }]);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-[#1e1e1e] rounded-lg shadow-2xl w-full h-full max-w-6xl max-h-[80vh] p-4 flex flex-col font-mono">
                {/* Header */}
                <div className="flex justify-between items-center mb-4 flex-shrink-0">
                    <h3 className="text-white font-semibold">Command Runner</h3>
                    <button onClick={onClose} className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                        Close
                    </button>
                </div>

                {/* Output Display */}
                <div className="flex-grow w-full h-full bg-black text-white p-4 rounded-md overflow-y-auto text-sm">
                    {history.length === 0 && <p className="text-gray-400">Enter a command below to begin.</p>}
                    {history.map((item, index) => (
                        <div key={index} className="mb-4">
                            <p className="text-green-400">
                                <span className="text-blue-400">$</span> {item.command}
                            </p>
                            {item.output && <pre className="whitespace-pre-wrap">{item.output}</pre>}
                            {item.error && <pre className="text-red-400 whitespace-pre-wrap">{item.error}</pre>}
                        </div>
                    ))}
                    {isLoading && <p className="text-yellow-400 animate-pulse">Executing...</p>}
                </div>

                {/* Input Form */}
                <div className="mt-4 flex-shrink-0">
                    <form onSubmit={handleCommandSubmit} className="flex items-center space-x-2">
                        <span className="text-blue-400 text-lg">$</span>
                        <input
                            type="text"
                            value={command}
                            onChange={(e) => setCommand(e.target.value)}
                            placeholder="e.g., kubectl get pods"
                            autoFocus
                            disabled={isLoading}
                            className="flex-grow bg-gray-900 text-white px-3 py-2 rounded-md border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !command}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                        >
                            Run
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
