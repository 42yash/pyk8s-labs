// frontend/src/lib/store/apiSlice.js
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const apiSlice = createApi({
    reducerPath: "api",
    baseQuery: fetchBaseQuery({
        baseUrl: "http://localhost:8000/api/v1", // URL of our FastAPI backend
        prepareHeaders: (headers, { getState }) => {
            // We will add logic here later to get the token from the state
            const token = getState().auth?.token;
            if (token) {
                headers.set("authorization", `Bearer ${token}`);
            }
            return headers;
        },
    }),
    tagTypes: ["Cluster"], // Used for automatic re-fetching
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
                // RTK Query needs the form data in the body for this type of request
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
            providesTags: ["Cluster"], // Provides the 'Cluster' tag for caching
        }),
        createCluster: builder.mutation({
            query: (clusterConfig) => ({
                url: "/clusters",
                method: "POST",
                body: clusterConfig,
            }),
            invalidatesTags: ["Cluster"], // Invalidates 'Cluster' tag, forcing a re-fetch
        }),
        deleteCluster: builder.mutation({
            query: (clusterId) => ({
                url: `/clusters/${clusterId}`,
                method: "DELETE",
            }),
            invalidatesTags: ["Cluster"], // Invalidates 'Cluster' tag, forcing a re-fetch
        }),
    }),
});

// Export auto-generated hooks for use in components
export const {
    useRegisterMutation,
    useLoginMutation,
    useGetClustersQuery,
    useCreateClusterMutation,
    useDeleteClusterMutation,
} = apiSlice;