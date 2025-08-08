"use client";

import { HTMLAttributes, forwardRef } from "react";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = "default", size = "md", className = "", children, style, ...props }, ref) => {
    const baseStyles = {
      display: "inline-flex",
      alignItems: "center",
      borderRadius: "9999px",
      fontWeight: "500",
      border: "1px solid transparent",
      whiteSpace: "nowrap" as const,
      transition: "all 0.2s ease-in-out",
    };

    const getSizeStyles = () => {
      switch (size) {
        case "sm":
          return {
            fontSize: "0.75rem",
            padding: "2px 8px",
            height: "20px",
          };
        case "lg":
          return {
            fontSize: "0.875rem",
            padding: "6px 12px",
            height: "32px",
          };
        case "md":
        default:
          return {
            fontSize: "0.75rem",
            padding: "4px 10px",
            height: "24px",
          };
      }
    };

    const getVariantStyles = () => {
      switch (variant) {
        case "secondary":
          return {
            backgroundColor: "#f1f5f9",
            color: "#475569",
            borderColor: "#e2e8f0",
          };
        case "destructive":
          return {
            backgroundColor: "#dc2626",
            color: "#ffffff",
            borderColor: "#dc2626",
          };
        case "success":
          return {
            backgroundColor: "#16a34a",
            color: "#ffffff",
            borderColor: "#16a34a",
          };
        case "warning":
          return {
            backgroundColor: "#d97706",
            color: "#ffffff",
            borderColor: "#d97706",
          };
        case "outline":
          return {
            backgroundColor: "transparent",
            color: "var(--color-foreground)",
            borderColor: "var(--color-border)",
          };
        case "default":
        default:
          return {
            backgroundColor: "var(--color-primary)",
            color: "var(--color-primary-foreground)",
            borderColor: "var(--color-primary)",
          };
      }
    };

    const combinedStyles = {
      ...baseStyles,
      ...getSizeStyles(),
      ...getVariantStyles(),
      ...style,
    };

    return (
      <span ref={ref} className={className} style={combinedStyles} {...props}>
        {children}
      </span>
    );
  },
);

Badge.displayName = "Badge";

export { Badge };