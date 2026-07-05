const PROJECTS = [
  {
    title: "Multi-Agent CV Chatbot",
    description:
      "LangGraph-powered multi-agent system that intelligently routes questions about my profile to specialist agents (skills, projects, contact, RAG). Includes voice I/O with a cloned voice via ElevenLabs.",
    tech: ["LangGraph", "FastAPI", "FAISS", "RAG", "ElevenLabs", "React"],
    highlight: true,
  },
  {
    title: "Conversational RAG Agent",
    description:
      "End-to-end RAG agent with document ingestion, vector indexing (Chroma), tool usage, and integration with external APIs. Built for production with LangChain.",
    tech: ["LangChain", "Chroma", "Python", "FastAPI"],
    highlight: false,
  },
  {
    title: "LLM Agent Orchestration",
    description:
      "Multi-agent workflows with task coordination, tool usage, and conditional routing using LangGraph. Designed for complex, stateful AI pipelines.",
    tech: ["LangGraph", "Python", "LLM APIs"],
    highlight: false,
  },
  {
    title: "AI Data Pipelines at IMT Nord Europe",
    description:
      "Built and deployed data processing pipelines and AI services (APIs + pipelines) in a professional R&D environment. April 2023 – August 2024.",
    tech: ["Python", "Docker", "CI/CD", "Azure AI", "MLflow"],
    highlight: false,
  },
]

export default function Projects() {
  return (
    <section id="projects" className="py-24 px-6 max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold text-white text-center mb-4">Projects & Experience</h2>
      <p className="text-slate-400 text-center mb-14">
        Things I've built and shipped
      </p>
      <div className="grid md:grid-cols-2 gap-6">
        {PROJECTS.map((project) => (
          <div
            key={project.title}
            className={`bg-card border rounded-xl p-6 hover:border-primary transition flex flex-col gap-4 ${
              project.highlight ? "border-primary/50" : "border-slate-700"
            }`}
          >
            {project.highlight && (
              <span className="text-xs text-primary font-mono uppercase tracking-widest">
                ★ Featured
              </span>
            )}
            <h3 className="text-white font-semibold text-lg">{project.title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed flex-1">
              {project.description}
            </p>
            <div className="flex flex-wrap gap-2">
              {project.tech.map((t) => (
                <span
                  key={t}
                  className="text-xs bg-primary/10 text-primary border border-primary/20 px-3 py-1 rounded-full"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
