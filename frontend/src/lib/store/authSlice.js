// frontend/src/lib/store/authSlice.js
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    user: null,
    token: null,
};

const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setCredentials: (state, action) => {
            // Use the correct key from the backend response
            const { user, access_token } = action.payload;
            state.user = user;
            state.token = access_token; // <-- CORRECTED
        },
        logOut: (state) => {
            state.user = null;
            state.token = null;
        },
    },
});

export const { setCredentials, logOut } = authSlice.actions;

export default authSlice.reducer;