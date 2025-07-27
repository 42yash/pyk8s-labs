// frontend/src/components/DashboardLayout.js
"use client";
import { logOut } from "@/lib/store/authSlice";
import Link from 'next/link';
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

export default function DashboardLayout({ children }) {
    const { token, user } = useSelector((state) => state.auth);
    const router = useRouter();
    const pathname = usePathname();
    const dispatch = useDispatch();

    useEffect(() => {
        if (!token) {
            router.push("/login");
        }
    }, [token, router]);

    const handleLogout = () => {
        dispatch(logOut());
        router.push("/");
    };

    if (!token) {
        return null;
    }

    const navLinkClasses = (path) =>
        `px-3 py-2 rounded-md text-sm font-medium transition-colors ${pathname === path
            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
        }`;

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <header className="bg-white dark:bg-gray-800 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <div className="flex items-center space-x-8">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                                <span className="text-white font-bold text-lg">K8</span>
                            </div>
                            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">PyK8s-Lab</h1>
                        </div>
                        <nav className="flex space-x-4">
                            <Link href="/dashboard" className={navLinkClasses('/dashboard')}>
                                Clusters
                            </Link>
                            <Link href="/dashboard/teams" className={navLinkClasses('/dashboard/teams')}>
                                Teams
                            </Link>
                        </nav>
                    </div>
                    <div className="flex items-center space-x-4">
                        <span className="text-gray-600 dark:text-gray-300 hidden sm:inline">{user?.email}</span>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </header>
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>
        </div>
    );
}