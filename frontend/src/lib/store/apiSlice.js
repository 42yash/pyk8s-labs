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
    tagTypes: ["Cluster", "Team"], // Add "Team" tag type
    endpoints: (builder) => ({
        // --- AUTH ENDPOINTS ---
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
        // --- CLUSTER ENDPOINTS ---
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

                    ws.onclose = (event) => {
                        console.log('WebSocket closed:', {
                            code: event.code,
                            reason: event.reason,
                            wasClean: event.wasClean,
                            timestamp: new Date().toISOString()
                        });

                        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
                            reconnectAttempts++;
                            console.log(`Attempting to reconnect WebSocket (${reconnectAttempts}/${maxReconnectAttempts})`);
                            setTimeout(connectWebSocket, 2000 * reconnectAttempts);
                        }
                    };
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
            invalidatesTags: ["Cluster"],
        }),
        deleteCluster: builder.mutation({
            query: (clusterId) => ({
                url: `/clusters/${clusterId}`,
                method: "DELETE",
            }),
            invalidatesTags: ["Cluster"],
        }),

        // --- TEAM ENDPOINTS ---
        getTeams: builder.query({
            query: () => '/teams',
            providesTags: (result) =>
                result
                    ? [...result.map(({ id }) => ({ type: 'Team', id })), { type: 'Team', id: 'LIST' }]
                    : [{ type: 'Team', id: 'LIST' }],
        }),
        createTeam: builder.mutation({
            query: (newTeam) => ({
                url: '/teams',
                method: 'POST',
                body: newTeam,
            }),
            invalidatesTags: [{ type: 'Team', id: 'LIST' }],
        }),
        getTeamDetails: builder.query({
            query: (teamId) => `/teams/${teamId}`,
            providesTags: (result, error, id) => [{ type: 'Team', id }],
        }),
        inviteMember: builder.mutation({
            query: ({ teamId, inviteData }) => ({
                url: `/teams/${teamId}/members`,
                method: 'POST',
                body: inviteData,
            }),
            invalidatesTags: (result, error, { teamId }) => [{ type: 'Team', id: teamId }],
        }),
    }),
});

export const {
    useRegisterMutation,
    useLoginMutation,
    useGetClustersQuery,
    useCreateClusterMutation,
    useDeleteClusterMutation,
    // Export new hooks
    useGetTeamsQuery,
    useCreateTeamMutation,
    useGetTeamDetailsQuery,
    useInviteMemberMutation,
} = apiSlice;