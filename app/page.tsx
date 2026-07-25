export default function HomeFallback() {
  return (
    <main
      style={{
        alignItems: "center",
        background:
          "radial-gradient(circle at 20% 10%, #dfe8ff 0, transparent 38%), #f7f8fc",
        color: "#16213a",
        display: "flex",
        fontFamily:
          '"Noto Sans JP", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif',
        justifyContent: "center",
        minHeight: "100vh",
        padding: "32px",
      }}
    >
      <section style={{ maxWidth: "680px" }}>
        <p
          style={{
            color: "#536de4",
            fontSize: "14px",
            fontWeight: 800,
            letterSpacing: "0.12em",
            margin: "0 0 12px",
          }}
        >
          AI相談 彦根
        </p>
        <h1
          style={{
            fontSize: "clamp(38px, 8vw, 72px)",
            letterSpacing: "-0.05em",
            lineHeight: 1.08,
            margin: 0,
          }}
        >
          AIを、仕事の仲間に。
        </h1>
        <p style={{ color: "#5f6d86", lineHeight: 1.9, margin: "24px 0 0" }}>
          サイトを準備しています。しばらくしてから、もう一度お試しください。
        </p>
      </section>
    </main>
  );
}
