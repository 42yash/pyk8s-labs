// frontend/src/lib/store/apiSlice.js
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const apiSlice = createApi({
    reducerPath: "api",
    baseQuery: fetchBaseQuery({
        baseUrl: "http://localhost:8000/api/v1",
        prepareHeaders: (headers, { getState }) => {
            const token = getState().auth?.token;
            if (token) {
                headers.set("authorization", `Bearer ${token}`);
            }
            return headers;
        },
    }),
    tagTypes: ["Cluster"],
    endpoints: (builder) => ({
        register: builder.mutation({
            query: (credentials) => ({
                url: "/users/register",
                method: "POST",
                body: credentials,
            }),
        }),
        login: builder.mutation({
            query: (credentials) => {
                const formData = new URLSearchParams();
                formData.append("username", credentials.email);
                formData.append("password", credentials.password);
                return {
                    url: "/auth/token",
                    method: "POST",
                    body: formData,
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                };
            },
        }),
        getClusters: builder.query({
            query: () => "/clusters",
            providesTags: ["Cluster"],
            async onCacheEntryAdded(
                arg,
                { updateCachedData, cacheDataLoaded, cacheEntryRemoved, getState }
            ) {
                const token = getState().auth.token;
                if (!token) return;

                let ws;
                let reconnectAttempts = 0;
                const maxReconnectAttempts = 5;

                const connectWebSocket = () => {
                    ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

                    ws.onopen = () => {
                        console.log("WebSocket connected");
                        reconnectAttempts = 0;
                    };

                    ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        console.log("WebSocket message received:", data);

                        updateCachedData((draft) => {
                            if (data.status === "DELETED") {
                                return draft.filter(c => c.id !== data.cluster_id);
                            }
                            const cluster = draft.find(c => c.id === data.cluster_id);
                            if (cluster) {
                                cluster.status = data.status;
                            }
                        });
                    };

                    ws.onerror = (error) => {
                        console.error('WebSocket error occurred:', {
                            readyState: ws.readyState,
                            url: ws.url,
                            timestamp: new Date().toISOString()
                        });
                    };

                    // --- CORRECTED SECTION ---
                    // The two onclose handlers have been merged into one.
                    ws.onclose = (event) => {
                        console.log('WebSocket closed:', {
                            code: event.code,
                            reason: event.reason,
                            wasClean: event.wasClean,
                            timestamp: new Date().toISOString()
                        });

                        // Attempt to reconnect if not a normal closure (code 1000)
                        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
                            reconnectAttempts++;
                            console.log(`Attempting to reconnect WebSocket (${reconnectAttempts}/${maxReconnectAttempts})`);
                            // Exponential backoff for reconnection attempts
                            setTimeout(connectWebSocket, 2000 * reconnectAttempts);
                        }
                    };
                    // --- END CORRECTED SECTION ---
                };

                try {
                    await cacheDataLoaded;
                    connectWebSocket();
                } catch (error) {
                    console.error("Cache loading failed:", error);
                }

                await cacheEntryRemoved;
                if (ws) {
                    ws.close(1000, "Component unmounted");
                }
            }
            ,
        }),
        createCluster: builder.mutation({
            query: (clusterConfig) => ({
                url: "/clusters",
                method: "POST",
                body: clusterConfig,
            }),
            // By invalidating the general 'Cluster' tag, we tell RTK Query to refetch the list.
            // This is simpler and more reliable than optimistic updates for this case.
            invalidatesTags: ["Cluster"],
        }),
        deleteCluster: builder.mutation({
            query: (clusterId) => ({
                url: `/clusters/${clusterId}`,
                method: "DELETE",
            }),
            // We keep this invalidation as a fallback, but the WebSocket should handle the primary update.
            invalidatesTags: ["Cluster"],
        }),
    }),
});

export const {
    useRegisterMutation,
    useLoginMutation,
    useGetClustersQuery,
    useCreateClusterMutation,
    useDeleteClusterMutation,
} = apiSlice;