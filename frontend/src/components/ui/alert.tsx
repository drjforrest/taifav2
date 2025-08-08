"use client";

import { HTMLAttributes, forwardRef } from "react";

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "destructive" | "warning" | "info";
  children: React.ReactNode;
}

const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ variant = "default", className = "", children, style, ...props }, ref) => {
    const baseStyles = {
      borderRadius: "var(--radius-md)",
      padding: "var(--spacing-md)",
      border: "1px solid",
      display: "flex",
      alignItems: "flex-start",
      gap: "var(--spacing-sm)",
      fontSize: "0.875rem",
      lineHeight: "1.5",
    };

    const getVariantStyles = () => {
      switch (variant) {
        case "destructive":
          return {
            backgroundColor: "#fef2f2",
            borderColor: "#fecaca",
            color: "#dc2626",
          };
        case "warning":
          return {
            backgroundColor: "#fffbeb",
            borderColor: "#fed7aa",
            color: "#d97706",
          };
        case "info":
          return {
            backgroundColor: "#eff6ff",
            borderColor: "#bfdbfe",
            color: "#2563eb",
          };
        case "default":
        default:
          return {
            backgroundColor: "var(--color-muted)",
            borderColor: "var(--color-border)",
            color: "var(--color-foreground)",
          };
      }
    };

    const combinedStyles = {
      ...baseStyles,
      ...getVariantStyles(),
      ...style,
    };

    return (
      <div ref={ref} className={className} style={combinedStyles} {...props}>
        {children}
      </div>
    );
  },
);

Alert.displayName = "Alert";

interface AlertDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

const AlertDescription = forwardRef<HTMLParagraphElement, AlertDescriptionProps>(
  ({ className = "", children, style, ...props }, ref) => {
    const descriptionStyles = {
      margin: 0,
      fontSize: "inherit",
      lineHeight: "inherit",
      color: "inherit",
      ...style,
    };

    return (
      <p ref={ref} className={className} style={descriptionStyles} {...props}>
        {children}
      </p>
    );
  },
);

AlertDescription.displayName = "AlertDescription";

interface AlertTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

const AlertTitle = forwardRef<HTMLHeadingElement, AlertTitleProps>(
  ({ className = "", children, style, ...props }, ref) => {
    const titleStyles = {
      fontSize: "1rem",
      fontWeight: "600",
      marginBottom: "var(--spacing-xs)",
      color: "inherit",
      ...style,
    };

    return (
      <h5 ref={ref} className={className} style={titleStyles} {...props}>
        {children}
      </h5>
    );
  },
);

AlertTitle.displayName = "AlertTitle";

export { Alert, AlertDescription, AlertTitle };