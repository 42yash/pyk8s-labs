// frontend/src/components/InvitationsList.js
"use client";

import { useAcceptInvitationMutation, useGetPendingInvitationsForUserQuery, useRejectInvitationMutation } from "@/lib/store/apiSlice";

export default function InvitationsList() {
    const { data: invitations, isLoading, error } = useGetPendingInvitationsForUserQuery();
    const [acceptInvitation, { isLoading: isAccepting }] = useAcceptInvitationMutation();
    const [rejectInvitation, { isLoading: isRejecting }] = useRejectInvitationMutation();

    if (isLoading || !invitations || invitations.length === 0) {
        return null;
    }

    const handleAccept = (token) => {
        acceptInvitation(token);
    };

    const handleReject = (token) => {
        rejectInvitation(token);
    };

    return (
        <div className="mb-8 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-blue-800 dark:text-blue-200">You have pending invitations!</h2>
            <ul className="space-y-3">
                {invitations.map(invite => (
                    <li key={invite.id} className="bg-white dark:bg-gray-800 p-4 rounded-md shadow-sm flex flex-col sm:flex-row justify-between items-center">
                        <p className="text-gray-700 dark:text-gray-300 mb-2 sm:mb-0">
                            You have been invited to join the team: <span className="font-bold">{invite.team.name}</span>
                        </p>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => handleAccept(invite.token)}
                                disabled={isAccepting || isRejecting}
                                className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors disabled:opacity-50"
                            >
                                {isAccepting ? 'Accepting...' : 'Accept'}
                            </button>
                            <button
                                onClick={() => handleReject(invite.token)}
                                disabled={isAccepting || isRejecting}
                                className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors disabled:opacity-50"
                            >
                                {isRejecting ? 'Rejecting...' : 'Reject'}
                            </button>
                        </div>
                    </li>
                ))}
            </ul>
            {error && <p className="text-red-500 mt-4">Could not load invitations.</p>}
        </div>
    );
}