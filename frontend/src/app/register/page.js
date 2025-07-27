// frontend/src/app/register/page.js
"use client";
import { useRegisterMutation } from "@/lib/store/apiSlice";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Register() {
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        confirmPassword: "",
    });
    const [error, setError] = useState("");

    const router = useRouter();
    
    // Get the mutation trigger, isLoading state, and error info from the hook
    const [register, { isLoading, isSuccess, isError, error: registerError }] = useRegisterMutation();

    useEffect(() => {
        // If registration is successful, redirect to the login page
        if (isSuccess) {
            router.push("/login?registered=true");
        }
        // If there's an error from the API, display it
        if (isError) {
            setError(registerError?.data?.detail || "An unexpected error occurred.");
        }
    }, [isSuccess, isError, registerError, router]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(""); // Clear previous errors

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match!");
            return;
        }

        try {
            // Call the mutation with the email and password
            await register({ email: formData.email, password: formData.password }).unwrap();
        } catch (err) {
            // Error is handled by the useEffect hook, but you can log it here if needed
            console.error("Failed to register:", err);
        }
    };

    // --- (JSX remains largely the same, but we'll paste the full component for clarity) ---
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                {/* Header */}
                <div className="text-center">
                    {/* ... (Header JSX is unchanged) ... */}
                </div>

                {/* Registration Form */}
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && <div className="p-3 bg-red-100 text-red-700 border border-red-300 rounded-lg">{error}</div>}
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
                        {/* ... (Password and Confirm Password inputs are unchanged) ... */}
                    </div>
                    {/* ... (Terms agreement checkbox is unchanged) ... */}
                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
                        >
                            {isLoading ? "Creating Account..." : "Create Account"}
                        </button>
                    </div>
                </form>

                <div className="text-center">
                    <Link href="/" className="text-blue-600 hover:text-blue-500 font-medium">
                        ← Back to home
                    </Link>
                </div>
            </div>
        </div>
    );
}