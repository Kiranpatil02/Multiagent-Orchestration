import { useState, useEffect, useRef, useCallback } from "react";

function fmt(ts) {
  if (!ts) return "";
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

const STATUS_LABELS = { pending: "pending", in_progress: "running", finish: "done", complete: "done", failed: "failed" };

function Dot({ status }) {
  const s = (status || "pending").toLowerCase();
  const color = { pending: "bg-zinc-300", in_progress: "bg-amber-500", finish: "bg-green-500", complete: "bg-green-500", failed: "bg-red-500" }[s] || "bg-zinc-300";
  return <span className={`inline-block w-1.5 h-1.5 rounded-full shrink-0 ${color}`} />;
}

function StatusText({ status }) {
  const s = (status || "pending").toLowerCase();
  const color = { pending: "text-zinc-400", in_progress: "text-amber-500", finish: "text-green-600", complete: "text-green-600", failed: "text-red-500" }[s] || "text-zinc-400";
  return <span className={`text-[11px] ${color}`}>{STATUS_LABELS[s] || s}</span>;
}

function TaskStatus({ status }) {
  const s = (status || "pending").toLowerCase();
  const styles = {
    pending:     "text-zinc-300",
    in_progress: "text-amber-500",
    finish:      "text-green-500",
    complete:    "text-green-500",
    failed:      "text-red-400",
  };
  const labels = { pending: "·", in_progress: "›", finish: "✓", complete: "✓", failed: "✗" };
  return <span className={`text-[11px] shrink-0 ${styles[s] || "text-zinc-300"}`}>{labels[s] || "·"}</span>;
}

function ProgressBar({ pct }) {
  return (
    <div className="h-px w-full bg-zinc-200 mt-2">
      <div className="h-full bg-zinc-900 transition-all duration-700 ease-out" style={{ width: `${pct}%` }} />
    </div>
  );
}

function Section({ label, status, children }) {
  return (
    <div className="border-t border-zinc-100 pt-5 pb-5">
      <div className={`flex items-center gap-2.5 ${children ? "mb-3.5" : ""}`}>
        <Dot status={status} />
        <span className="text-[11px] tracking-widest uppercase text-zinc-400">{label}</span>
        <span className="ml-auto"><StatusText status={status} /></span>
      </div>
      {children}
    </div>
  );
}

function DataToggle({ data, label }) {
  const [open, setOpen] = useState(false);
  if (!data) return null;
  return (
    <div className="mt-2.5">
      <button onClick={() => setOpen(o => !o)} className="text-xs text-zinc-400 hover:text-zinc-600 transition-colors bg-transparent border-none cursor-pointer p-0 font-[inherit]">
        {open ? "− hide" : `+ ${label || "details"}`}
      </button>
      {open && (
        <pre className="mt-2 text-xs text-zinc-500 bg-zinc-50 border border-zinc-100 rounded p-3 overflow-auto max-h-48 whitespace-pre-wrap break-words font-[inherit]">
          {typeof data === "string" ? data : JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}

function parseInline(text) {
  const parts = [];
  const re = /(\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`)/g;
  let last = 0, m, key = 0;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(<span key={key++}>{text.slice(last, m.index)}</span>);
    if (m[2]) parts.push(<strong key={key++} className="font-semibold text-zinc-800">{m[2]}</strong>);
    else if (m[3]) parts.push(<em key={key++} className="italic">{m[3]}</em>);
    else if (m[4]) parts.push(<code key={key++} className="bg-zinc-100 text-zinc-700 rounded px-1 py-px text-[12px] font-mono">{m[4]}</code>);
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(<span key={key++}>{text.slice(last)}</span>);
  return parts.length ? parts : text;
}

function ReportContent({ content }) {
  if (!content) return null;
  const lines = content.split("\n");
  const elements = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { elements.push(<div key={i} className="h-3" />); i++; continue; }
    if (line.startsWith("# ")) {
      elements.push(<h1 key={i} className="text-xl font-bold text-zinc-900 mt-8 mb-3 pb-2 border-b border-zinc-100 tracking-tight">{parseInline(line.slice(2))}</h1>);
      i++; continue;
    }
    if (line.startsWith("## ")) {
      elements.push(<h2 key={i} className="text-base font-semibold text-zinc-800 mt-6 mb-2">{parseInline(line.slice(3))}</h2>);
      i++; continue;
    }
    if (line.startsWith("### ")) {
      elements.push(<h3 key={i} className="text-[13px] font-semibold text-zinc-600 mt-4 mb-1.5 uppercase tracking-wide">{parseInline(line.slice(4))}</h3>);
      i++; continue;
    }
    if (/^[-*]{3,}$/.test(line.trim())) { elements.push(<hr key={i} className="border-none border-t border-zinc-100 my-4" />); i++; continue; }
    if (line.startsWith("> ")) {
      elements.push(<blockquote key={i} className="border-l-2 border-zinc-200 pl-4 my-2 text-zinc-500 italic text-[13px] leading-7">{parseInline(line.slice(2))}</blockquote>);
      i++; continue;
    }
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) { items.push(lines[i].replace(/^\d+\.\s/, "")); i++; }
      elements.push(
        <ol key={`ol-${i}`} className="flex flex-col gap-1 my-2 pl-1">
          {items.map((item, idx) => (
            <li key={idx} className="flex gap-2.5 text-[13.5px] text-zinc-600 leading-7">
              <span className="text-zinc-300 shrink-0 min-w-[18px] text-right">{idx + 1}.</span>
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }
    if (line.startsWith("- ") || line.startsWith("* ")) {
      const items = [];
      while (i < lines.length && (lines[i].startsWith("- ") || lines[i].startsWith("* "))) { items.push(lines[i].slice(2)); i++; }
      elements.push(
        <ul key={`ul-${i}`} className="flex flex-col gap-1 my-2 pl-1">
          {items.map((item, idx) => (
            <li key={idx} className="flex gap-2.5 text-[13.5px] text-zinc-600 leading-7">
              <span className="text-zinc-300 shrink-0">–</span>
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }
    elements.push(<p key={i} className="text-[13.5px] leading-7 text-zinc-600 my-1">{parseInline(line)}</p>);
    i++;
  }
  return <div className="flex flex-col">{elements}</div>;
}

function TimelineEntry({ entry, isLast }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="flex gap-4 pb-5">
      <div className="flex flex-col items-center">
        <div className="w-1.5 h-1.5 rounded-full bg-zinc-200 shrink-0 mt-1.5" />
        {!isLast && <div className="w-px flex-1 bg-zinc-100 mt-1.5" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2.5 mb-1">
          <span className="text-sm text-zinc-700">{entry.agent}</span>
          {entry.revision != null && <span className="text-[11px] text-zinc-400">rev {entry.revision}</span>}
          {entry.timestamp && <span className="text-[11px] text-zinc-400 ml-auto">{fmt(entry.timestamp)}</span>}
        </div>
        <button onClick={() => setOpen(o => !o)} className="text-xs text-zinc-400 hover:text-zinc-600 transition-colors bg-transparent border-none cursor-pointer p-0 font-[inherit]">
          {open ? "− hide" : "+ output"}
        </button>
        {open && (
          <pre className="mt-2 text-xs text-zinc-500 bg-zinc-50 border border-zinc-100 rounded p-3 overflow-auto max-h-44 whitespace-pre-wrap break-words font-[inherit]">
            {JSON.stringify(entry.output, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [requestId, setRequestId] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [error, setError] = useState(null);
  const [tab, setTab] = useState("pipeline");
  const pollRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSubmit = async () => {
    if (!query.trim() || loading) return;
    setLoading(true); setError(null); setStatusData(null); setRequestId(null);
    try {
      const res = await fetch("http://localhost:8000/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request: query.trim() }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || "Failed"); }
      const data = await res.json();
      setRequestId(data.request_id);
    } catch (e) { setError(e.message); setLoading(false); }
  };

  const fetchStatus = useCallback(async (rid) => {
    try {
      const res = await fetch(`http://localhost:8000/api/tasks/${rid}/status`);
      if (!res.ok) throw new Error("Status fetch failed");
      const data = await res.json();
      setStatusData(data);
      if (data.is_complete) { clearInterval(pollRef.current); setLoading(false); }
    } catch (e) { setError(e.message); clearInterval(pollRef.current); setLoading(false); }
  }, []);

  useEffect(() => {
    if (!requestId) return;
    fetchStatus(requestId);
    pollRef.current = setInterval(() => fetchStatus(requestId), 2500);
    return () => clearInterval(pollRef.current);
  }, [requestId, fetchStatus]);

  const handleReset = () => {
    clearInterval(pollRef.current);
    setRequestId(null); setStatusData(null); setError(null);
    setLoading(false); setQuery(""); setTab("pipeline");
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  const pipeline = statusData?.pipeline;
  const progress = statusData?.progress;
  const currentAgent = statusData?.current_agent;
  const outputs = statusData?.all_outputs || [];
  const isDone = statusData?.is_complete;
  const writerContent =
    pipeline?.writer?.output?.content ||
    pipeline?.writer?.output?.report ||
    (typeof pipeline?.writer?.output === "string" ? pipeline?.writer?.output : null);

  return (
    <div className="min-h-screen bg-white text-zinc-900">
      <h2 className="text-center text-5xl py-14 italic">Your Agentic Researcher ✒️</h2>
      <main className="max-w-2xl mx-auto px-8 py-12">

        {!requestId && (
          <div className="flex flex-col gap-6">
            <p className="text-xl text-zinc-500 leading-relaxed">Enter a research topic or question to begin the pipeline.</p>
            <div className="border border-black rounded-md">
              <textarea
                ref={textareaRef}
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Enter topic here"
                rows={5}
                maxLength={5000}
                className="w-full bg-transparent text-zinc-900 placeholder-zinc-300 px-4 pt-3.5 pb-2 resize-none border-none leading-relaxed block font-[inherit]"
              />
              <div className="border-t border-black px-4 py-2.5 flex items-center justify-between">
                <button
                  onClick={handleSubmit}
                  disabled={!query.trim() || loading}
                  className={`px-4 py-1.5 rounded border-none cursor-pointer transition-colors font-[inherit] text-sm ${query.trim() && !loading ? "bg-zinc-900 text-white hover:bg-zinc-700" : "bg-zinc-100 text-zinc-400 cursor-not-allowed"}`}
                >
                  Run
                </button>
              </div>
            </div>
            {error && <p className="text-xs text-red-500">{error}</p>}
          </div>
        )}

        {requestId && (
          <div className="flex flex-col">
            <div className="pb-6">
              <p className="text-xl leading-relaxed mb-3">{statusData?.query || query}</p>
              {progress && (
                <>
                  <ProgressBar pct={progress.percentage} />
                  <div className="flex gap-5 mt-2 text-[11px] text-zinc-400">
                    <span>{progress.percentage}%</span>
                    <span>{progress.completed}/{progress.total_tasks} tasks</span>
                    {currentAgent && !isDone && <span className="text-amber-500">{currentAgent}</span>}
                    {isDone && <span className="text-green-600">complete</span>}
                  </div>
                </>
              )}
              {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
            </div>

            {pipeline && (
              <>
                <div className="flex">
                  {["pipeline", "timeline", "result"].map(t => (
                    <button
                      key={t}
                      onClick={() => setTab(t)}
                      className={`text-[11px] tracking-[0.12em] uppercase py-3 mr-7 bg-transparent border-none border-t-2 -mt-px cursor-pointer transition-colors font-[inherit] ${tab === t ? "text-zinc-900 border-t-zinc-900" : "text-zinc-400 border-t-transparent hover:text-zinc-600"}`}
                    >
                      {t}
                    </button>
                  ))}
                </div>

                {tab === "pipeline" && (
                  <div>
                    {/* Planner */}
                    <Section label="Planner" status={pipeline.planner?.status}>
                      {pipeline.planner?.output && (
                        <div>
                          {pipeline.planner.output.approach && (
                            <p className="text-xs text-zinc-500 leading-relaxed mb-2.5">{pipeline.planner.output.approach}</p>
                          )}
                          {pipeline.planner.output.research_queries && (
                            <ol className="flex flex-col gap-1 list-none p-0">
                              {pipeline.planner.output.research_queries.map((q, i) => (
                                <li key={i} className="flex gap-2.5 text-xs text-zinc-500">
                                  <span className="text-zinc-300 min-w-[16px]">{i + 1}.</span>
                                  <span>{q}</span>
                                </li>
                              ))}
                            </ol>
                          )}
                          <DataToggle data={pipeline.planner.output} label="full output" />
                        </div>
                      )}
                    </Section>

                    {/* Research — no Dot per task, use TaskStatus glyph instead */}
                    <Section label={`Research · ${pipeline.research?.completed_tasks || 0}/${pipeline.research?.total_tasks || 0}`} status={pipeline.research?.status}>
                      {pipeline.research?.tasks?.length > 0 && (
                        <div className="flex flex-col gap-2">
                          {pipeline.research.tasks.map((t, i) => (
                            <div key={t.id || i} className="flex items-start gap-2.5">
                              <TaskStatus status={t.status} />
                              <div className="flex flex-col gap-0.5 min-w-0">
                                {t.output?.query
                                  ? <span className="text-xs text-zinc-600 leading-relaxed">{t.output.query}</span>
                                  : <span className="text-xs text-zinc-400 italic">researching…</span>
                                }
                                {t.output?.summary && (
                                  <span className="text-[11px] text-zinc-400 leading-relaxed">{t.output.summary}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </Section>

                    {/* Writer — no nested Dot */}
                    <Section label={`Writer${pipeline.writer?.current_revision > 0 ? ` · rev ${pipeline.writer.current_revision}` : ""}`} status={pipeline.writer?.status}>
                      {writerContent && (
                        <div className="max-h-60 overflow-y-auto pr-1">
                          <ReportContent content={writerContent} />
                        </div>
                      )}
                    </Section>

                    {/* Reviewer */}
                    <Section label="Reviewer" status={pipeline.reviewer?.status}>
                      {pipeline.reviewer?.feedback && (
                        <div>
                          <p className={`text-xs text-zinc-600 leading-relaxed pl-3 border-l-2 ${pipeline.reviewer.approved ? "border-green-300" : "border-amber-300"}`}>
                            {pipeline.reviewer.feedback}
                          </p>
                          {pipeline.reviewer.revision_history?.length > 1 && (
                            <div className="mt-3 flex flex-col gap-1">
                              {pipeline.reviewer.revision_history.map((r, i) => (
                                <div key={i} className="flex gap-3 text-[11px] text-zinc-400">
                                  <span>r{r.revision}</span>
                                  <span className={r.approved ? "text-green-600" : "text-amber-500"}>{r.approved ? "approved" : "rejected"}</span>
                                  {r.timestamp && <span>{fmt(r.timestamp)}</span>}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </Section>
                  </div>
                )}

                {tab === "timeline" && (
                  <div className="pt-6">
                    {outputs.length === 0
                      ? <p className="text-xs text-zinc-400">No outputs yet.</p>
                      : (
                        <div className="flex flex-col">
                          {outputs.map((entry, i) => (
                            <TimelineEntry key={i} entry={entry} isLast={i === outputs.length - 1 && !(loading && !isDone)} />
                          ))}
                          {loading && !isDone && (
                            <div className="flex gap-4 items-center">
                              <div className="w-1.5 h-1.5 rounded-full border border-zinc-200" />
                              <span className="text-[11px] text-zinc-400">processing…</span>
                            </div>
                          )}
                        </div>
                      )}
                  </div>
                )}

                {tab === "result" && (
                  <div className="pt-6">
                    {writerContent ? (
                      <>
                        <div className="flex items-center justify-between mb-5 pb-4 border-b border-zinc-100">
                          <div className="flex items-center gap-3">
                            {isDone && (
                              <span className={`text-[11px] border rounded-full px-2.5 py-0.5 ${pipeline.reviewer?.approved ? "text-green-600 border-green-200" : "text-zinc-500 border-zinc-200"}`}>
                                {pipeline.reviewer?.approved ? "approved" : "complete"}
                              </span>
                            )}
                            {(pipeline.reviewer?.revision_history?.length || 0) > 0 && (
                              <span className="text-[11px] text-zinc-400">
                                {pipeline.reviewer.revision_history.length} revision{pipeline.reviewer.revision_history.length > 1 ? "s" : ""}
                              </span>
                            )}
                          </div>
                          <button
                            onClick={() => { const b = new Blob([writerContent], { type: "text/plain" }); const a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = "report.md"; a.click(); }}
                            className="text-[11px] text-zinc-500 hover:text-zinc-800 transition-colors border border-zinc-200 hover:border-zinc-400 rounded px-3 py-1 bg-transparent cursor-pointer font-[inherit]"
                          >
                            export .md
                          </button>
                        </div>
                        <ReportContent content={writerContent} />
                        {pipeline.reviewer?.feedback && (
                          <div className="mt-8 pt-5 border-t border-zinc-100">
                            <p className="text-[11px] text-zinc-400 uppercase tracking-widest mb-2">Reviewer note</p>
                            <p className={`text-xs text-zinc-500 leading-relaxed pl-3 border-l-2 ${pipeline.reviewer.approved ? "border-green-300" : "border-amber-300"}`}>
                              {pipeline.reviewer.feedback}
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <p className="text-xs text-zinc-400">Report not yet available.</p>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;