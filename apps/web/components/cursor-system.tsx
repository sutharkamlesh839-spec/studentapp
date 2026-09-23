"use client";

import { useEffect, useRef, useState } from "react";

export function CursorSystem() {
  const dotRef = useRef<HTMLSpanElement>(null);
  const ringRef = useRef<HTMLSpanElement>(null);
  const [label, setLabel] = useState("");

  useEffect(() => {
    const finePointer = window.matchMedia("(pointer: fine)");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (!finePointer.matches || reducedMotion.matches) return undefined;

    document.body.classList.add("custom-cursor-active");
    let targetX = -100;
    let targetY = -100;
    let ringX = targetX;
    let ringY = targetY;
    let frame = 0;

    const move = (event: PointerEvent) => {
      targetX = event.clientX;
      targetY = event.clientY;
      const target = (event.target as HTMLElement | null)?.closest<HTMLElement>("[data-cursor-label]");
      setLabel(target?.dataset.cursorLabel ?? "");
    };
    const leave = () => setLabel("");
    const animate = () => {
      ringX += (targetX - ringX) * 0.16;
      ringY += (targetY - ringY) * 0.16;
      if (dotRef.current) dotRef.current.style.transform = `translate3d(${targetX}px, ${targetY}px, 0)`;
      if (ringRef.current) ringRef.current.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;
      frame = requestAnimationFrame(animate);
    };
    window.addEventListener("pointermove", move, { passive: true });
    window.addEventListener("pointerleave", leave);
    frame = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerleave", leave);
      document.body.classList.remove("custom-cursor-active");
    };
  }, []);

  return <><span ref={dotRef} className="cursor-dot" aria-hidden="true" /><span ref={ringRef} className={`cursor-ring ${label ? "cursor-ring-labelled" : ""}`} aria-hidden="true"><span>{label}</span></span></>;
}
