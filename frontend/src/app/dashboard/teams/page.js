// frontend/src/app/dashboard/teams/page.js
"use client";

import DashboardLayout from "@/components/DashboardLayout";
import TeamDetails from "@/components/teams/TeamDetails"; // Import the new component
import { useCreateTeamMutation, useGetTeamsQuery } from "@/lib/store/apiSlice";
import { useState } from "react";

export default function TeamsPage() {
    const [selectedTeamId, setSelectedTeamId] = useState(null);
    const [newTeamName, setNewTeamName] = useState("");
    const [apiError, setApiError] = useState("");

    const { data: teams, isLoading, error } = useGetTeamsQuery();
    const [createTeam, { isLoading: isCreating }] = useCreateTeamMutation();

    const handleCreateTeam = async (e) => {
        e.preventDefault();
        if (!newTeamName || isCreating) return;
        setApiError("");

        try {
            await createTeam({ name: newTeamName }).unwrap();
            setNewTeamName(""); // Clear input on success
        } catch (err) {
            setApiError(err.data?.detail || "Failed to create team.");
        }
    };

    const teamListItemClasses = (teamId) =>
        `block w-full text-left p-4 rounded-lg transition-colors ${selectedTeamId === teamId
            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
            : 'hover:bg-gray-100 dark:hover:bg-gray-700'
        }`;

    return (
        <DashboardLayout>
            <div className="grid md:grid-cols-3 gap-8">
                {/* Left Column: Team List and Creation */}
                <div className="md:col-span-1 space-y-6">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                        <h2 className="text-xl font-bold mb-4">Create a New Team</h2>
                        <form onSubmit={handleCreateTeam} className="space-y-4">
                            <input
                                type="text"
                                value={newTeamName}
                                onChange={(e) => setNewTeamName(e.target.value)}
                                placeholder="my-awesome-team"
                                required
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700"
                            />
                            <button
                                type="submit"
                                disabled={isCreating || !newTeamName}
                                className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors disabled:opacity-50"
                            >
                                {isCreating ? "Creating..." : "Create Team"}
                            </button>
                            {apiError && <p className="text-red-500 text-sm mt-2">{apiError}</p>}
                        </form>
                    </div>

                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                        <h2 className="text-xl font-bold mb-4">Your Teams</h2>
                        {isLoading && <p>Loading teams...</p>}
                        {error && <p className="text-red-500">Failed to load teams.</p>}
                        {teams && (
                            <ul className="space-y-2">
                                {teams.map((team) => (
                                    <li key={team.id}>
                                        <button
                                            onClick={() => setSelectedTeamId(team.id)}
                                            className={teamListItemClasses(team.id)}
                                        >
                                            <span className="font-semibold">{team.name}</span>
                                        </button>
                                    </li>
                                ))}
                                {teams.length === 0 && <p className="text-gray-500">You are not a member of any teams yet.</p>}
                            </ul>
                        )}
                    </div>
                </div>

                {/* Right Column: Team Details */}
                <div className="md:col-span-2">
                    {/* Replace the placeholder with the real component */}
                    <TeamDetails teamId={selectedTeamId} />
                </div>
            </div>
        </DashboardLayout>
    );
}