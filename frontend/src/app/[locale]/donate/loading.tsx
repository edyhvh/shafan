export default function DonateLoading() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="space-y-6 font-ui-latin text-gray animate-pulse">
          {/* Skeleton for wallet rows */}
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center justify-center gap-3">
              <div className="w-6 h-6 bg-gray/20 rounded" />
              <div className="w-20 h-5 bg-gray/20 rounded" />
              <div className="w-48 h-4 bg-gray/20 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
