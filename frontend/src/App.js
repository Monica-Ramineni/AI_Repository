import React, { useState, useRef, useEffect } from "react";

function App() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]); // {role: "user"|"agent", text, type, time}
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const time = new Date().toLocaleTimeString();
    setChat((prev) => [...prev, { role: "user", text: input, time }]);
    setLoading(true);
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      const data = await response.json();
      setChat((prev) => [
        ...prev,
        {
          role: "agent",
          text: data.data,
          type: data.type,
          time: new Date().toLocaleTimeString(),
        },
      ]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        {
          role: "agent",
          text: "Error: " + err.message,
          type: "error",
          time: new Date().toLocaleTimeString(),
        },
      ]);
    }
    setInput("");
    setLoading(false);
  };

  const handleClear = () => setChat([]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const renderAgentAnswer = (msg) => {
    if (msg.type === "tavily" && msg.text.results && msg.text.results.length > 0) {
      return (
        <div>
          <a
            href={msg.text.results[0].url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontWeight: "bold", color: "#4f8cff", textDecoration: "underline" }}
          >
            {msg.text.results[0].title}
          </a>
          <div style={{ marginTop: "0.5rem" }}>{msg.text.results[0].content}</div>
        </div>
      );
    }
    return (
      <span>
        {typeof msg.text === "object"
          ? JSON.stringify(msg.text, null, 2)
          : msg.text}
      </span>
    );
  };

  return (
    <div
      style={{
        maxWidth: 700,
        margin: "2rem auto",
        fontFamily: "Inter, sans-serif",
        display: "flex",
        flexDirection: "column",
        height: "90vh",
        background: "#f4f6fb",
        borderRadius: "18px",
        boxShadow: "0 4px 24px rgba(0,0,0,0.07)",
        padding: "1.5rem 1rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ textAlign: "center", color: "#2d3a4a", margin: 0 }}>Health Chat Agent</h2>
        <button
          onClick={handleClear}
          style={{
            background: "none",
            border: "none",
            color: "#4f8cff",
            cursor: "pointer",
            fontSize: "1rem",
            fontWeight: "bold",
            transition: "color 0.2s",
          }}
          onMouseOver={e => (e.target.style.color = "#2d3a4a")}
          onMouseOut={e => (e.target.style.color = "#4f8cff")}
        >
          Clear Chat
        </button>
      </div>
      <div
        style={{
          flex: 1,
          background: "#e9eef6",
          borderRadius: "12px",
          padding: "1rem",
          overflowY: "auto",
          margin: "1rem 0",
          boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
        }}
      >
        {chat.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              flexDirection: msg.role === "user" ? "row-reverse" : "row",
              alignItems: "flex-end",
              marginBottom: "1.2rem",
            }}
          >
            {/* Avatar */}
            <div style={{ margin: "0 0.5rem" }}>
              {msg.role === "user" ? (
                <span role="img" aria-label="user" style={{ fontSize: "1.5rem" }}>🧑</span>
              ) : (
                <span role="img" aria-label="agent" style={{ fontSize: "1.5rem" }}>🤖</span>
              )}
            </div>
            {/* Bubble */}
            <div
              style={{
                background: msg.role === "user" ? "#4f8cff" : "#fff",
                color: msg.role === "user" ? "#fff" : "#2d3a4a",
                padding: "0.9rem 1.3rem",
                borderRadius: "18px",
                maxWidth: "70%",
                wordBreak: "break-word",
                fontSize: "1.1rem",
                boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
                border: msg.role === "agent" ? "1px solid #dbeafe" : "none",
                marginLeft: msg.role === "user" ? "0" : "0.5rem",
                marginRight: msg.role === "user" ? "0.5rem" : "0",
              }}
            >
              <div>{msg.role === "agent" ? renderAgentAnswer(msg) : msg.text}</div>
              <div style={{ fontSize: "0.8rem", color: "#888", marginTop: "0.3rem", textAlign: "right" }}>
                {msg.time}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ textAlign: "left", margin: "0.5rem 0" }}>
            <span role="img" aria-label="agent" style={{ fontSize: "1.5rem" }}>🤖</span>
            <span style={{ marginLeft: "0.5rem", color: "#4f8cff" }}>
              <span className="spinner" style={{
                display: "inline-block",
                width: "18px",
                height: "18px",
                border: "3px solid #4f8cff",
                borderTop: "3px solid #e9eef6",
                borderRadius: "50%",
                animation: "spin 1s linear infinite",
                verticalAlign: "middle"
              }} />
              Typing...
            </span>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
          background: "#fff",
          borderRadius: "12px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
          padding: "0.75rem 1rem",
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          style={{
            width: "70%",
            padding: "0.75rem",
            fontSize: "1rem",
            borderRadius: "6px",
            border: "1.5px solid #4f8cff",
            outline: "none",
            marginRight: "0.5rem",
          }}
          disabled={loading}
        />
        <button
          type="submit"
          style={{
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            borderRadius: "6px",
            border: "none",
            background: "#4f8cff",
            color: "#fff",
            cursor: "pointer",
            transition: "background 0.2s",
          }}
          disabled={loading}
        >
          {loading ? (
            <span className="spinner" style={{
              display: "inline-block",
              width: "18px",
              height: "18px",
              border: "3px solid #fff",
              borderTop: "3px solid #4f8cff",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
              verticalAlign: "middle"
            }} />
          ) : (
            <span>&#9658;</span>
          )}
        </button>
      </form>
      {/* Spinner animation keyframes */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg);}
            100% { transform: rotate(360deg);}
          }
        `}
      </style>
    </div>
  );
}

export default App;