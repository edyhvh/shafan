'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { getLocaleFromPath } from '@/lib/locale';
import { t } from '@/lib/translations';
import { WarningIcon } from './icons';

const GITHUB_DISCUSSIONS_URL = 'https://github.com/edyhvh/shafan/discussions';

export default function CorrectionWarning() {
  const pathname = usePathname();
  const locale = getLocaleFromPath(pathname);

  return (
    <div className="fixed top-4 left-4 z-40">
      <div className="bg-yellow-300/80 backdrop-blur-sm border-2 border-yellow-400/60 rounded-lg px-2 py-2.5 shadow-lg flex items-start gap-1.5 max-w-[200px]">
        <WarningIcon className="w-4 h-4 text-black flex-shrink-0 mt-0.5" />
        <p className="text-[10px] sm:text-[11px] text-black font-medium leading-tight">
          {t('correction_warning_text', locale)}{' '}
          <Link
            href={GITHUB_DISCUSSIONS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="underline font-semibold hover:text-black/80 transition-colors"
          >
            {t('correction_warning_link', locale)}
          </Link>
        </p>
      </div>
    </div>
  );
}

