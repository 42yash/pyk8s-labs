// frontend/src/app/dashboard/page.js
"use client";
import DashboardLayout from "@/components/DashboardLayout";
import { useCreateClusterMutation, useDeleteClusterMutation, useGetClustersQuery } from "@/lib/store/apiSlice";
import { useState } from "react";

export default function Dashboard() {
    // --- THIS IS THE ONLY CHANGE IN THIS FILE ---
    // The pollingInterval is removed, WebSocket will handle updates.
    const { data: clusters, error, isLoading, isFetching } = useGetClustersQuery();
    // --- END OF CHANGE ---

    const [createCluster, { isLoading: isCreating }] = useCreateClusterMutation();
    const [deleteCluster, { isLoading: isDeleting }] = useDeleteClusterMutation();
    const [clusterName, setClusterName] = useState("");
    const [apiError, setApiError] = useState("");

    const [successMessage, setSuccessMessage] = useState("");

    const handleCreateCluster = async (e) => {
        e.preventDefault();
        if (!clusterName || isCreating) return;
        setApiError("");
        setSuccessMessage("");

        try {
            // Await the mutation without unwrap() to avoid throwing on 202
            const response = await createCluster({ name: clusterName, ttl_hours: 1 });

            // Check if there's an error in the response
            if (response.error) {
                throw response.error;  // Will go to catch block
            }

            // If no error, it's successful (includes 202 status)
            setClusterName("");
            setSuccessMessage(`Cluster "${clusterName}" is being provisioned. You'll see status updates below.`);
            setTimeout(() => setSuccessMessage(""), 5000);
        } catch (err) {
            console.error("Cluster creation error:", err);  // Log for debugging
            setApiError(err.data?.detail || "Failed to create cluster. Please try again.");
        }
    };



    const handleDeleteCluster = async (clusterId) => {
        if (isDeleting) return;
        try {
            await deleteCluster(clusterId).unwrap();
        } catch (err) {
            alert(err.data?.detail || "Failed to delete cluster.");
        }
    };

    const renderStatusBadge = (status) => {
        const styles = {
            RUNNING: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
            PROVISIONING: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300 animate-pulse",
            DELETING: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300 animate-pulse",
            ERROR: "bg-red-200 text-red-900 dark:bg-red-900 dark:text-red-200",
        };
        return <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${styles[status] || 'bg-gray-100 text-gray-800'}`}>{status}</span>;
    };

    return (
        <DashboardLayout>
            <div className="space-y-8">
                {/* Create Cluster Form */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                    <h2 className="text-xl font-bold mb-4">Create a New Cluster</h2>
                    <form onSubmit={handleCreateCluster} className="flex items-center space-x-4">
                        <input
                            type="text"
                            value={clusterName}
                            onChange={(e) => setClusterName(e.target.value)}
                            placeholder="my-test-cluster (lowercase, letters/numbers)"
                            required
                            className="flex-grow px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700"
                        />
                        <button
                            type="submit"
                            disabled={isCreating || !clusterName}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50"
                        >
                            {isCreating ? "Provisioning..." : "Create Cluster"}
                        </button>
                    </form>
                    {successMessage && <p className="text-green-500 mt-2">{successMessage}</p>}
                    {apiError && <p className="text-red-500 mt-2">{apiError}</p>}

                </div>

                {/* Cluster List */}
                <div>
                    <h2 className="text-xl font-bold mb-4">Your Clusters</h2>
                    {(isLoading || isFetching) && <p>Loading clusters...</p>}
                    {error && <p className="text-red-500">Error fetching clusters: {error.toString()}</p>}

                    {!isLoading && !error && (
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
                            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                                {clusters?.length === 0 && <li className="p-4 text-center text-gray-500">No clusters found. Create one to get started!</li>}
                                {clusters?.map((cluster) => (
                                    <li key={cluster.id} className="p-4 flex justify-between items-center">
                                        <div>
                                            <p className="font-bold text-lg">{cluster.name}</p>
                                            <p className="text-sm text-gray-500">Expires: {new Date(cluster.ttl_expires_at).toLocaleString()}</p>
                                        </div>
                                        <div className="flex items-center space-x-4">
                                            {renderStatusBadge(cluster.status)}
                                            <button
                                                onClick={() => handleDeleteCluster(cluster.id)}
                                                disabled={isDeleting || cluster.status === 'DELETING'}
                                                className="px-4 py-1 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 disabled:opacity-50"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}