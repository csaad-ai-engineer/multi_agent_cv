const LINKS = [
  { label: "Email", value: "chaima.zidi.ingia@gmail.com", href: "mailto:chaima.zidi.ingia@gmail.com", icon: "✉️" },
  { label: "Phone", value: "+33 758 949 591", href: "tel:+33758949591", icon: "📞" },
  { label: "GitHub", value: "github.com/csaad-ai-engineer", href: "https://github.com/csaad-ai-engineer", icon: "🐙" },
  { label: "Location", value: "France", href: null, icon: "📍" },
]

export default function Contact() {
  return (
    <section id="contact" className="py-24 px-6 max-w-3xl mx-auto text-center">
      <h2 className="text-3xl font-bold text-white mb-4">Let's Talk</h2>
      <p className="text-slate-400 mb-14">
        Open to R&D positions, freelance missions, and research collaborations.
      </p>
      <div className="grid sm:grid-cols-2 gap-4">
        {LINKS.map(({ label, value, href, icon }) => (
          <div
            key={label}
            className="bg-card border border-slate-700 hover:border-primary rounded-xl p-5 flex items-center gap-4 transition"
          >
            <span className="text-2xl">{icon}</span>
            <div className="text-left">
              <p className="text-slate-500 text-xs uppercase tracking-widest mb-1">{label}</p>
              {href ? (
                <a
                  href={href}
                  target={href.startsWith("http") ? "_blank" : undefined}
                  rel="noopener noreferrer"
                  className="text-white hover:text-primary transition text-sm font-medium"
                >
                  {value}
                </a>
              ) : (
                <p className="text-white text-sm font-medium">{value}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
