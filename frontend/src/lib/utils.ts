import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges tailwind classes using clsx and tailwind-merge.
 * This prevents class conflicts (e.g., matching padding-4 and padding-8).
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
