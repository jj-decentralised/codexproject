"use client";

import { colors } from "@/lib/theme";

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  number?: number;
}

export default function SectionHeader({ title, subtitle, number }: SectionHeaderProps) {
  return (
    <div className="mb-6">
      {number !== undefined && (
        <span
          className="text-xs uppercase tracking-widest"
          style={{ color: colors.mediumGray }}
        >
          Section {number}
        </span>
      )}
      <h2
        className="text-2xl mt-1"
        style={{ fontFamily: "Georgia, serif", color: colors.textBlack }}
      >
        {title}
      </h2>
      {subtitle && (
        <p className="text-sm mt-1" style={{ color: colors.mediumGray }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}
