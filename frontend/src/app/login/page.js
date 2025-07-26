"use client";
import { useState } from "react";
import Link from "next/link";

export default function Login() {
	const [formData, setFormData] = useState({
		email: "",
		password: "",
		rememberMe: false,
	});

	const handleInputChange = (e) => {
		const { name, value, type, checked } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
		}));
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		console.log("Login attempt:", formData);
		alert("Login successful! (Demo only)");
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-md w-full space-y-8">
				{/* Header */}
				<div className="text-center">
					<Link
						href="/"
						className="inline-flex items-center space-x-3 mb-8"
					>
						<div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
							<span className="text-white font-bold text-xl">
								K8
							</span>
						</div>
						<div className="text-left">
							<div className="text-2xl font-bold text-gray-900 dark:text-white">
								PyK8s-Lab
							</div>
							<div className="text-xs text-gray-500 dark:text-gray-400">
								Prototype v0.1
							</div>
						</div>
					</Link>

					<h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">
						Sign in to your account
					</h2>
					<p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
						Or{" "}
						<Link
							href="/register"
							className="font-medium text-blue-600 hover:text-blue-500"
						>
							create a new account
						</Link>
					</p>
				</div>

				{/* Login Form */}
				<form className="mt-8 space-y-6" onSubmit={handleSubmit}>
					<div className="space-y-4">
						<div>
							<label
								htmlFor="email"
								className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>
								Email Address
							</label>
							<input
								id="email"
								name="email"
								type="email"
								autoComplete="email"
								required
								value={formData.email}
								onChange={handleInputChange}
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
								id="password"
								name="password"
								type="password"
								autoComplete="current-password"
								required
								value={formData.password}
								onChange={handleInputChange}
								className="appearance-none relative block w-full px-4 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
								placeholder="Enter your password"
							/>
						</div>
					</div>

					<div className="flex items-center justify-between">
						<div className="flex items-center">
							<input
								id="rememberMe"
								name="rememberMe"
								type="checkbox"
								checked={formData.rememberMe}
								onChange={handleInputChange}
								className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
							/>
							<label
								htmlFor="rememberMe"
								className="ml-2 block text-sm text-gray-900 dark:text-gray-300"
							>
								Remember me
							</label>
						</div>

						<div className="text-sm">
							<a
								href="#"
								className="font-medium text-blue-600 hover:text-blue-500"
							>
								Forgot your password?
							</a>
						</div>
					</div>

					<div>
						<button
							type="submit"
							className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl"
						>
							<span className="absolute left-0 inset-y-0 flex items-center pl-3">
								<svg
									className="h-5 w-5 text-blue-300 group-hover:text-blue-200"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 20 20"
									fill="currentColor"
									aria-hidden="true"
								>
									<path
										fillRule="evenodd"
										d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
										clipRule="evenodd"
									/>
								</svg>
							</span>
							Sign in
						</button>
					</div>

					{/* Demo Info */}
					<div className="mt-6">
						<div className="relative">
							<div className="absolute inset-0 flex items-center">
								<div className="w-full border-t border-gray-300 dark:border-gray-600" />
							</div>
							<div className="relative flex justify-center text-sm">
								<span className="px-2 bg-blue-50 dark:bg-gray-800 text-gray-500">
									Demo Features
								</span>
							</div>
						</div>

						<div className="mt-6 space-y-4">
							<div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
								<h3 className="font-medium text-gray-900 dark:text-white mb-2">
									🚀 Quick Access:
								</h3>
								<ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
									<li>• Create clusters in &lt; 3 minutes</li>
									<li>• Web UI + CLI interface</li>
									<li>• Real-time status updates</li>
									<li>• Automatic cleanup with TTL</li>
								</ul>
							</div>

							<div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
								<h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
									💡 What&apos;s Next:
								</h3>
								<p className="text-sm text-blue-800 dark:text-blue-200">
									After login, you&apos;ll access the
									dashboard to create and manage your
									ephemeral Kubernetes clusters powered by
									KinD.
								</p>
							</div>
						</div>
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
