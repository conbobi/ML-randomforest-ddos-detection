// src/pages/Home.tsx
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: '700',
          background: 'linear-gradient(135deg, #5cc9f5, #2d7ff9)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '1rem'
        }}>
          IDS Security Dashboard
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          Real-time DDoS Detection & Mitigation Monitoring
        </p>
      </div>

      <div className="grid">
        {[
          { path: "/detection", title: "Detection State", icon: "🔍", color: "#5cc9f5" },
          { path: "/top-sources", title: "Top Sources", icon: "🌐", color: "#9f7aea" },
          { path: "/firewall", title: "Firewall Rules", icon: "🛡️", color: "#48bb78" },
          { path: "/system", title: "System Metrics", icon: "📊", color: "#ecc94b" },
          { path: "/logs", title: "Logs", icon: "📝", color: "#f56565" },
        ].map(item => (
          <Link 
            key={item.path} 
            to={item.path}
            style={{ textDecoration: 'none' }}
          >
            <div className="card" style={{ cursor: 'pointer', height: '100%' }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>{item.icon}</div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: '600', color: item.color }}>
                {item.title}
              </h3>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
