'use client';

import { useState } from 'react';

const CopyIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 512 512"
    fill="none"
    stroke="currentColor"
    strokeWidth="32"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect x="128" y="128" width="336" height="336" rx="57" ry="57" />
    <path d="M383.5 128l.5-24a56.16 56.16 0 00-56-56H112a64.19 64.19 0 00-64 64v216a56.16 56.16 0 0056 56h24" />
  </svg>
);

const CheckmarkIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 512 512"
    fill="none"
    stroke="currentColor"
    strokeWidth="32"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="416 128 192 384 96 288" />
  </svg>
);

interface CopyableWalletProps {
  icon: React.ReactNode;
  name: string;
  address: string;
}

export default function CopyableWallet({ icon, name, address }: CopyableWalletProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center justify-center gap-3 text-lg group">
      {icon}
      <span className="font-medium">{name}</span>
      <button
        onClick={handleCopy}
        className="flex items-center gap-2 text-gray/70 hover:text-black transition-colors cursor-pointer"
        title={`Copy ${name} address`}
      >
        <span className="font-mono text-sm">{address}</span>
        {copied ? (
          <CheckmarkIcon className="w-4 h-4 text-green-600" />
        ) : (
          <CopyIcon className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
      </button>
    </div>
  );
}

