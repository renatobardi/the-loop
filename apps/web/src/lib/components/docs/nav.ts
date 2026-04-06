export type NavItem = {
	slug: string;
	label: string;
	icon: string;
	visibility: 'all' | 'admin';
};

export type PersonaKey = 'developer' | 'it-manager' | 'operator' | 'support' | 'qa' | 'security';

export type Persona = {
	key: PersonaKey;
	label: string;
	description: string;
	primarySections: string[];
};

export const USER_SECTIONS: NavItem[] = [
	{ slug: 'getting-started', label: 'Getting Started', icon: '🚀', visibility: 'all' },
	{ slug: 'incidents', label: 'Incidents', icon: '🔥', visibility: 'all' },
	{ slug: 'postmortems', label: 'Postmortems', icon: '📋', visibility: 'all' },
	{ slug: 'analytics', label: 'Analytics', icon: '📊', visibility: 'all' },
	{ slug: 'semgrep', label: 'Semgrep', icon: '🛡️', visibility: 'all' },
	{ slug: 'api-keys', label: 'API Keys', icon: '🔑', visibility: 'all' },
	{ slug: 'rules', label: 'Rules', icon: '📏', visibility: 'all' }
];

export const ADMIN_SECTIONS: NavItem[] = [
	{ slug: 'administration', label: 'Administration', icon: '⚙️', visibility: 'admin' },
	{ slug: 'security', label: 'Security', icon: '🔒', visibility: 'admin' },
	{ slug: 'api-reference', label: 'API Reference', icon: '📡', visibility: 'admin' }
];

export const PERSONAS: Persona[] = [
	{
		key: 'developer',
		label: 'Developer',
		description: 'Integrate the scanner into CI/CD pipelines',
		primarySections: ['semgrep', 'api-keys', 'rules']
	},
	{
		key: 'it-manager',
		label: 'IT Manager',
		description: 'Monitor incident metrics and team performance',
		primarySections: ['getting-started', 'analytics']
	},
	{
		key: 'operator',
		label: 'Operator',
		description: 'Manage incidents and on-call workflows',
		primarySections: ['incidents', 'postmortems', 'getting-started']
	},
	{
		key: 'support',
		label: 'Support',
		description: 'Track and resolve user-reported incidents',
		primarySections: ['incidents', 'postmortems']
	},
	{
		key: 'qa',
		label: 'QA',
		description: 'Validate scan rules and test coverage',
		primarySections: ['semgrep', 'rules']
	},
	{
		key: 'security',
		label: 'Security',
		description: 'Audit rules and manage API key scopes',
		primarySections: ['semgrep', 'api-keys', 'rules']
	}
];
