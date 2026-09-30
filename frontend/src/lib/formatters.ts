export function formatDisplayLabel(value: string | null | undefined): string {
  if (!value || typeof value !== 'string') return "";

  // Replace underscores with spaces
  const withSpaces = value.replace(/_/g, ' ');

  // Convert to Title Case (capitalize first letter of each word, lowercase the rest)
  return withSpaces
    .split(/\s+/)
    .filter(Boolean)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}
