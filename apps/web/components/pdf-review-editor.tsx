"use client";

import { PDFDocument, rgb, StandardFonts } from "pdf-lib";
import { useCallback, useEffect, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import { API_BASE_URL } from "@/lib/api-client";
import { Icon } from "@/components/icon";

pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();

type Point = { x: number; y: number };
type Stroke = { type: "pen" | "marker"; page: number; points: Point[] };
type TextNote = { type: "text"; page: number; x: number; y: number; text: string };
type Annotation = Stroke | TextNote;

type Props = {
  paperId: string;
  title: string;
  onSaved: () => void;
  onClose: () => void;
};

function normalisePoint(event: React.PointerEvent<HTMLCanvasElement>, canvas: HTMLCanvasElement): Point {
  const rect = canvas.getBoundingClientRect();
  return { x: Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)), y: Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)) };
}

export function PdfReviewEditor({ paperId, title, onSaved, onClose }: Props) {
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [pdfData, setPdfData] = useState<ArrayBuffer | null>(null);
  const [pages, setPages] = useState(0);
  const [page, setPage] = useState(1);
  const [tool, setTool] = useState<"pen" | "marker" | "text">("pen");
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [draft, setDraft] = useState<Point[]>([]);
  const [marks, setMarks] = useState("");
  const [feedback, setFeedback] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const pageFrameRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let objectUrl: string | null = null;

    const openSubmittedPdf = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/papers/${paperId}/download`, { credentials: "include", signal: controller.signal });
        if (!response.ok) throw new Error("The submitted PDF could not be opened.");
        const data = await response.arrayBuffer();

        // Do not hand an unverified response to the rendered PDF.js document.
        // Older demo records and mislabelled uploads can start with %PDF- while
        // still being plain text. Validate with PDF.js first so its
        // InvalidPDFException becomes an actionable editor message instead of
        // a runtime overlay.
        const bytes = new Uint8Array(data);
        const tail = new TextDecoder().decode(bytes.slice(Math.max(0, bytes.length - 2048)));
        if (new TextDecoder().decode(bytes.slice(0, 5)) !== "%PDF-" || !tail.includes("startxref") || !tail.includes("%%EOF")) {
          throw new Error("The submitted file is not a readable PDF. Ask the student to upload the original PDF again.");
        }
        const loadingTask = pdfjs.getDocument({ data: data.slice(0) });
        try {
          await loadingTask.promise;
        } catch {
          throw new Error("The submitted file is not a readable PDF. Ask the student to upload the original PDF again.");
        } finally {
          await loadingTask.destroy();
        }
        if (controller.signal.aborted) return;
        setPdfData(data);
        objectUrl = URL.createObjectURL(new Blob([data], { type: "application/pdf" }));
        setFileUrl(objectUrl);
      } catch (error) {
        if (controller.signal.aborted) return;
        setStatus(error instanceof Error ? error.message : "The submitted PDF could not be opened.");
      }
    };

    void openSubmittedPdf();
    return () => { controller.abort(); if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [paperId]);

  const drawOverlay = useCallback(() => {
    const canvas = canvasRef.current;
    const frame = pageFrameRef.current;
    if (!canvas || !frame) return;
    const rect = frame.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, rect.width, rect.height);
    const visible = annotations.filter((item) => item.page === page);
    for (const item of visible) {
      if (item.type === "text") {
        context.fillStyle = "#b42318";
        context.font = "700 16px Inter, sans-serif";
        context.fillText(item.text, item.x * rect.width, item.y * rect.height);
        continue;
      }
      if (item.points.length < 2) continue;
      context.strokeStyle = item.type === "marker" ? "rgba(245, 190, 40, .45)" : "#c0392b";
      context.lineWidth = (item.type === "marker" ? 14 : 3) * ratio;
      context.lineCap = "round";
      context.lineJoin = "round";
      context.beginPath();
      item.points.forEach((point, index) => index === 0 ? context.moveTo(point.x * rect.width, point.y * rect.height) : context.lineTo(point.x * rect.width, point.y * rect.height));
      context.stroke();
    }
    if (draft.length > 1) {
      context.strokeStyle = tool === "marker" ? "rgba(245, 190, 40, .45)" : "#c0392b";
      context.lineWidth = tool === "marker" ? 14 : 3;
      context.lineCap = "round";
      context.beginPath();
      draft.forEach((point, index) => index === 0 ? context.moveTo(point.x * rect.width, point.y * rect.height) : context.lineTo(point.x * rect.width, point.y * rect.height));
      context.stroke();
    }
  }, [annotations, draft, page, tool]);

  useEffect(() => { drawOverlay(); const observer = new ResizeObserver(drawOverlay); if (pageFrameRef.current) observer.observe(pageFrameRef.current); return () => observer.disconnect(); }, [drawOverlay]);

  const pointerDown = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.setPointerCapture(event.pointerId);
    const point = normalisePoint(event, canvas);
    if (tool === "text") {
      const text = window.prompt("Text to place on the paper:", "");
      if (text?.trim()) setAnnotations((current) => [...current, { type: "text", page, x: point.x, y: point.y, text: text.trim() }]);
      return;
    }
    setDraft([point]);
  };
  const pointerMove = (event: React.PointerEvent<HTMLCanvasElement>) => { if (!draft.length || !canvasRef.current) return; setDraft((current) => [...current, normalisePoint(event, canvasRef.current as HTMLCanvasElement)]); };
  const pointerUp = () => { if (draft.length > 1 && tool !== "text") setAnnotations((current) => [...current, { type: tool === "marker" ? "marker" : "pen", page, points: draft }]); setDraft([]); };

  const save = async () => {
    if (!pdfData) return;
    setSaving(true); setStatus(null);
    try {
      const document = await PDFDocument.load(pdfData);
      const font = await document.embedFont(StandardFonts.Helvetica);
      annotations.forEach((annotation) => {
        const pdfPage = document.getPage(annotation.page - 1);
        const size = pdfPage.getSize();
        if (annotation.type === "text") {
          pdfPage.drawText(annotation.text, { x: annotation.x * size.width, y: size.height - annotation.y * size.height, size: 12, font, color: rgb(.72, .08, .05) });
          return;
        }
        for (let index = 1; index < annotation.points.length; index += 1) {
          const from = annotation.points[index - 1]; const to = annotation.points[index];
          pdfPage.drawLine({ start: { x: from.x * size.width, y: size.height - from.y * size.height }, end: { x: to.x * size.width, y: size.height - to.y * size.height }, thickness: annotation.type === "marker" ? 12 : 2.5, color: annotation.type === "marker" ? rgb(1, .75, .05) : rgb(.72, .08, .05), opacity: annotation.type === "marker" ? .35 : .95 });
        }
      });
      const reviewedPdf = await document.save();
      const reviewedBuffer = reviewedPdf.buffer.slice(reviewedPdf.byteOffset, reviewedPdf.byteOffset + reviewedPdf.byteLength) as ArrayBuffer;
      const file = new File([reviewedBuffer], `reviewed-${title.replace(/\s+/g, "-")}.pdf`, { type: "application/pdf" });
      const annotatedBody = new FormData();
      annotatedBody.append("file", file);
      annotatedBody.append("marks", marks);
      annotatedBody.append("feedback", feedback);
      const annotatedResponse = await fetch(`${API_BASE_URL}/api/v1/papers/${paperId}/annotated`, { method: "POST", credentials: "include", body: annotatedBody });
      if (!annotatedResponse.ok) {
        const detail = await annotatedResponse.json().catch(() => ({}));
        throw new Error(typeof detail.detail === "string" ? detail.detail : "Could not save the reviewed PDF, marks and feedback.");
      }
      setStatus("Reviewed PDF, marks and feedback saved. The student has been notified.");
      onSaved();
    } catch (error) { setStatus(error instanceof Error ? error.message : "Could not save the review."); } finally { setSaving(false); }
  };

  return <section className="pdf-review-editor"><div className="pdf-review-header"><div><span className="section-kicker">Faculty review</span><h2>{title}</h2><p>Draw on the paper, highlight a point or place a text note. Save when marks and feedback are ready.</p></div><button className="icon-button" onClick={onClose} aria-label="Close PDF review"><Icon name="x" size={18} /></button></div><div className="pdf-review-toolbar"><button className={tool === "pen" ? "tool-active" : ""} onClick={() => setTool("pen")}><Icon name="pen" size={15} /> Pen</button><button className={tool === "marker" ? "tool-active" : ""} onClick={() => setTool("marker")}><Icon name="highlighter" size={15} /> Marker</button><button className={tool === "text" ? "tool-active" : ""} onClick={() => setTool("text")}><Icon name="type" size={15} /> Text</button><button onClick={() => setAnnotations((current) => current.slice(0, -1))}>Undo</button><span className="pdf-page-control"><button disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Previous</button><strong>{page} / {pages || "—"}</strong><button disabled={page >= pages} onClick={() => setPage((current) => current + 1)}>Next</button></span></div>{fileUrl ? <div className="pdf-page-shell"><Document file={fileUrl} onLoadSuccess={({ numPages }) => setPages(numPages)} onLoadError={(error) => setStatus(error.message)} loading={<div className="pdf-loading">Opening submitted PDF…</div>}><div className="pdf-page-frame" ref={pageFrameRef}><Page pageNumber={page} width={760} renderTextLayer={false} renderAnnotationLayer={false} onRenderSuccess={drawOverlay} /><canvas ref={canvasRef} className="pdf-annotation-canvas" onPointerDown={pointerDown} onPointerMove={pointerMove} onPointerUp={pointerUp} onPointerCancel={pointerUp} /></div></Document></div> : <div className="pdf-loading">{status ?? "Opening submitted PDF…"}</div>}<div className="pdf-review-footer"><label>Marks<input type="number" min="0" value={marks} onChange={(event) => setMarks(event.target.value)} placeholder="0" required /></label><label className="pdf-feedback-field">Suggestions and feedback<textarea value={feedback} onChange={(event) => setFeedback(event.target.value)} placeholder="Write clear, actionable feedback for the student." required /></label><button className="button button-primary" onClick={save} disabled={saving || !pdfData || !marks || !feedback}>{saving ? "Saving review…" : "Save review and notify student"}<Icon name="check" size={15} /></button></div>{status ? <div className="inline-notice"><Icon name="check" size={15} /> {status}</div> : null}</section>;
}
