// src/App.tsx
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { api } from "./api/api";
import Home from "./pages/Home";
import DetectionState from "./pages/DetectionState";
import TopSources from "./pages/TopSources";
import FirewallRules from "./pages/FirewallRules";
import SystemMetrics from "./pages/SystemMetrics";
import Logs from "./pages/Logs";
import type { DetectionState as DetectionStateType } from "./types/api";
import "./App.css";

export default function App() {
  const [isAttack, setIsAttack] = useState(false);

  useEffect(() => {
    const checkAttack = () => {
      api.get("/detection/state")
        .then(res => setIsAttack(res.data.label === 1))
        .catch(() => {});
    };

    checkAttack();
    const interval = setInterval(checkAttack, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <BrowserRouter>
      <div className="app">
        <nav className="nav">
          <div className="nav-container">
            <NavLink to="/" className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''}`
            } end>
              <span className="nav-icon">🏠</span>
              <span>HOME</span>
            </NavLink>

            <NavLink to="/detection" className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''} ${isAttack ? 'alert' : ''}`
            }>
              <span className="nav-icon">🔍</span>
              <span>DETECTION</span>
              {isAttack && <span className="nav-badge">!</span>}
            </NavLink>

            <NavLink to="/top-sources" className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''}`
            }>
              <span className="nav-icon">🌐</span>
              <span>TOP SOURCES</span>
            </NavLink>

            <NavLink to="/firewall" className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''}`
            }>
              <span className="nav-icon">🛡️</span>
              <span>FIREWALL</span>
            </NavLink>

            <NavLink to="/system" className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''}`
            }>
              <span className="nav-icon">📊</span>
              <span>SYSTEM</span>
            </NavLink>

            <NavLink to="/logs" className={({ isActive }) => 
              `nav-link ${isActive ? 'active' : ''}`
            }>
              <span className="nav-icon">📝</span>
              <span>LOGS</span>
            </NavLink>
          </div>
        </nav>

        <main className="main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/detection" element={<DetectionState />} />
            <Route path="/top-sources" element={<TopSources />} />
            <Route path="/firewall" element={<FirewallRules />} />
            <Route path="/system" element={<SystemMetrics />} />
            <Route path="/logs" element={<Logs />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
