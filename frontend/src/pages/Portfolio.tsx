import { Link } from "react-router-dom"
import Hero from "../components/Hero"
import Skills from "../components/Skills"
import Projects from "../components/Projects"
import Contact from "../components/Contact"
import ChatWidget from "../components/ChatWidget"

export default function Portfolio() {
  return (
    <div className="min-h-screen bg-surface text-slate-300">
      <nav className="fixed top-0 w-full z-40 bg-surface/80 backdrop-blur border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <span className="text-white font-bold text-lg">
            CS <span className="text-primary">·</span>
          </span>
          <div className="flex gap-6 text-sm text-slate-400 items-center">
            <a href="#skills"   className="hover:text-primary transition">Skills</a>
            <a href="#projects" className="hover:text-primary transition">Projects</a>
            <a href="#contact"  className="hover:text-primary transition">Contact</a>
            <Link
              to="/persona"
              className="flex items-center gap-2 px-4 py-1.5 bg-primary/10 border border-primary/30 text-primary rounded-full text-xs font-medium hover:bg-primary/20 transition"
            >
              <span className="animate-pulse">●</span> Talk to Chaima AI
            </Link>
          </div>
        </div>
      </nav>

      <main>
        <Hero />
        <Skills />
        <Projects />
        <Contact />
      </main>

      <footer className="text-center py-10 text-slate-600 text-sm border-t border-slate-800">
        Built with LangGraph · FastAPI · React · Ollama
      </footer>

      <ChatWidget />
    </div>
  )
}
