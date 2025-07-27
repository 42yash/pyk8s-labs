"use client";
import Link from "next/link";
import { useState } from "react";

export default function Home() {
	const [showLoginModal, setShowLoginModal] = useState(false);
	const [showRegisterModal, setShowRegisterModal] = useState(false);

	const handleLogin = (e) => {
		e.preventDefault();
		alert("Login successful! (Demo only)");
		setShowLoginModal(false);
	};

	const handleRegister = (e) => {
		e.preventDefault();
		alert("Account created successfully! (Demo only)");
		setShowRegisterModal(false);
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
			{/* Header */}
			<header className="bg-white dark:bg-gray-900 shadow-sm sticky top-0 z-40">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
					<div className="flex items-center justify-between">
						<div className="flex items-center space-x-3">
							<div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
								<span className="text-white font-bold text-lg">
									K8
								</span>
							</div>
							<div>
								<h1 className="text-2xl font-bold text-gray-900 dark:text-white">
									PyK8s-Lab
								</h1>
								<p className="text-xs text-gray-500 dark:text-gray-400">
									Prototype v0.1
								</p>
							</div>
						</div>
						<div className="flex space-x-4">
							<Link
								href="/login"
								className="px-4 py-2 text-blue-600 hover:text-blue-800 font-medium transition-colors"
							>
								Login
							</Link>
							<Link
								href="/register"
								className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-all duration-200 hover:shadow-lg"
							>
								Register
							</Link>
						</div>
					</div>
				</div>
			</header>

			{/* Hero Section */}
			<main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
				<div className="text-center">
					<div className="mb-8">
						<span className="inline-block px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium mb-4">
							🚀 Self-Service Kubernetes Playground
						</span>
					</div>

					<h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
						DOES THIS UPDATE?
					</h1>

					<p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
						PyK8s-Lab provides developers and learners with isolated
						Kubernetes clusters in minutes, not hours. Perfect for
						testing, learning, and rapid prototyping with automatic
						cleanup and resource management.
					</p>

					<div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
						<Link
							href="/register"
							className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 font-semibold text-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
						>
							Get Started Free
						</Link>
						<Link
							href="/login"
							className="px-8 py-4 border-2 border-blue-600 text-blue-600 rounded-xl hover:bg-blue-600 hover:text-white font-semibold text-lg transition-all duration-200"
						>
							Sign In
						</Link>
					</div>

					{/* Key Features */}
					<div className="grid md:grid-cols-3 gap-8 mt-20">
						<div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
							<div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mb-6 mx-auto">
								<svg
									className="w-8 h-8 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M13 10V3L4 14h7v7l9-11h-7z"
									/>
								</svg>
							</div>
							<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
								Fast Provisioning
							</h3>
							<p className="text-gray-600 dark:text-gray-300 mb-4">
								Get your Kubernetes cluster ready in under 3
								minutes using KinD (Kubernetes in Docker). No
								complex setup required.
							</p>
							<div className="text-sm text-green-600 dark:text-green-400 font-medium">
								P90 &lt; 3 minutes cluster readiness
							</div>
						</div>

						<div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
							<div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center mb-6 mx-auto">
								<svg
									className="w-8 h-8 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
									/>
								</svg>
							</div>
							<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
								Isolated & Secure
							</h3>
							<p className="text-gray-600 dark:text-gray-300 mb-4">
								Each cluster runs in complete isolation with
								proper multi-tenancy. JWT authentication and
								encrypted kubeconfig storage.
							</p>
							<div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
								Data plane + Control plane isolation
							</div>
						</div>

						<div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
							<div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mb-6 mx-auto">
								<svg
									className="w-8 h-8 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</div>
							<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
								Ephemeral Clusters
							</h3>
							<p className="text-gray-600 dark:text-gray-300 mb-4">
								Automatic cleanup with configurable TTL prevents
								resource waste. Focus on learning and testing
								without infrastructure management.
							</p>
							<div className="text-sm text-purple-600 dark:text-purple-400 font-medium">
								&gt;95% automatic cleanup success
							</div>
						</div>
					</div>

					{/* Technology Stack */}
					<div className="mt-24 bg-white dark:bg-gray-800 rounded-3xl p-10 shadow-xl border border-gray-100 dark:border-gray-700">
						<h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-12 text-center">
							Built with Modern Technology
						</h2>
						<div className="grid md:grid-cols-3 lg:grid-cols-6 gap-8">
							<div className="text-center">
								<div className="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl flex items-center justify-center mb-4 mx-auto">
									<span className="text-white font-bold text-lg">
										FA
									</span>
								</div>
								<h4 className="font-semibold text-gray-900 dark:text-white mb-2">
									FastAPI
								</h4>
								<p className="text-sm text-gray-600 dark:text-gray-300">
									High-performance async Python backend
								</p>
							</div>

							<div className="text-center">
								<div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center mb-4 mx-auto">
									<span className="text-white font-bold text-lg">
										⚛️
									</span>
								</div>
								<h4 className="font-semibold text-gray-900 dark:text-white mb-2">
									React + Next.js
								</h4>
								<p className="text-sm text-gray-600 dark:text-gray-300">
									Modern web UI with TypeScript
								</p>
							</div>

							<div className="text-center">
								<div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl flex items-center justify-center mb-4 mx-auto">
									<span className="text-white font-bold text-lg">
										🐘
									</span>
								</div>
								<h4 className="font-semibold text-gray-900 dark:text-white mb-2">
									PostgreSQL
								</h4>
								<p className="text-sm text-gray-600 dark:text-gray-300">
									Reliable, feature-rich database
								</p>
							</div>

							<div className="text-center">
								<div className="w-16 h-16 bg-gradient-to-br from-red-600 to-orange-600 rounded-2xl flex items-center justify-center mb-4 mx-auto">
									<span className="text-white font-bold text-lg">
										📦
									</span>
								</div>
								<h4 className="font-semibold text-gray-900 dark:text-white mb-2">
									Redis
								</h4>
								<p className="text-sm text-gray-600 dark:text-gray-300">
									Caching and background tasks
								</p>
							</div>

							<div className="text-center">
								<div className="w-16 h-16 bg-gradient-to-br from-blue-700 to-purple-700 rounded-2xl flex items-center justify-center mb-4 mx-auto">
									<span className="text-white font-bold text-lg">
										☸️
									</span>
								</div>
								<h4 className="font-semibold text-gray-900 dark:text-white mb-2">
									KinD
								</h4>
								<p className="text-sm text-gray-600 dark:text-gray-300">
									Kubernetes in Docker
								</p>
							</div>

							<div className="text-center">
								<div className="w-16 h-16 bg-gradient-to-br from-gray-700 to-gray-900 rounded-2xl flex items-center justify-center mb-4 mx-auto">
									<span className="text-white font-bold text-lg">
										🐳
									</span>
								</div>
								<h4 className="font-semibold text-gray-900 dark:text-white mb-2">
									Docker + K8s
								</h4>
								<p className="text-sm text-gray-600 dark:text-gray-300">
									Containerized deployment
								</p>
							</div>
						</div>
					</div>

					{/* Use Cases */}
					<div className="mt-24">
						<h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-16 text-center">
							Perfect for Every Use Case
						</h2>
						<div className="grid md:grid-cols-2 gap-12">
							<div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-8 rounded-2xl">
								<div className="text-4xl mb-4">🚀</div>
								<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
									Developers
								</h3>
								<ul className="space-y-3 text-gray-700 dark:text-gray-300">
									<li className="flex items-start">
										<span className="text-blue-500 mr-3 mt-1">
											•
										</span>
										Test applications in isolated
										environments
									</li>
									<li className="flex items-start">
										<span className="text-blue-500 mr-3 mt-1">
											•
										</span>
										Experiment with new Kubernetes features
									</li>
									<li className="flex items-start">
										<span className="text-blue-500 mr-3 mt-1">
											•
										</span>
										Debug production issues safely
									</li>
									<li className="flex items-start">
										<span className="text-blue-500 mr-3 mt-1">
											•
										</span>
										Rapid prototyping and development
									</li>
								</ul>
							</div>

							<div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-8 rounded-2xl">
								<div className="text-4xl mb-4">🎓</div>
								<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
									Students & Learners
								</h3>
								<ul className="space-y-3 text-gray-700 dark:text-gray-300">
									<li className="flex items-start">
										<span className="text-purple-500 mr-3 mt-1">
											•
										</span>
										Learn Kubernetes without complex setup
									</li>
									<li className="flex items-start">
										<span className="text-purple-500 mr-3 mt-1">
											•
										</span>
										Practice with real clusters
									</li>
									<li className="flex items-start">
										<span className="text-purple-500 mr-3 mt-1">
											•
										</span>
										Follow tutorials and courses
									</li>
									<li className="flex items-start">
										<span className="text-purple-500 mr-3 mt-1">
											•
										</span>
										Zero-cost learning environment
									</li>
								</ul>
							</div>
						</div>
					</div>

					{/* API Features */}
					<div className="mt-24 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-3xl p-10">
						<h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-12 text-center">
							Complete API & CLI Access
						</h2>
						<div className="grid md:grid-cols-2 gap-12">
							<div>
								<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
									🌐 REST API + WebSockets
								</h3>
								<div className="bg-gray-900 rounded-xl p-6 text-green-400 font-mono text-sm">
									<div className="mb-2">POST /auth/token</div>
									<div className="mb-2">GET /clusters/</div>
									<div className="mb-2">POST /clusters/</div>
									<div className="mb-2">
										DELETE /clusters/{`{id}`}
									</div>
									<div className="text-blue-400">
										WS /ws # Real-time updates
									</div>
								</div>
							</div>

							<div>
								<h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
									💻 Python CLI
								</h3>
								<div className="bg-gray-900 rounded-xl p-6 text-green-400 font-mono text-sm">
									<div className="mb-2">
										$ pyk8s auth login
									</div>
									<div className="mb-2">
										$ pyk8s cluster create --name test
									</div>
									<div className="mb-2">
										$ pyk8s cluster list
									</div>
									<div className="mb-2">
										$ pyk8s cluster get-kubeconfig test
									</div>
									<div className="text-blue-400">
										$ pyk8s cluster delete test
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</main>

			{/* Footer */}
			<footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-24">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
					<div className="text-center">
						<div className="flex items-center justify-center space-x-3 mb-6">
							<div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
								<span className="text-white font-bold text-sm">
									K8
								</span>
							</div>
							<span className="text-2xl font-bold text-gray-900 dark:text-white">
								PyK8s-Lab
							</span>
							<span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-xs font-medium">
								Prototype v0.1
							</span>
						</div>
						<p className="text-gray-600 dark:text-gray-400 mb-6">
							Self-service, on-demand Kubernetes playground for
							developers and learners
						</p>
						<div className="flex justify-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
							<span>Built with FastAPI + React + Next.js</span>
							<span>•</span>
							<span>&copy; 2025 PyK8s-Lab Project</span>
						</div>
					</div>
				</div>
			</footer>

			{/* Login Modal */}
			{showLoginModal && (
				<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
					<div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full shadow-2xl">
						<div className="flex justify-between items-center mb-6">
							<h2 className="text-2xl font-bold text-gray-900 dark:text-white">
								Sign In to PyK8s-Lab
							</h2>
							<button
								onClick={() => setShowLoginModal(false)}
								className="text-gray-400 hover:text-gray-600 p-2"
							>
								<svg
									className="w-6 h-6"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M6 18L18 6M6 6l12 12"
									/>
								</svg>
							</button>
						</div>
						<form onSubmit={handleLogin}>
							<div className="mb-4">
								<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Email Address
								</label>
								<input
									type="email"
									required
									className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									placeholder="Enter your email"
								/>
							</div>
							<div className="mb-6">
								<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Password
								</label>
								<input
									type="password"
									required
									className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									placeholder="Enter your password"
								/>
							</div>
							<button
								type="submit"
								className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium"
							>
								Sign In
							</button>
						</form>
						<p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
							Don&apos;t have an account?{" "}
							<button
								onClick={() => {
									setShowLoginModal(false);
									setShowRegisterModal(true);
								}}
								className="text-blue-600 hover:text-blue-500 font-medium"
							>
								Create one
							</button>
						</p>
					</div>
				</div>
			)}

			{/* Register Modal */}
			{showRegisterModal && (
				<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
					<div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full shadow-2xl">
						<div className="flex justify-between items-center mb-6">
							<h2 className="text-2xl font-bold text-gray-900 dark:text-white">
								Join PyK8s-Lab
							</h2>
							<button
								onClick={() => setShowRegisterModal(false)}
								className="text-gray-400 hover:text-gray-600 p-2"
							>
								<svg
									className="w-6 h-6"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d="M6 18L18 6M6 6l12 12"
									/>
								</svg>
							</button>
						</div>
						<form onSubmit={handleRegister}>
							<div className="mb-4">
								<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Email Address
								</label>
								<input
									type="email"
									required
									className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									placeholder="Enter your email"
								/>
							</div>
							<div className="mb-4">
								<label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									Password
								</label>
								<input
									type="password"
									required
									className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									placeholder="Create a strong password"
								/>
							</div>
							<div className="mb-6">
								<label className="flex items-start">
									<input
										type="checkbox"
										required
										className="mt-1 mr-3"
									/>
									<span className="text-sm text-gray-600 dark:text-gray-400">
										I agree to use PyK8s-Lab for testing and
										learning purposes only. Clusters will be
										automatically deleted according to TTL
										policy.
									</span>
								</label>
							</div>
							<button
								type="submit"
								className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium"
							>
								Create Account
							</button>
						</form>
						<p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
							Already have an account?{" "}
							<button
								onClick={() => {
									setShowRegisterModal(false);
									setShowLoginModal(true);
								}}
								className="text-blue-600 hover:text-blue-500 font-medium"
							>
								Sign in
							</button>
						</p>
					</div>
				</div>
			)}
		</div>
	);
}
