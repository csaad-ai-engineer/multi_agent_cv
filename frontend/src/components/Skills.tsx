const SKILLS = [
  {
    category: "Generative AI & Agents",
    icon: "🤖",
    items: ["LangGraph", "LangChain", "RAG", "MCP", "A2A", "Prompt Engineering", "LLM Engineering"],
  },
  {
    category: "Machine & Deep Learning",
    icon: "🧠",
    items: ["Python", "scikit-learn", "TensorFlow", "Model Evaluation", "Monitoring"],
  },
  {
    category: "APIs & Architecture",
    icon: "⚙️",
    items: ["FastAPI", "Flask", "REST APIs", "Microservices", "GenAI Systems Design", "OpenAI API"],
  },
  {
    category: "Data Engineering",
    icon: "🗄️",
    items: ["Data Pipelines", "PostgreSQL", "Chroma", "Neo4j", "Airflow", "Data Quality"],
  },
  {
    category: "MLOps & DevOps",
    icon: "🚀",
    items: ["Azure AI Services", "Docker", "CI/CD", "GitHub Actions", "MLflow", "Model Versioning"],
  },
]

export default function Skills() {
  return (
    <section id="skills" className="py-24 px-6 max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold text-white text-center mb-4">Technical Skills</h2>
      <p className="text-slate-400 text-center mb-14">
        What I bring to the table
      </p>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {SKILLS.map((group) => (
          <div
            key={group.category}
            className="bg-card border border-slate-700 rounded-xl p-6 hover:border-primary transition"
          >
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">{group.icon}</span>
              <h3 className="text-white font-semibold">{group.category}</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {group.items.map((item) => (
                <span
                  key={item}
                  className="text-xs bg-slate-700 text-slate-300 px-3 py-1 rounded-full"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
