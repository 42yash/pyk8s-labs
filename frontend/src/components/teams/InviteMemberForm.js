// frontend/src/components/teams/InviteMemberForm.js
import { useInviteMemberMutation } from '@/lib/store/apiSlice';
import { useState } from 'react';

const InviteMemberForm = ({ teamId }) => {
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('member');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [inviteMember, { isLoading }] = useInviteMemberMutation();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            await inviteMember({ teamId, inviteData: { email, role } }).unwrap();
            setSuccess(`Successfully invited ${email} to the team.`);
            setEmail('');
            setRole('member');
        } catch (err) {
            setError(err.data?.detail || 'Failed to invite member.');
        }
    };

    return (
        <div className="mt-8 border-t border-gray-200 dark:border-gray-700 pt-6">
            <h4 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">Invite New Member</h4>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:space-x-4 space-y-4 sm:space-y-0">
                    <input type="email" placeholder="user@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required className="flex-grow px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700" />
                    <select value={role} onChange={(e) => setRole(e.target.value)} className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700">
                        <option value="member">Member</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <button type="submit" disabled={isLoading || !email} className="w-full sm:w-auto px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors disabled:opacity-50">
                    {isLoading ? 'Sending...' : 'Send Invite'}
                </button>
            </form>
            {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            {success && <p className="text-green-500 text-sm mt-2">{success}</p>}
        </div>
    );
};

export default InviteMemberForm;