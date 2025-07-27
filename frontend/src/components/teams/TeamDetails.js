// frontend/src/components/teams/TeamDetails.js
import { useGetTeamDetailsQuery } from '@/lib/store/apiSlice';
import { useSelector } from 'react-redux';
import InviteMemberForm from './InviteMemberForm';
import TeamMemberList from './TeamMemberList';

const TeamDetails = ({ teamId }) => {
    // Get the current user's info from the auth slice
    const { user: currentUser } = useSelector((state) => state.auth);

    // Fetch team details using the RTK Query hook
    const {
        data: team,
        isLoading,
        isError,
        error,
    } = useGetTeamDetailsQuery(teamId, {
        // Only run the query if a teamId is provided
        skip: !teamId,
    });

    if (!teamId) {
        return (
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow h-full flex items-center justify-center">
                <p className="text-gray-500 text-center">Select a team from the list to see its members and manage settings.</p>
            </div>
        );
    }

    if (isLoading) return <div>Loading team details...</div>;
    if (isError) return <div className="text-red-500">Error: {error.data?.detail || 'Failed to fetch team details'}</div>;

    // Find the current user's role within this team
    const currentUserMembership = team?.members.find(
        (member) => member.id === currentUser?.id
    );
    const currentUserRole = currentUserMembership?.role;

    return (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
            <h3 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">{team.name}</h3>

            {/* Member List Component */}
            <TeamMemberList members={team.members} />

            {/* Conditionally render the invite form only for admins */}
            {currentUserRole === 'admin' && (
                <InviteMemberForm teamId={teamId} />
            )}
        </div>
    );
};

export default TeamDetails;