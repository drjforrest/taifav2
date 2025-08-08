'use client';

import { ButtonHTMLAttributes, forwardRef } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className = '', children, style, onMouseEnter, onMouseLeave, disabled, ...props }, ref) => {
    const baseStyles = {
      fontWeight: '600',
      borderRadius: 'var(--radius-md)',
      transition: 'all 0.2s ease-in-out',
      cursor: disabled ? 'not-allowed' : 'pointer',
      border: 'none',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 'var(--spacing-sm)',
      opacity: disabled ? 0.5 : 1,
      outline: 'none',
    };

    const sizeStyles = {
      sm: {
        padding: 'var(--spacing-sm) var(--spacing-md)',
        fontSize: '0.875rem',
        height: '2rem',
      },
      md: {
        padding: 'var(--spacing-md) var(--spacing-lg)',
        fontSize: '1rem',
        height: '2.5rem',
      },
      lg: {
        padding: 'var(--spacing-lg) var(--spacing-xl)',
        fontSize: '1.125rem',
        height: '3rem',
      },
    };

    const getVariantStyles = (isHover = false) => {
      switch (variant) {
        case 'primary':
          return {
            backgroundColor: isHover ? '#2563eb' : '#3b82f6',
            color: 'white',
          };
        case 'secondary':
          return {
            backgroundColor: isHover ? '#e2e8f0' : '#f1f5f9',
            color: '#475569',
          };
        case 'outline':
          return {
            backgroundColor: isHover ? '#f8fafc' : 'transparent',
            color: '#374151',
            border: '1px solid #d1d5db',
          };
        case 'ghost':
          return {
            backgroundColor: isHover ? '#f8fafc' : 'transparent',
            color: '#374151',
          };
        case 'destructive':
          return {
            backgroundColor: isHover ? '#dc2626' : '#ef4444',
            color: 'white',
          };
        default:
          return {};
      }
    };

    const handleMouseEnter = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled) {
        const hoverStyles = getVariantStyles(true);
        Object.assign(e.currentTarget.style, hoverStyles);
        onMouseEnter?.(e);
      }
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (!disabled) {
        const normalStyles = getVariantStyles(false);
        Object.assign(e.currentTarget.style, normalStyles);
        onMouseLeave?.(e);
      }
    };

    const combinedStyles = {
      ...baseStyles,
      ...sizeStyles[size],
      ...getVariantStyles(false),
      ...style,
    };

    return (
      <button
        ref={ref}
        className={className}
        style={combinedStyles}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        disabled={disabled}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;