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
    tagTypes: ["Cluster", "Team", "Invitation"],
    endpoints: (builder) => ({
        // AUTH
        register: builder.mutation({
            query: (credentials) => ({ url: "/users/register", method: "POST", body: credentials }),
        }),
        login: builder.mutation({
            query: (credentials) => {
                const formData = new URLSearchParams();
                formData.append("username", credentials.email);
                formData.append("password", credentials.password);
                return { url: "/auth/token", method: "POST", body: formData, headers: { "Content-Type": "application/x-www-form-urlencoded" } };
            },
        }),
        // CLUSTERS
        getClusters: builder.query({
            query: () => "/clusters",
            providesTags: ["Cluster"],
            async onCacheEntryAdded(arg, { updateCachedData, cacheDataLoaded, cacheEntryRemoved, getState }) {
                const token = getState().auth.token;
                if (!token) return;

                const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

                ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);

                    // Handle messages from the new unified WebSocket
                    if (message.type === "cluster_status_update") {
                        const data = message.payload;
                        updateCachedData((draft) => {
                            if (data.status === "DELETED") {
                                return draft.filter(c => c.id !== data.cluster_id);
                            }
                            const cluster = draft.find(c => c.id === data.cluster_id);
                            if (cluster) {
                                cluster.status = data.status;
                            }
                        });
                    }
                };

                await cacheEntryRemoved;
                ws.close();
            },
        }),
        createCluster: builder.mutation({
            query: (config) => ({ url: "/clusters", method: "POST", body: config }),
            invalidatesTags: ["Cluster"],
        }),
        deleteCluster: builder.mutation({
            query: (id) => ({ url: `/clusters/${id}`, method: "DELETE" }),
            invalidatesTags: ["Cluster"],
        }),
        // TEAMS
        getTeams: builder.query({
            query: () => '/teams',
            providesTags: (result) => result ? [...result.map(({ id }) => ({ type: 'Team', id })), { type: 'Team', id: 'LIST' }] : [{ type: 'Team', id: 'LIST' }],
        }),
        createTeam: builder.mutation({
            query: (team) => ({ url: '/teams', method: 'POST', body: team }),
            invalidatesTags: [{ type: 'Team', id: 'LIST' }],
        }),
        getTeamDetails: builder.query({
            query: (id) => `/teams/${id}`,
            providesTags: (result, error, id) => [{ type: 'Team', id }],
        }),
        inviteMember: builder.mutation({
            query: ({ teamId, inviteData }) => ({ url: `/teams/${teamId}/members`, method: 'POST', body: inviteData }),
            invalidatesTags: (result, error, { teamId }) => [{ type: 'Invitation', id: `TEAM-${teamId}` }],
        }),
        // INVITATIONS
        getPendingInvitationsForUser: builder.query({
            query: () => '/invitations/pending',
            providesTags: (result) => result ? [...result.map(({ id }) => ({ type: 'Invitation', id })), { type: 'Invitation', id: 'LIST' }] : [{ type: 'Invitation', id: 'LIST' }],
        }),
        getPendingInvitationsForTeam: builder.query({
            query: (teamId) => `/teams/${teamId}/invitations`,
            providesTags: (result, error, teamId) => [{ type: 'Invitation', id: `TEAM-${teamId}` }],
        }),
        acceptInvitation: builder.mutation({
            query: (token) => ({ url: `/invitations/${token}/accept`, method: 'POST' }),
            invalidatesTags: [{ type: 'Team', id: 'LIST' }, { type: 'Invitation', id: 'LIST' }],
        }),
        rejectInvitation: builder.mutation({
            query: (token) => ({ url: `/invitations/${token}/reject`, method: 'POST' }),
            invalidatesTags: [{ type: 'Invitation', id: 'LIST' }],
        }),
    }),
});

export const {
    useRegisterMutation, useLoginMutation, useGetClustersQuery,
    useCreateClusterMutation, useDeleteClusterMutation, useGetTeamsQuery,
    useCreateTeamMutation, useGetTeamDetailsQuery, useInviteMemberMutation,
    useGetPendingInvitationsForUserQuery, useGetPendingInvitationsForTeamQuery,
    useAcceptInvitationMutation, useRejectInvitationMutation,
} = apiSlice;