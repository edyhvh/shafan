import { DONATION_CONFIG } from '@/lib/config';
import CopyableWallet from '@/components/CopyableWallet';

// Pre-render this page for all locales at build time
export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'es' }, { locale: 'he' }];
}

// Inline SVG icons - rendered on server, no client JS needed
const EthereumIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 320 512" fill="currentColor">
    <path d="M311.9 260.8L160 353.6 8 260.8 160 0l151.9 260.8zM160 383.4L8 290.6 160 512l152-221.4-152 92.8z" />
  </svg>
);

const BitcoinIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 512 512" fill="currentColor">
    <path d="M504 256c0 136.967-111.033 248-248 248S8 392.967 8 256 119.033 8 256 8s248 111.033 248 248zm-141.651-35.33c4.937-32.999-20.191-50.739-54.55-62.573l11.146-44.702-27.213-6.781-10.851 43.524c-7.154-1.783-14.502-3.464-21.803-5.13l10.929-43.81-27.198-6.781-11.153 44.686c-5.922-1.349-11.735-2.682-17.377-4.084l.031-.14-37.53-9.37-7.239 29.062s20.191 4.627 19.765 4.913c11.022 2.751 13.014 10.044 12.68 15.825l-12.696 50.925c.76.194 1.744.473 2.829.907-.907-.225-1.876-.473-2.876-.713l-17.796 71.338c-1.349 3.348-4.767 8.37-12.471 6.464.271.395-19.78-4.937-19.78-4.937l-13.51 31.147 35.414 8.827c6.588 1.651 13.045 3.379 19.4 5.006l-11.262 45.213 27.182 6.781 11.153-44.733a1038.209 1038.209 0 0 0 21.687 5.627l-11.115 44.523 27.213 6.781 11.262-45.128c46.404 8.781 81.299 5.239 95.986-36.727 11.836-33.79-.589-53.281-25.004-65.991 17.78-4.098 31.174-15.792 34.747-39.949zm-62.177 87.179c-8.41 33.79-65.308 15.523-83.755 10.943l14.944-59.899c18.446 4.603 77.6 13.717 68.811 48.956zm8.417-87.667c-7.673 30.736-55.031 15.12-70.393 11.292l13.548-54.327c15.363 3.828 64.836 10.973 56.845 43.035z" />
  </svg>
);

const SolanaIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 397.7 311.7" fill="currentColor">
    <path d="M64.6 237.9c2.4-2.4 5.7-3.8 9.2-3.8h317.4c5.8 0 8.7 7 4.6 11.1l-62.7 62.7c-2.4 2.4-5.7 3.8-9.2 3.8H6.5c-5.8 0-8.7-7-4.6-11.1l62.7-62.7z" />
    <path d="M64.6 3.8C67.1 1.4 70.4 0 73.8 0h317.4c5.8 0 8.7 7 4.6 11.1l-62.7 62.7c-2.4 2.4-5.7 3.8-9.2 3.8H6.5c-5.8 0-8.7-7-4.6-11.1L64.6 3.8z" />
    <path d="M333.1 120.1c-2.4-2.4-5.7-3.8-9.2-3.8H6.5c-5.8 0-8.7 7-4.6 11.1l62.7 62.7c2.4 2.4 5.7 3.8 9.2 3.8h317.4c5.8 0 8.7-7 4.6-11.1l-62.7-62.7z" />
  </svg>
);

const TetherIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 339.43 295.27">
    <path fill="currentColor" d="M62.15,1.45l-61.89,130a2.52,2.52,0,0,0,.54,2.94L167.95,294.56a2.55,2.55,0,0,0,3.53,0L338.63,134.4a2.52,2.52,0,0,0,.54-2.94l-61.89-130A2.5,2.5,0,0,0,275,0H64.45a2.5,2.5,0,0,0-2.3,1.45h0Z" />
    <path fill="#fff" d="M191.19,144.8v0c-1.2.09-7.4,0.46-21.23,0.46-11,0-18.81-.33-21.55-0.46v0c-42.51-1.87-74.24-9.27-74.24-18.13s31.73-16.25,74.24-18.15v28.91c2.78,0.19,10.93.67,21.74,0.67,13,0,19.82-.56,21-0.66v-28.9c42.42,1.89,74.08,9.29,74.08,18.13s-31.65,16.24-74.08,18.12h0Zm0-39.25V79.68h59.2V40.23H89.21V79.68h59.2v25.86c-48.11,2.21-84.29,11.74-84.29,23.16s36.18,20.94,84.29,23.16v82.9h42.78v-82.93c48-2.21,84.12-11.73,84.12-23.14s-36.09-20.93-84.12-23.15h0Z" />
  </svg>
);

const USDCIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 2000 2000">
    <path fill="currentColor" d="M1000 2000c554.17 0 1000-445.83 1000-1000S1554.17 0 1000 0 0 445.83 0 1000s445.83 1000 1000 1000z"/>
    <path fill="#fff" d="M1275 1158.33c0-145.83-87.5-195.83-262.5-216.66-125-16.67-150-50-150-108.34s41.67-95.83 125-95.83c75 0 116.67 25 137.5 87.5 4.17 12.5 16.67 20.83 29.17 20.83h66.66c16.67 0 29.17-12.5 29.17-29.16v-4.17c-16.67-91.67-91.67-162.5-187.5-170.83v-100c0-16.67-12.5-29.17-33.33-33.34h-62.5c-16.67 0-29.17 12.5-33.34 33.34v95.83c-125 16.67-204.16 100-204.16 204.17 0 137.5 83.33 191.66 258.33 212.5 116.67 20.83 154.17 45.83 154.17 112.5s-58.34 112.5-137.5 112.5c-108.34 0-145.84-45.84-158.34-108.34-4.16-16.66-16.66-25-29.16-25h-70.84c-16.66 0-29.16 12.5-29.16 29.17v4.17c16.66 104.16 83.33 179.16 220.83 200v100c0 16.66 12.5 29.16 33.33 33.33h62.5c16.67 0 29.17-12.5 33.34-33.33v-100c125-20.84 208.33-108.34 208.33-220.84z"/>
    <path fill="#fff" d="M787.5 1595.83c-325-116.66-491.67-479.16-370.83-800 62.5-166.67 191.66-295.84 358.33-358.34 16.67-8.33 25-20.83 25-41.66v-58.34c0-16.66-8.33-29.16-25-33.33-4.17 0-12.5 0-16.67 4.17-395.83 125-612.5 545.83-487.5 941.66 75 233.34 254.17 412.5 487.5 487.5 16.67 8.34 33.34 0 37.5-16.66 4.17-4.17 4.17-8.34 4.17-16.67v-58.33c0-12.5-12.5-29.17-12.5-50zm441.67-1337.5c-16.67-8.33-33.34 0-37.5 16.67-4.17 4.16-4.17 8.33-4.17 16.66v58.34c0 16.66 8.33 33.33 25 41.66 325 116.67 491.67 479.17 370.83 800-62.5 166.67-191.66 295.84-358.33 358.34-16.67 8.33-25 20.83-25 41.66v58.34c0 16.66 8.33 29.16 25 33.33 4.17 0 12.5 0 16.67-4.17 395.83-125 612.5-545.83 487.5-941.66-75-237.5-258.34-416.67-500-479.17z"/>
  </svg>
);

const GithubSponsorsIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path
      fillRule="evenodd"
      d="M4.25 2.5c-1.336 0-2.75 1.164-2.75 3 0 2.15 1.58 4.144 3.365 5.682A20.565 20.565 0 008 13.393a20.561 20.561 0 003.135-2.211C12.92 9.644 14.5 7.65 14.5 5.5c0-1.836-1.414-3-2.75-3-1.373 0-2.609.986-3.029 2.456a.75.75 0 01-1.442 0C6.859 3.486 5.623 2.5 4.25 2.5zM8 14.25l-.345.666-.002-.001-.006-.003-.018-.01a7.643 7.643 0 01-.31-.17 22.075 22.075 0 01-3.434-2.414C2.045 10.731 0 8.35 0 5.5 0 2.836 2.086 1 4.25 1 5.797 1 7.153 1.802 8 3.02 8.847 1.802 10.203 1 11.75 1 13.914 1 16 2.836 16 5.5c0 2.85-2.045 5.231-3.885 6.818a22.08 22.08 0 01-3.744 2.584l-.018.01-.006.003h-.002L8 14.25zm0 0l.345.666a.752.752 0 01-.69 0L8 14.25z"
    />
  </svg>
);

const CreditCardIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v1h14V4a1 1 0 0 0-1-1H2zm13 4H1v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V7z" />
    <path d="M2 10a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-1z" />
  </svg>
);

export default function DonatePage() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="space-y-6 font-ui-latin text-gray">
          {/* Ethereum */}
          <CopyableWallet
            icon={
              <div className="flex items-center gap-1">
                <EthereumIcon className="w-6 h-6" />
                <TetherIcon className="w-5 h-5" />
                <USDCIcon className="w-5 h-5" />
              </div>
            }
            name="Ethereum"
            address={DONATION_CONFIG.wallets.ethereum}
          />

          {/* Bitcoin */}
          <CopyableWallet
            icon={<BitcoinIcon className="w-6 h-6" />}
            name="Bitcoin"
            address={DONATION_CONFIG.wallets.bitcoin}
          />

          {/* Solana */}
          <CopyableWallet
            icon={
              <div className="flex items-center gap-1">
                <SolanaIcon className="w-6 h-6" />
                <TetherIcon className="w-5 h-5" />
                <USDCIcon className="w-5 h-5" />
              </div>
            }
            name="Solana"
            address={DONATION_CONFIG.wallets.solana}
          />

          {/* GitHub Sponsor */}
          <div className="flex items-center justify-center gap-3 text-lg">
            <div className="flex items-center gap-1">
              <GithubSponsorsIcon className="w-6 h-6" />
              <CreditCardIcon className="w-5 h-5" />
            </div>
            <span className="font-medium">Github Sponsor</span>
            <a
              href={DONATION_CONFIG.githubSponsor}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray/70 hover:text-black underline underline-offset-2 transition-colors"
            >
              @edyhvh
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
