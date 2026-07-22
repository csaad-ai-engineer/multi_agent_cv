export default function Hero() {
  return (
    <section className="min-h-screen flex flex-col justify-center items-center text-center px-6 py-24">
      <p className="text-primary font-mono text-sm mb-4 tracking-widest uppercase">
        AI Engineer · R&D
      </p>
      <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
        Chaima <span className="text-primary">SAAD</span>
      </h1>
      <p className="text-slate-400 text-lg md:text-xl max-w-2xl mb-10 leading-relaxed">
        Building intelligent multi-agent systems, RAG pipelines, and production-ready
        GenAI applications. Passionate about LLM engineering and agentic AI.
      </p>
      <div className="flex flex-wrap gap-4 justify-center mb-12">
        <a
          href="mailto:chaima.zidi.ingia@gmail.com"
          className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-indigo-500 transition"
        >
          Get in touch
        </a>
        <a
          href="https://github.com/csaad-ai-engineer"
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-3 border border-slate-600 text-slate-300 rounded-lg font-medium hover:border-primary hover:text-primary transition"
        >
          GitHub
        </a>
      </div>
      <div className="flex flex-wrap gap-6 justify-center text-slate-500 text-sm">
        <span>📍 France</span>
        <span>🇫🇷 French · 🇬🇧 English · 🇸🇦 Arabic</span>
        <span>🚗 Permis B</span>
      </div>
      <a
        href="#skills"
        className="mt-20 text-slate-600 hover:text-primary transition animate-bounce"
        aria-label="Scroll down"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </a>
    </section>
  )
}
