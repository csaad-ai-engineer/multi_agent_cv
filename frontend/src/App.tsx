import { BrowserRouter, Routes, Route } from "react-router-dom"
import Portfolio from "./pages/Portfolio"
import Persona from "./pages/Persona"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Portfolio />} />
        <Route path="/persona" element={<Persona />} />
      </Routes>
    </BrowserRouter>
  )
}
