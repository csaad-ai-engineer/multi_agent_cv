import { useState, useRef, useEffect } from "react"
import { Link } from "react-router-dom"

const API_URL = import.meta.env.VITE_API_URL || "/api"

type State = "idle" | "listening" | "thinking" | "speaking"

interface Turn {
  user: string
  assistant: string
}

const ORB_CONFIG: Record<State, { color: string; glow: string; label: string; speed: string }> = {
  idle:      { color: "#6366f1", glow: "rgba(99,102,241,0.5)",  label: "Tap to speak",  speed: "3s" },
  listening: { color: "#ef4444", glow: "rgba(239,68,68,0.6)",   label: "Listening…",    speed: "0.8s" },
  thinking:  { color: "#f59e0b", glow: "rgba(245,158,11,0.5)",  label: "Thinking…",     speed: "1.5s" },
  speaking:  { color: "#22c55e", glow: "rgba(34,197,94,0.5)",   label: "Speaking…",     speed: "1s" },
}

export default function Persona() {
  const [state, setState] = useState<State>("idle")
  const [transcript, setTranscript] = useState("")
  const [answer, setAnswer] = useState("")
  const [history, setHistory] = useState<Turn[]>([])
  const [error, setError] = useState("")

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioElRef = useRef<HTMLAudioElement | null>(null)
  const historyEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [history])

  async function handleOrbClick() {
    if (state === "listening") {
      stopRecording()
      return
    }
    if (state !== "idle") return
    startRecording()
  }

  function startRecording() {
    setError("")
    setTranscript("")
    setAnswer("")
    // Unlock audio element on user gesture so Safari allows playback later
    if (!audioElRef.current) {
      audioElRef.current = new Audio()
    }
    // Play silence to unlock — Safari requires play() inside a user gesture
    const silent = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA="
    audioElRef.current.src = silent
    audioElRef.current.play().catch(() => {})
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        processAudio()
      }
      recorder.start()
      mediaRecorderRef.current = recorder
      setState("listening")
    }).catch(() => setError("Microphone access denied."))
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop()
    setState("thinking")
  }

  async function processAudio() {
    try {
      // 1. Speech → Text
      const blob = new Blob(chunksRef.current, { type: "audio/webm" })
      const form = new FormData()
      form.append("audio", blob, "recording.webm")
      const sttRes = await fetch(`${API_URL}/voice/stt`, { method: "POST", body: form })
      const sttData = await sttRes.json()
      const question = sttData.text?.trim()
      if (!question) {
        setError("Couldn't hear anything. Try again.")
        setState("idle")
        return
      }
      setTranscript(question)

      // 2. Text → Answer
      const chatRes = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      })
      const chatData = await chatRes.json()
      const reply = chatData.answer
      setAnswer(reply)

      // 3. Answer → Speech
      const ttsRes = await fetch(`${API_URL}/voice/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: reply }),
      })
      const audioBlob = new Blob([await ttsRes.arrayBuffer()], { type: "audio/wav" })
      const audioUrl = URL.createObjectURL(audioBlob)

      setState("speaking")
      const audio = new Audio(audioUrl)
      audioElRef.current = audio
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl)
        setHistory((h) => [...h, { user: question, assistant: reply }])
        setTranscript("")
        setAnswer("")
        setState("idle")
      }
      audio.play().catch((err) => {
        setError("Playback error: " + err.message)
        setState("idle")
      })
    } catch (e) {
      setError("Something went wrong. Is the backend running?")
      setState("idle")
    }
  }

  const cfg = ORB_CONFIG[state]

  return (
    <div className="min-h-screen bg-[#060910] flex flex-col overflow-hidden relative">

      {/* Back link */}
      <div className="absolute top-6 left-6 z-10">
        <Link
          to="/"
          className="text-slate-500 hover:text-slate-300 text-sm flex items-center gap-2 transition"
        >
          ← Portfolio
        </Link>
      </div>

      {/* Title */}
      <div className="pt-16 text-center">
        <p className="text-slate-600 font-mono text-xs tracking-[0.3em] uppercase mb-1">AI Persona</p>
        <h1 className="text-white font-bold text-2xl tracking-wide">
          Chaima <span style={{ color: cfg.color }} className="transition-colors duration-700">AI</span>
        </h1>
      </div>

      {/* History */}
      <div className="flex-1 flex flex-col items-center justify-end pb-4 px-6 max-w-xl mx-auto w-full overflow-y-auto">
        {history.length === 0 && state === "idle" && (
          <p className="text-slate-700 text-sm text-center mb-8">
            Start a conversation — ask anything about Chaima's profile
          </p>
        )}
        <div className="w-full space-y-4 mb-4">
          {history.map((turn, i) => (
            <div key={i} className="space-y-2">
              <div className="flex justify-end">
                <div className="bg-slate-800 text-slate-300 text-sm rounded-2xl rounded-br-sm px-4 py-2 max-w-[80%]">
                  {turn.user}
                </div>
              </div>
              <div className="flex justify-start">
                <div className="text-slate-300 text-sm rounded-2xl rounded-bl-sm px-4 py-2 max-w-[80%] border border-slate-800 bg-slate-900">
                  {turn.assistant}
                </div>
              </div>
            </div>
          ))}
          <div ref={historyEndRef} />
        </div>

        {/* Live transcript */}
        {(transcript || answer) && (
          <div className="w-full text-center mb-4 space-y-2">
            {transcript && (
              <p className="text-slate-400 text-sm italic">"{transcript}"</p>
            )}
            {answer && state === "speaking" && (
              <p className="text-slate-300 text-sm max-w-md mx-auto leading-relaxed">{answer}</p>
            )}
          </div>
        )}

        {error && (
          <p className="text-red-400 text-sm text-center mb-4">{error}</p>
        )}
      </div>

      {/* Orb */}
      <div className="flex flex-col items-center pb-16 gap-6">
        <p
          className="text-sm font-mono tracking-widest transition-colors duration-500"
          style={{ color: cfg.color }}
        >
          {cfg.label}
        </p>

        <button
          onClick={handleOrbClick}
          disabled={state === "thinking" || state === "speaking"}
          className="relative focus:outline-none group"
          aria-label={state === "listening" ? "Stop recording" : "Start recording"}
        >
          {/* Concentric rings (listening only) */}
          {state === "listening" && (
            <>
              {[1, 2, 3].map((i) => (
                <span
                  key={i}
                  className="absolute inset-0 rounded-full"
                  style={{
                    border: `1px solid ${cfg.color}`,
                    animation: `ripple ${cfg.speed} ease-out ${i * 0.3}s infinite`,
                    opacity: 0,
                  }}
                />
              ))}
            </>
          )}

          {/* Rotating ring (thinking only) */}
          {state === "thinking" && (
            <span
              className="absolute -inset-3 rounded-full"
              style={{
                background: `conic-gradient(${cfg.color}, transparent, ${cfg.color})`,
                animation: "spin 1.5s linear infinite",
                mask: "radial-gradient(farthest-side, transparent calc(100% - 3px), white calc(100% - 3px))",
                WebkitMask: "radial-gradient(farthest-side, transparent calc(100% - 3px), white calc(100% - 3px))",
              }}
            />
          )}

          {/* Main orb */}
          <span
            className="block w-36 h-36 rounded-full transition-all duration-700"
            style={{
              background: `radial-gradient(circle at 35% 35%, ${cfg.color}cc, ${cfg.color}44)`,
              boxShadow: `0 0 60px 20px ${cfg.glow}, inset 0 0 40px rgba(255,255,255,0.05)`,
              animation: `breathe ${cfg.speed} ease-in-out infinite`,
            }}
          />

          {/* Icon overlay */}
          <span className="absolute inset-0 flex items-center justify-center text-3xl pointer-events-none">
            {state === "idle"     && "🎙️"}
            {state === "listening" && "⏹"}
            {state === "thinking" && "✦"}
            {state === "speaking" && "🔊"}
          </span>
        </button>

        <p className="text-slate-700 text-xs">
          {state === "idle" ? "tap · speak · release" : ""}
        </p>
      </div>

      <style>{`
        @keyframes breathe {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.07); }
        }
        @keyframes ripple {
          0%   { transform: scale(1); opacity: 0.6; }
          100% { transform: scale(2.5); opacity: 0; }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
