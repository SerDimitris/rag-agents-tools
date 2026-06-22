const STARS = Array.from({ length: 72 }, (_, index) => ({
  left: `${((index * 7919 + 104729) % 10000) / 100}%`,
  top: `${((index * 6271 + 8731) % 10000) / 100}%`,
  size: index % 5 === 0 ? 3 : index % 3 === 0 ? 2 : 1,
  delay: (index * 0.17) % 4,
  duration: 2 + (index % 5),
}))

export function RetroStarfield() {
  return (
    <div className="retro-starfield pointer-events-none absolute inset-0" aria-hidden>
      {STARS.map((star, index) => (
        <span
          key={index}
          className="retro-star"
          style={{
            left: star.left,
            top: star.top,
            width: star.size,
            height: star.size,
            animationDelay: `${star.delay}s`,
            animationDuration: `${star.duration}s`,
          }}
        />
      ))}
    </div>
  )
}
