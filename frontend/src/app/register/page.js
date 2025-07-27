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
        agreeTerms: false, // Add this to state
    });
    const [error, setError] = useState("");

    const router = useRouter();

    const [register, { isLoading, isSuccess, isError, error: registerError }] = useRegisterMutation();

    useEffect(() => {
        if (isSuccess) {
            router.push("/login?registered=true");
        }
        if (isError) {
            setError(registerError?.data?.detail || "An unexpected error occurred.");
        }
    }, [isSuccess, isError, registerError, router]);

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match!");
            return;
        }
        if (!formData.agreeTerms) {
            setError("You must agree to the terms to register.");
            return;
        }

        try {
            await register({ email: formData.email, password: formData.password }).unwrap();
        } catch (err) {
            console.error("Failed to register:", err);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <Link href="/" className="inline-flex items-center space-x-3 mb-8">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                            <span className="text-white font-bold text-xl">K8</span>
                        </div>
                        <div className="text-left">
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">PyK8s-Lab</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">Prototype v0.1</div>
                        </div>
                    </Link>
                    <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">Create your account</h2>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        Or{" "}
                        <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                            sign in to your existing account
                        </Link>
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && <div className="p-3 bg-red-100 text-red-700 border border-red-300 rounded-lg">{error}</div>}
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email Address</label>
                            <input
                                id="email" name="email" type="email" autoComplete="email"
                                required value={formData.email} onChange={handleInputChange}
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Enter your email address"
                            />
                        </div>

                        {/* --- START: ADDED THIS SECTION --- */}
                        <div>
                            <label
                                htmlFor="password"
                                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                            >
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete="new-password"
                                required
                                value={formData.password}
                                onChange={handleInputChange}
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Create a strong password"
                            />
                        </div>
                        <div>
                            <label
                                htmlFor="confirmPassword"
                                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                            >
                                Confirm Password
                            </label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                autoComplete="new-password"
                                required
                                value={formData.confirmPassword}
                                onChange={handleInputChange}
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                placeholder="Confirm your password"
                            />
                        </div>
                    </div>
                    <div className="flex items-start">
                        <input
                            id="agreeTerms"
                            name="agreeTerms"
                            type="checkbox"
                            required
                            checked={formData.agreeTerms}
                            onChange={handleInputChange}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
                        />
                        <label
                            htmlFor="agreeTerms"
                            className="ml-2 block text-sm text-gray-900 dark:text-gray-300"
                        >
                            I agree to use PyK8s-Lab for testing and learning
                            purposes only. I understand that clusters will be
                            automatically deleted according to TTL policy and
                            this is a prototype service.
                        </label>
                    </div>
                    {/* --- END: ADDED THIS SECTION --- */}

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