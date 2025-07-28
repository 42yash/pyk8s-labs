// frontend/src/components/teams/TeamMemberList.js
const TeamMemberList = ({ members = [] }) => {
    return (
        <div>
            <h4 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200">Team Members</h4>
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {members.map((member) => (
                    <li key={member.id} className="py-3 flex justify-between items-center">
                        <div><p className="font-medium text-gray-900 dark:text-white">{member.email}</p></div>
                        <span className="px-2 py-1 text-xs font-semibold leading-5 rounded-full bg-gray-200 text-gray-800 dark:bg-gray-600 dark:text-gray-100">{member.role}</span>
                    </li>
                ))}
                {members.length === 0 && <p className="text-gray-500">This team has no members.</p>}
            </ul>
        </div>
    );
};
export default TeamMemberList;