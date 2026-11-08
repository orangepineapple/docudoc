export function cx(...c: (string | false | null | undefined)[]) {
  return c.filter(Boolean).join(' ')
}

export const btn = {
  primary:
    'inline-flex items-center gap-2 rounded-md bg-accent px-3.5 py-2 text-sm font-medium text-accent-text hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed',
  ghost:
    'inline-flex items-center gap-1.5 rounded-md border border-line bg-panel px-3 py-1.5 text-sm text-ink hover:bg-sunken disabled:opacity-50',
  link: 'text-xs text-accent hover:underline',
}

export const input =
  'w-full rounded-md border border-line bg-panel px-2.5 py-1.5 text-sm text-ink placeholder:text-faint focus:outline-2 focus:outline-accent'
