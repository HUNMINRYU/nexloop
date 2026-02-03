'use client';

import * as React from 'react';

const inputClasses = 'w-full rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-[var(--color-foreground)] placeholder:text-[var(--color-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-ring)] focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50';

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  function Input({ className = '', ...props }, ref) {
    return <input ref={ref} className={`${inputClasses} ${className}`.trim()} {...props} />;
  }
);

export default Input;
