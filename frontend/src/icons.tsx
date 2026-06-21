// Minimal inline icons (stroke = currentColor) so they inherit card accents
// and stay crisp on a big TV.
type P = { size?: number; className?: string };
const base = (size: number) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
});

export const Thermo = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
  </svg>
);

export const Car = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M5 13l1.5-4.5A2 2 0 0 1 8.4 7h7.2a2 2 0 0 1 1.9 1.5L19 13" />
    <path d="M3 13h18v4a1 1 0 0 1-1 1h-1a2 2 0 0 1-4 0H9a2 2 0 0 1-4 0H4a1 1 0 0 1-1-1z" />
    <circle cx="7.5" cy="17" r="1.4" />
    <circle cx="16.5" cy="17" r="1.4" />
  </svg>
);

export const Home = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M3 11l9-8 9 8" />
    <path d="M5 10v10h14V10" />
    <path d="M9 20v-6h6v6" />
  </svg>
);

export const Pin = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z" />
    <circle cx="12" cy="10" r="2.5" />
  </svg>
);

export const Battery = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <rect x="2" y="8" width="16" height="8" rx="1.5" />
    <path d="M20 11v2" />
  </svg>
);

export const Check = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M20 6L9 17l-5-5" />
  </svg>
);

export const Sensor = ({ size = 24, className }: P) => (
  <svg {...base(size)} className={className}>
    <circle cx="12" cy="12" r="2" />
    <path d="M16.2 7.8a6 6 0 0 1 0 8.4M7.8 16.2a6 6 0 0 1 0-8.4" />
    <path d="M19 5a10 10 0 0 1 0 14M5 19A10 10 0 0 1 5 5" />
  </svg>
);
