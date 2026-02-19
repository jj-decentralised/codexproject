"use client";

interface PullquoteProps {
  quote: string;
  attribution?: string;
}

export default function Pullquote({ quote, attribution }: PullquoteProps) {
  return (
    <blockquote className="my-12 py-6 border-t border-b" style={{ borderColor: "#E8E8E8" }}>
      <p
        className="text-2xl md:text-3xl leading-snug"
        style={{ fontFamily: "Georgia, serif", color: "#0A2240" }}
      >
        {quote}
      </p>
      {attribution && (
        <cite
          className="block mt-3 text-sm not-italic"
          style={{ color: "#999999" }}
        >
          {attribution}
        </cite>
      )}
    </blockquote>
  );
}
