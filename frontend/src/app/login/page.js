// frontend/src/app/login/page.js
"use client";
import { useLoginMutation } from "@/lib/store/apiSlice";
import { setCredentials } from "@/lib/store/authSlice";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";

export default function Login() {
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [error, setError] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    const router = useRouter();
    const searchParams = useSearchParams();
    const dispatch = useDispatch();

    const [login, { isLoading }] = useLoginMutation();
    
    useEffect(() => {
        // Check for a query param to show a message after successful registration
        if (searchParams.get("registered")) {
            setSuccessMessage("Registration successful! Please sign in.");
        }
    }, [searchParams]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccessMessage("");

        try {
            const userData = await login(formData).unwrap();
            // Dispatch the action to save token and user info
            dispatch(setCredentials({ ...userData, user: { email: formData.email } }));
            // Redirect to the dashboard
            router.push("/dashboard");
        } catch (err) {
            setError(err.data?.detail || "Failed to log in. Please check your credentials.");
            console.error("Failed to login:", err);
        }
    };

    // --- (JSX remains largely the same) ---
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                {/* ... (Header JSX is unchanged) ... */}
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && <div className="p-3 bg-red-100 text-red-700 border border-red-300 rounded-lg">{error}</div>}
                    {successMessage && <div className="p-3 bg-green-100 text-green-700 border border-green-300 rounded-lg">{successMessage}</div>}
                    
                    <div className="space-y-4">
                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                            >
                                Email Address
                            </label>
                            <input
                                id="email" name="email" type="email" autoComplete="email"
                                required value={formData.email} onChange={handleInputChange}
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Enter your email address"
                            />
                        </div>
                        <div>
                            <label
                                htmlFor="password"
                                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                            >
                                Password
                            </label>
                            <input
                                id="password" name="password" type="password" autoComplete="current-password"
                                required value={formData.password} onChange={handleInputChange}
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Enter your password"
                            />
                        </div>
                    </div>

                    {/* ... (Remember me / Forgot password JSX is unchanged) ... */}

                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
                        >
                           {isLoading ? "Signing In..." : "Sign in"}
                        </button>
                    </div>
                </form>
                <div className="text-center">
                    <Link
                        href="/"
                        className="text-blue-600 hover:text-blue-500 font-medium"
                    >
                        ← Back to home
                    </Link>
                </div>
            </div>
        </div>
    );
}