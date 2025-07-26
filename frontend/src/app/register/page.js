"use client";
import { useState } from "react";
import Link from "next/link";

export default function Register() {
	const [formData, setFormData] = useState({
		email: "",
		password: "",
		confirmPassword: "",
		agreeTerms: false,
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

		if (formData.password !== formData.confirmPassword) {
			alert("Passwords do not match!");
			return;
		}

		if (!formData.agreeTerms) {
			alert("Please agree to the terms and conditions");
			return;
		}

		console.log("Registration attempt:", formData);
		alert("Account created successfully! (Demo only)");
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
						Create your account
					</h2>
					<p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
						Or{" "}
						<Link
							href="/login"
							className="font-medium text-blue-600 hover:text-blue-500"
						>
							sign in to your existing account
						</Link>
					</p>
				</div>

				{/* Registration Form */}
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
									<path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
								</svg>
							</span>
							Create Account
						</button>
					</div>

					{/* Getting Started Info */}
					<div className="mt-6">
						<div className="relative">
							<div className="absolute inset-0 flex items-center">
								<div className="w-full border-t border-gray-300 dark:border-gray-600" />
							</div>
							<div className="relative flex justify-center text-sm">
								<span className="px-2 bg-blue-50 dark:bg-gray-800 text-gray-500">
									What You Get
								</span>
							</div>
						</div>

						<div className="mt-6 space-y-4">
							<div className="bg-white dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
								<h3 className="font-medium text-gray-900 dark:text-white mb-2">
									🎯 Prototype Features:
								</h3>
								<ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
									<li>• On-demand KinD clusters</li>
									<li>• Automatic TTL cleanup</li>
									<li>• Web dashboard + CLI access</li>
									<li>• Real-time provisioning updates</li>
									<li>• Encrypted kubeconfig storage</li>
								</ul>
							</div>

							<div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
								<h3 className="font-medium text-green-900 dark:text-green-100 mb-2">
									🚀 Getting Started:
								</h3>
								<ol className="text-sm text-green-800 dark:text-green-200 space-y-1">
									<li>1. Create your account</li>
									<li>2. Access the dashboard</li>
									<li>3. Click &quot;Create Cluster&quot;</li>
									<li>4. Wait ~3 minutes for provisioning</li>
									<li>5. Download kubeconfig and explore!</li>
								</ol>
							</div>

							<div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
								<h3 className="font-medium text-amber-900 dark:text-amber-100 mb-2">
									⚠️ Prototype Limitations:
								</h3>
								<ul className="text-sm text-amber-800 dark:text-amber-200 space-y-1">
									<li>
										• KinD clusters only (no cloud
										providers)
									</li>
									<li>• Fixed TTL (automatic deletion)</li>
									<li>• Demo authentication system</li>
									<li>• Single-node clusters</li>
								</ul>
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
